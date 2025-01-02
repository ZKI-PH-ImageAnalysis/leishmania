from collections import defaultdict

import cv2
import pycocotools
import torch

from data import COLORS, cfg, set_cfg
from layers.output_utils import postprocess
from utils.augmentations import FastBaseTransform
from yolact import Yolact

color_cache = defaultdict(lambda: {})


def prep_display(
    dets_out,
    img,
    RBC_color,
    WBC_color,
    PLT_color,
    h,
    w,
    undo_transform=True,
    class_color=True,
    mask_alpha=0.45,
):
    """
    Note: If undo_transform=False then im_h and im_w are allowed to be None.
    """
    # set_cfg("yolact_resnet101_blood_config")
    cfg.eval_mask_branch = True

    img_gpu = img / 255.0
    h, w, _ = img.shape

    save = cfg.rescore_bbox
    cfg.rescore_bbox = True
    t = postprocess(
        dets_out,
        w,
        h,
        visualize_lincomb=False,
        crop_masks=True,
        score_threshold=0.5,
    )
    cfg.rescore_bbox = save

    idx = t[1].argsort(0, descending=True)[:300]

    if cfg.eval_mask_branch:
        # Masks are drawn on the GPU, so don't copy
        masks = t[3][idx]

    classes, scores, boxes = [x[idx].detach().cpu().numpy() for x in t[:3]]

    RBC = 0
    WBC = 0
    PLT = 0

    for i in classes:
        if i == 0:
            RBC += 1
        if i == 1:
            WBC += 1
        if i == 2:
            PLT += 1

    num_dets_to_consider = min(300, classes.shape[0])
    for j in range(num_dets_to_consider):
        if scores[j] < 0.5:
            num_dets_to_consider = j
            break

    # Quick and dirty lambda for selecting the color for a particular index
    # Also keeps track of a per-gpu color cache for maximum speed
    def get_color(j, on_gpu=None):
        global color_cache
        color_idx = (classes[j] * 5 if class_color else j * 5) % len(COLORS)

        if on_gpu is not None and color_idx in color_cache[on_gpu]:
            return color_cache[on_gpu][color_idx]
        else:
            color = COLORS[color_idx]
            if not undo_transform:
                # The image might come in as RGB or BRG, depending
                color = (color[2], color[1], color[0])
            if on_gpu is not None:
                color = torch.Tensor(color).to(on_gpu).float() / 255.0
                color_cache[on_gpu][color_idx] = color
            return color

    # First, draw the masks on the GPU where we can do it really fast
    # Beware: very fast but possibly unintelligible mask-drawing code ahead
    # I wish I had access to OpenGL or Vulkan but alas, I guess Pytorch tensor operations will have to suffice
    if True and cfg.eval_mask_branch and num_dets_to_consider > 0:
        # After this, mask is of size [num_dets, h, w, 1]
        masks = masks[:num_dets_to_consider, :, :, None]

        # Prepare the RGB images for each mask given their color (size [num_dets, h, w, 1])
        colors = torch.cat(
            [
                get_color(j, on_gpu=img_gpu.device.index).view(1, 1, 1, 3)
                for j in range(num_dets_to_consider)
            ],
            dim=0,
        )
        masks_color = masks.repeat(1, 1, 1, 3) * colors * mask_alpha

        # I did the math for this on pen and paper. This whole block should be equivalent to:
        #    for j in range(num_dets_to_consider):
        #        img_gpu = img_gpu * inv_alph_masks[j] + masks_color[j]
        img_result = (img_gpu * 255).byte().cpu().numpy()

        for j in range(num_dets_to_consider):
            img_mask = img_gpu * 0 * masks[j] + masks_color[j]
            img_contours = (img_mask * 255).byte().cpu().numpy()

            imgray = cv2.cvtColor(img_contours, cv2.COLOR_BGR2GRAY)
            ret, thresh = cv2.threshold(imgray, 0, 255, cv2.THRESH_BINARY)
            contours, hierarchy = cv2.findContours(
                thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
            )

            for c in range(len(contours)):
                # RBC
                if classes[j] == 0:
                    cv2.drawContours(img_result, contours[c], -1, RBC_color, 2)
                # WBC
                if classes[j] == 1:
                    cv2.drawContours(img_result, contours[c], -1, WBC_color, 2)
                # PLT
                if classes[j] == 2:
                    cv2.drawContours(img_result, contours[c], -1, PLT_color, 2)

        # masks_color_summand = masks_color[0]
        # if num_dets_to_consider > 1:
        # inv_alph_cumul = inv_alph_masks[:(num_dets_to_consider-1)].cumprod(dim=0)
        # masks_color_cumul = masks_color[1:] * inv_alph_cumul
        # masks_color_summand += masks_color_cumul.sum(dim=0)

        # img_gpu = img_gpu * inv_alph_masks.prod(dim=0) + masks_color_summand

    # Then draw the stuff that needs to be done on the cpu
    # Note, make sure this is a uint8 tensor or opencv will not anti alias text for whatever reason
    img_numpy = (img_gpu * 255).byte().cpu().numpy()

    if num_dets_to_consider == 0:
        return img_numpy, RBC, WBC, PLT

    for j in reversed(range(num_dets_to_consider)):
        x1, y1, x2, y2 = boxes[j, :]
        color = get_color(j)
        score = scores[j]

        cv2.rectangle(img_numpy, (x1, y1), (x2, y2), color, 1)

        _class = cfg.dataset.class_names[classes[j]]
        text_str = "%s %.2f" % (_class, score) if True else _class

        font_face = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 0.4
        font_thickness = 1

        text_pt = (x1 - 8, y1 + 8)
        text_color = [255, 255, 255]

        # cv2.rectangle(img_numpy, (x1, y1), (x1 + text_w, y1 - text_h - 4), color, -1)
        cv2.putText(
            img_result,
            text_str,
            text_pt,
            font_face,
            font_scale,
            text_color,
            font_thickness,
            cv2.LINE_AA,
        )

    return img_result, RBC, WBC, PLT


def evalimage(net: Yolact, path: str, RBC_color, WBC_color, PLT_color):
    frame = torch.from_numpy(path).cuda().float()
    batch = FastBaseTransform()(frame.unsqueeze(0))
    preds = net(batch)
    return prep_display(
        preds, frame, RBC_color, WBC_color, PLT_color, None, None, undo_transform=False
    )


def evaluate(net: Yolact, path: str, RBC_color, WBC_color, PLT_color):
    set_cfg("yolact_resnet101_blood_config")
    net.detect.use_fast_nms = True
    net.detect.use_cross_class_nms = False
    cfg.mask_proto_debug = False
    return evalimage(net, path, RBC_color, WBC_color, PLT_color)
