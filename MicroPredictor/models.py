import os

import torch
import torch.backends.cudnn as cudnn
from PIL import Image
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QColorDialog, QHBoxLayout, QLabel, QPushButton
from ruamel.yaml import YAML
from ultralytics import YOLO

import prediction
from data import cfg, set_cfg
from yolact import Yolact


class YolactWorker(QThread):
    """
    A QThread subclass to handle the initialization of the Yolact model in a separate thread.

    Emits signals to notify the main thread when the model is initialized or an error occurs.
    """

    # Signal to send the initialized model to the main thread
    model_initialized = pyqtSignal(object)

    # Signal to send error messages to the main thread
    error_occurred = pyqtSignal(str)

    def __init__(self, config):
        """
        Initialize the YolactWorker.

        Parameters:
            config (dict): Configuration dictionary for Yolact.
        """
        super().__init__()
        self.config = config
        self.net = None  # The initialized model will be stored here

    def run(self):
        """
        Initialize the Yolact model and prepare it for evaluation.

        Sends the initialized model to the main thread or an error signal if something fails.
        """
        try:
            # Configure the device (CUDA or CPU)
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

            # Configure CUDA for maximum performance
            cudnn.fastest = True
            torch.set_default_tensor_type("torch.cuda.FloatTensor")

            # Set the Yolact configuration
            set_cfg(self.config["yolact_config"])
            cfg.eval_mask_branch = False  # Disable mask branch for performance

            # Load and initialize the Yolact model
            self.net = Yolact()
            self.net.to(device)
            self.net.load_weights(self.config["yolact_weights"])
            self.net.eval()  # Set the model to evaluation mode

            # Move the model to GPU if available
            if torch.cuda.is_available():
                self.net = self.net.cuda()

            # Synchronize CUDA to ensure all operations are complete
            torch.cuda.synchronize()

            # Emit the signal that the model is initialized
            self.model_initialized.emit(self.net)

        except Exception as e:
            # Emit the error signal with the exception message
            self.error_occurred.emit(str(e))


def activate_blood_cell_output(self):
    """
    Create UI elements for displaying and configuring blood cell analysis results.

    Adds labels, color selectors, and buttons for RBC, WBC, and PLT outputs.
    """
    # RBC (Red Blood Cells) Output
    self.RBC_output_label = QLabel("RBC:")
    self.RBC_output_label.setAlignment(Qt.AlignLeft)
    self.output_vbox.addWidget(self.RBC_output_label)

    self.RBC_color_hbox = QHBoxLayout()
    self.output_vbox.addLayout(self.RBC_color_hbox)

    self.RBC_color_label = QLabel()
    self.RBC_color_label.setFixedSize(40, 10)
    self.RBC_color_label.setStyleSheet("background-color: rgb(255, 0, 0);")  # Red
    self.RBC_color_hbox.addWidget(self.RBC_color_label)

    self.RBC_change_color_button = QPushButton("Change Color")
    self.RBC_change_color_button.setMaximumWidth(100)
    self.RBC_change_color_button.clicked.connect(lambda: change_color("RBC"))
    self.RBC_color_hbox.addWidget(self.RBC_change_color_button)
    self.RBC_color_hbox.addStretch()

    # WBC (White Blood Cells) Output
    self.WBC_output_label = QLabel("WBC:")
    self.WBC_output_label.setAlignment(Qt.AlignLeft)
    self.output_vbox.addWidget(self.WBC_output_label)

    self.WBC_color_hbox = QHBoxLayout()
    self.output_vbox.addLayout(self.WBC_color_hbox)

    self.WBC_color_label = QLabel()
    self.WBC_color_label.setFixedSize(40, 10)
    self.WBC_color_label.setStyleSheet("background-color: rgb(0, 0, 255);")  # Blue
    self.WBC_color_hbox.addWidget(self.WBC_color_label)

    self.change_color_button = QPushButton("Change Color")
    self.change_color_button.setMaximumWidth(100)
    self.change_color_button.clicked.connect(lambda: change_color("WBC"))
    self.WBC_color_hbox.addWidget(self.change_color_button)
    self.WBC_color_hbox.addStretch()

    # PLT (Platelets) Output
    self.PLT_output_label = QLabel("PLT:")
    self.PLT_output_label.setAlignment(Qt.AlignLeft)
    self.output_vbox.addWidget(self.PLT_output_label)

    self.PLT_color_hbox = QHBoxLayout()
    self.output_vbox.addLayout(self.PLT_color_hbox)

    self.PLT_color_label = QLabel()
    self.PLT_color_label.setFixedSize(40, 10)
    self.PLT_color_label.setStyleSheet("background-color: rgb(0, 255, 0);")  # Green
    self.PLT_color_hbox.addWidget(self.PLT_color_label)

    self.change_color_button = QPushButton("Change Color")
    self.change_color_button.setMaximumWidth(100)
    self.change_color_button.clicked.connect(lambda: change_color("PLT"))
    self.PLT_color_hbox.addWidget(self.change_color_button)
    self.PLT_color_hbox.addStretch()

    def change_color(bloodpart):
        """
        Open a color dialog to change the color for a specific blood cell type.

        Parameters:
            bloodpart (str): The type of blood cell ("RBC", "WBC", "PLT").
        """
        color = QColorDialog.getColor()
        if color.isValid():
            r, g, b, _ = QColor(color.rgb()).getRgb()
            if bloodpart == "RBC":
                self.RBC_color_label.setStyleSheet(
                    f"background-color: rgb({r}, {g}, {b});"
                )
                self.camera_thread.change_blood_cell_color("RBC", (b, g, r))
            elif bloodpart == "WBC":
                self.WBC_color_label.setStyleSheet(
                    f"background-color: rgb({r}, {g}, {b});"
                )
                self.camera_thread.change_blood_cell_color("WBC", (b, g, r))
            elif bloodpart == "PLT":
                self.PLT_color_label.setStyleSheet(
                    f"background-color: rgb({r}, {g}, {b});"
                )
                self.camera_thread.change_blood_cell_color("PLT", (b, g, r))


def update_frame_blood_cell_count(self, frame, net, RBC, WBC, PLT):
    """
    Update the frame with predictions for RBC, WBC, and PLT counts.

    Parameters:
        frame (np.ndarray): The original frame.
        net: The initialized Yolact model.
        RBC (int): Red blood cell count.
        WBC (int): White blood cell count.
        PLT (int): Platelet count.

    Returns:
        tuple: Updated frame and updated counts for RBC, WBC, and PLT.
    """
    frame, RBC, WBC, PLT = prediction.evaluate(
        net,
        frame,
        RBC,
        WBC,
        PLT,
    )
    torch.cuda.empty_cache()  # Clear CUDA memory cache
    return frame, RBC, WBC, PLT


def activate_leishmania(self, config):
    """
    Load the Leishmania YOLO model for predictions.

    Parameters:
        config (dict): Configuration dictionary containing the model's weight path.
    """
    self.leishmania_model = YOLO(config["yolo_weights"])


def update_frame_leishmania(self, frame):
    """
    Update the frame with Leishmania predictions.

    Parameters:
        frame (np.ndarray): The original frame.

    Returns:
        np.ndarray: The frame with predictions drawn on it.
    """
    results = self.leishmania_model.predict(frame, verbose=False)
    frame = results[0].plot()  # Draw predictions on the frame
    return frame


def analyze_leishmania(self, file_path, isimage, save_path):
    """
    Perform Leishmania analysis on a file.

    Parameters:
        file_path (str): The path of the file to analyze.
        isimage (bool): True if the file is an image, False if it's a video.
        save_path (str): The path to save analysis results.
    """
    self.leishmania_model = YOLO(
        "D:\\Leischmanien\\MicroPredictor-main\\MicroPredictor\\weights\\best.pt"
    )
    if isimage:
        # Analyze the image and save the results
        results = self.leishmania_model.predict([file_path], verbose=False)
        results[0].save(filename=f"{save_path}/{os.path.basename(file_path)}")
    else:
        # Analyze the video and save the results
        results = self.leishmania_model(
            file_path,
            stream=True,
            save=True,
            verbose=False,
            project=f"{save_path}",
            name="result",
        )
        for result in results:
            pass  # Ensure all frames are processed
