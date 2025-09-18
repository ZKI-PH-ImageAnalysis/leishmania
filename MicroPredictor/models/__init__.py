import os
from ruamel.yaml import YAML
from ultralytics import YOLO


def _load_config():
    """Load configuration from MicroPredictor/config/config.yml"""
    yaml = YAML()
    yaml.preserve_quotes = True
    main_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(main_path, "config", "config.yml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.load(f)


def activate_leishmania(self, config):
    """Load the Leishmania YOLO model for predictions using config path."""
    self.leishmania_model = YOLO(config["yolo_weights"])


def update_frame_leishmania(self, frame):
    """Update the frame with Leishmania predictions and return plotted frame."""
    results = self.leishmania_model.predict(frame, verbose=False)
    frame = results[0].plot()
    return frame


def analyze_leishmania(self, file_path, isimage, save_path):
    """Run Leishmania analysis on image or video and save results to save_path."""
    # Resolve weights path from config; fallback to default relative path
    try:
        config = _load_config()
        weights_path = config.get("yolo_weights")
    except Exception:
        main_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        weights_path = os.path.join(main_path, "weights", "best.pt")

    self.leishmania_model = YOLO(weights_path)

    if isimage:
        results = self.leishmania_model.predict([file_path], verbose=False)
        out_path = os.path.join(save_path, os.path.basename(file_path))
        results[0].save(filename=out_path)
    else:
        results = self.leishmania_model(
            file_path,
            stream=True,
            save=True,
            verbose=False,
            project=f"{save_path}",
            name="result",
        )
        for _ in results:
            pass

