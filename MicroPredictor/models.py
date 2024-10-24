import os
import sys
import time

import cv2
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.backends.cudnn as cudnn
import yaml
from PIL import Image
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QIcon, QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)
from ultralytics import YOLO

import prediction
from data import cfg, set_cfg
from yolact import Yolact


def activate_blood_cell_count(self, config):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    cudnn.fastest = True
    torch.set_default_tensor_type("torch.cuda.FloatTensor")

    set_cfg(config["yolact_config"])
    cfg.eval_mask_branch = False

    self.net = Yolact()
    self.net.to(device)
    self.net.load_weights(config["yolact_weights"])
    self.net.eval()
    self.net = self.net.cuda()

    self.RBC_output_label = QLabel()
    self.RBC_output_label.setAlignment(Qt.AlignLeft)
    self.output_vbox.addWidget(self.RBC_output_label)
    self.RBC_output_label.setText(f"RBC:")

    self.RBC_color_hbox = QHBoxLayout()
    self.output_vbox.addLayout(self.RBC_color_hbox)
    self.RBC_color_label = QLabel()
    self.RBC_color_label.setAlignment(Qt.AlignLeft)
    self.RBC_color_label.setFixedSize(40, 10)
    self.RBC_color_label.setStyleSheet("background-color: rgb(255, 0, 0);")
    self.RBC_color = (0, 0, 255)
    self.RBC_color_hbox.addWidget(self.RBC_color_label)

    self.RBC_change_color_button = QPushButton("Change Color")
    self.RBC_change_color_button.setMaximumWidth(100)
    self.RBC_change_color_button.clicked.connect(lambda: change_color("RBC"))
    self.RBC_color_hbox.addWidget(self.RBC_change_color_button)

    self.RBC_color_hbox.addStretch()

    self.WBC_output_label = QLabel()
    self.WBC_output_label.setAlignment(Qt.AlignLeft)
    self.output_vbox.addWidget(self.WBC_output_label)
    self.WBC_output_label.setText(f"WBC:")

    self.WBC_color_hbox = QHBoxLayout()
    self.output_vbox.addLayout(self.WBC_color_hbox)
    self.WBC_color_label = QLabel()
    self.WBC_color_label.setAlignment(Qt.AlignLeft)
    self.WBC_color_label.setFixedSize(40, 10)
    self.WBC_color_label.setStyleSheet("background-color: rgb(0, 0, 255);")
    self.WBC_color = (255, 0, 0)
    self.WBC_color_hbox.addWidget(self.WBC_color_label)

    self.change_color_button = QPushButton("Change Color")
    self.change_color_button.setMaximumWidth(100)
    self.change_color_button.clicked.connect(lambda: change_color("WBC"))
    self.WBC_color_hbox.addWidget(self.change_color_button)

    self.WBC_color_hbox.addStretch()

    self.PLT_output_label = QLabel()
    self.PLT_output_label.setAlignment(Qt.AlignLeft)
    self.output_vbox.addWidget(self.PLT_output_label)
    self.PLT_output_label.setText(f"PLT:")

    self.PLT_color_hbox = QHBoxLayout()
    self.output_vbox.addLayout(self.PLT_color_hbox)
    self.PLT_color_label = QLabel()
    self.PLT_color_label.setAlignment(Qt.AlignLeft)
    self.PLT_color_label.setFixedSize(40, 10)
    self.PLT_color_label.setStyleSheet("background-color: rgb(0, 255, 0);")
    self.PLT_color = (0, 255, 0)
    self.PLT_color_hbox.addWidget(self.PLT_color_label)

    self.change_color_button = QPushButton("Change Color")
    self.change_color_button.setMaximumWidth(100)
    self.change_color_button.clicked.connect(lambda: change_color("PLT"))
    self.PLT_color_hbox.addWidget(self.change_color_button)

    self.PLT_color_hbox.addStretch()

    def change_color(bloodpart):
        color = QColorDialog.getColor()
        if color.isValid():
            r, g, b, _ = QColor(color.rgb()).getRgb()
            if bloodpart == "RBC":
                self.RBC_color_label.setStyleSheet(
                    f"background-color: rgb({r}, {g}, {b});"
                )
                self.RBC_color = (b, g, r)
            elif bloodpart == "WBC":
                self.WBC_color_label.setStyleSheet(
                    f"background-color: rgb({r}, {g}, {b});"
                )
            elif bloodpart == "PLT":
                self.PLT_color_label.setStyleSheet(
                    f"background-color: rgb({r}, {g}, {b});"
                )
                self.PLT_color = (b, g, r)


def update_frame_blood_cell_count(self):
    self.frame, RBC, WBC, PLT = prediction.evaluate(
        self.net, self.frame, self.RBC_color, self.WBC_color, self.PLT_color
    )
    self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
    h, w, ch = self.frame.shape
    bytes_per_line = ch * w
    qt_img = QImage(self.frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
    self.video_label.setPixmap(QPixmap.fromImage(qt_img))
    self.RBC_output_label.setText(f"RBC: {RBC}")
    self.WBC_output_label.setText(f"WBC: {WBC}")
    self.PLT_output_label.setText(f"PLT: {PLT}")


def activate_leishmania(self, config):
    self.leishmania_model = YOLO(
        config[
            "yolo_weights"
        ]  # "D:\\Leischmanien\\MicroPredictor-main\\MicroPredictor\\weights\\best.pt"
    )


def update_frame_leishmania(self):
    results = self.leishmania_model.predict(self.frame, verbose=False)
    self.frame = results[0].plot()
    self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
    h, w, ch = self.frame.shape
    bytes_per_line = ch * w
    qt_img = QImage(self.frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
    self.video_label.setPixmap(QPixmap.fromImage(qt_img))


def analyze_leishmania(self, path, isimage):
    self.leishmania_model = YOLO(
        "D:\\Leischmanien\\MicroPredictor-main\\MicroPredictor\\weights\\best.pt"
    )
    if isimage:
        results = self.leishmania_model.predict([path], verbose=False)
        results[0].save(filename=f"{self.save_path}/{os.path.basename(path)}")
    else:
        results = self.leishmania_model(
            path,
            stream=True,
            save=True,
            verbose=False,
            project=f"{self.save_path}",
            name="result",
        )
        for result in results:
            pass
