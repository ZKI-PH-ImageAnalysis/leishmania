import os
import sys
import time

import cv2
import yaml
from PIL import Image
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from models import (  # change_color,
    activate_blood_cell_count,
    activate_leishmania,
    analyze_leishmania,
    update_frame_blood_cell_count,
    update_frame_leishmania,
)

# Loading the config File
main_path = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(main_path, "config.yml"), "r") as file:
    config = yaml.safe_load(file)


class analyze_window(QWidget):
    def __init__(self):
        super().__init__()

        # Layout
        layout = QVBoxLayout()

        # Fenster-Titel
        self.setWindowTitle("Analyze Image/Video")

        # Add a box to choose a deep learning model for predictions
        self.model_groupbox = QGroupBox("Choose Model")
        self.model_groupbox.setCheckable(False)
        layout.addWidget(self.model_groupbox)

        self.model_vbox = QVBoxLayout(self.model_groupbox)
        self.model_groupbox.setLayout(self.model_vbox)

        self.model_combobox = QComboBox()
        self.model_combobox.addItems(["No Model", "Blood Cell Count", "Leishmania"])
        self.model_vbox.addWidget(self.model_combobox)
        self.model_combobox.currentTextChanged.connect(self.on_model_combobox_change)
        self.choosed_model = "no_model"

        # GroupBox für Radiobuttons
        self.image_or_video_groupbox = QGroupBox("Image or Video")
        self.image_or_video_groupbox.setCheckable(False)
        self.image_or_video_groupbox.setDisabled(True)
        self.image_or_video_groupbox.setFixedWidth(350)
        layout.addWidget(self.image_or_video_groupbox)

        # Layout innerhalb der GroupBox (vertikal)
        self.image_or_video_vbox = QVBoxLayout()
        self.image_or_video_groupbox.setLayout(self.image_or_video_vbox)

        # Layout für Radiobuttons (horizontal)
        self.image_or_video_hbox = QHBoxLayout()
        self.image_or_video_vbox.addLayout(self.image_or_video_hbox)

        # Radiobuttons
        self.image_radiobutton = QRadioButton("Image")
        self.image_radiobutton.setChecked(True)
        self.image_radiobutton.toggled.connect(self.update_format_label)
        self.image_or_video_hbox.addWidget(self.image_radiobutton)

        self.video_radiobutton = QRadioButton("Video")
        self.video_radiobutton.toggled.connect(self.update_format_label)
        self.image_or_video_hbox.addWidget(self.video_radiobutton)

        self.image_or_video_hbox.addStretch()

        # Label für unterstützte Formate
        self.format_label = QLabel("Formats:")
        self.image_or_video_vbox.addWidget(self.format_label)

        self.choose_file_hbox = QHBoxLayout()
        layout.addLayout(self.choose_file_hbox)

        self.choose_file_button = QPushButton("Choose Files")
        self.choose_file_button.setFixedWidth(100)
        self.choose_file_button.clicked.connect(self.choose_files)
        self.choose_file_button.setDisabled(True)
        self.choose_file_hbox.addWidget(self.choose_file_button)

        self.choose_files_label = QLabel("")
        self.choose_file_hbox.addWidget(self.choose_files_label)

        self.choose_file_hbox.addStretch()

        self.save_path_hbox = QHBoxLayout()
        layout.addLayout(self.save_path_hbox)

        self.set_save_path_button = QPushButton("Set Save Path")
        self.set_save_path_button.setMaximumWidth(100)
        self.set_save_path_button.clicked.connect(self.set_save_path)
        self.set_save_path_button.setDisabled(True)
        self.save_path_hbox.addWidget(self.set_save_path_button)

        self.save_path_label = QLabel("")
        self.save_path_hbox.addWidget(self.save_path_label)

        self.save_path_hbox.addStretch()

        # Close Button
        self.start_button = QPushButton("Start")
        self.start_button.setMaximumWidth(100)
        self.start_button.clicked.connect(self.start)
        self.start_button.setDisabled(True)
        layout.addWidget(self.start_button)

        self.prediction_progress_bar = QProgressBar()
        self.prediction_progress_bar.setFixedWidth(350)
        layout.addWidget(self.prediction_progress_bar)

        self.test_button = QPushButton("Close")
        self.test_button.setMaximumWidth(100)
        self.test_button.clicked.connect(self.close)
        self.test_button.setDisabled(True)
        layout.addWidget(self.test_button)

        layout.addStretch()

        # Setze das Layout
        self.setLayout(layout)

    def update_format_label(self):
        if (
            self.image_radiobutton.isChecked()
            and self.model_combobox.currentText() == "Leishmania"
        ):
            self.format_label.setText(
                "Formats: .bmp .dng .jpeg .jpg .mpo .png .tif .tiff .webp .pfm"
            )
            self.deactivate_old()
        elif (
            self.video_radiobutton.isChecked()
            and self.model_combobox.currentText() == "Leishmania"
        ):
            self.format_label.setText(
                "Formats: .asf .avi .gif .m4v .mkv .mov .mp4 .mpeg .mpg .ts .wmv .webm"
            )
            self.deactivate_old()

    def on_model_combobox_change(self):
        if self.model_combobox.currentText() == "No Model":
            self.format_label.setText("Formats:")
            self.image_or_video_groupbox.setDisabled(True)
            self.choose_file_button.setDisabled(True)
            self.deactivate_old()
        elif self.model_combobox.currentText() == "Blood Cell Count":
            self.image_or_video_groupbox.setDisabled(False)
            self.image_radiobutton.setChecked(True)
            self.video_radiobutton.setDisabled(True)
            self.format_label.setText("Formats: .jpg .jpeg .png .bmp .tif .tiff .webp")
            self.choose_file_button.setDisabled(False)
            self.deactivate_old()
        elif self.model_combobox.currentText() == "Leishmania":
            self.image_or_video_groupbox.setDisabled(False)
            self.video_radiobutton.setDisabled(False)
            self.update_format_label()
            self.choose_file_button.setDisabled(False)
            self.deactivate_old()

    def deactivate_old(self):
        self.set_save_path_button.setDisabled(True)
        self.start_button.setDisabled(True)
        self.files = []
        self.save_path = ""

    def choose_files(self):
        if self.image_radiobutton.isChecked():
            filter = "Images (*.bmp *.dng *.jpeg *.jpg *.mpo *.png *.tif *.tiff *.webp *.pfm)"
        elif self.video_radiobutton.isChecked():
            filter = "Video (*.asf *.avi *.gif *.m4v *.mkv *.mov *.mp4 *.mpeg *.mpg *.ts *.wmv *.webm)"
        self.files = QFileDialog.getOpenFileNames(self, "Choose Files", "", filter)[0]
        if self.files == []:
            return
        self.choose_files_label.setText(f"\u2714   {len(self.files)} files selected!")
        self.set_save_path_button.setDisabled(False)

    def set_save_path(self):
        self.save_path = QFileDialog.getExistingDirectory(self)
        print(self.save_path)
        if self.save_path == "":
            return
        self.start_button.setDisabled(False)
        self.save_path_label.setText(f"\u2714")

    def start(self):
        self.prediction_progress_bar.setValue(0)
        progress = 0
        self.model_groupbox.setDisabled(True)
        self.image_or_video_groupbox.setDisabled(True)
        self.choose_file_button.setDisabled(True)
        self.set_save_path_button.setDisabled(True)
        self.start_button.setDisabled(True)
        if self.image_radiobutton.isChecked() == True:
            for path in self.files:
                analyze_leishmania(self, path, True)
                progress += 1
                self.prediction_progress_bar.setValue(
                    (100 / len(self.files)) * progress
                )
        if self.video_radiobutton.isChecked() == True:
            for path in self.files:
                analyze_leishmania(self, path, False)
                progress += 1
                self.prediction_progress_bar.setValue(
                    (100 / len(self.files)) * progress
                )
        self.test_button.setDisabled(False)

    def test(self):
        self.steps = 16
        self.progress += 1
        self.prediction_progress_bar.setValue((100 / self.steps) * self.progress)
        if self.progress == self.steps:
            self.close()


class VideoStream(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Micro Predictor")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon(os.path.join(main_path, "image_1.png")))

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout(central_widget)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)  # Update frame every 10 milliseconds

        # Horizontal layout for buttons
        self.top_GUI_layout = QHBoxLayout()

        # Add a Start/Stop button
        self.start_stop_button = QPushButton("Start/Stop")
        self.start_stop_button.setMaximumWidth(100)
        self.start_stop_button.clicked.connect(self.start_stop_stream)
        self.top_GUI_layout.addWidget(self.start_stop_button)

        # Add a button to snap an image
        self.snap_image_is_clicked = False
        self.snap_image_button = QPushButton("Snap Image")
        self.snap_image_button.setMaximumWidth(100)
        self.snap_image_button.clicked.connect(self.snap_image)
        self.top_GUI_layout.addWidget(self.snap_image_button)

        # Add a button to set the save path of the pictures taken
        self.save_path = ""
        self.set_save_path_button = QPushButton("Set Save Path")
        self.set_save_path_button.setMaximumWidth(100)
        self.set_save_path_button.clicked.connect(self.set_save_path)
        self.top_GUI_layout.addWidget(self.set_save_path_button)

        # Add a button to set the save path of the pictures taken
        self.set_save_path_button = QPushButton("Analyze Image/Video")
        self.set_save_path_button.setMaximumWidth(150)
        self.set_save_path_button.clicked.connect(self.open_analyze_window)
        self.top_GUI_layout.addWidget(self.set_save_path_button)

        # Add a button to end everything
        self.quit_button = QPushButton("Quit")
        self.quit_button.setMaximumWidth(100)  # Set maximum width for button
        self.quit_button.clicked.connect(self.close)
        self.top_GUI_layout.addWidget(self.quit_button)

        # Add stretch to move buttons to the left
        self.top_GUI_layout.addStretch()

        # Add a label to schow current FPS
        self.fps_label = QLabel("")
        self.top_GUI_layout.addWidget(self.fps_label)

        # Add everything to the top row
        self.layout.addLayout(self.top_GUI_layout)

        # Create a Layout for the second row: options and scrollable area with livestream
        self.middle_GUI_layout = QHBoxLayout()

        # Add a vertical box for options
        self.options_groupbox = QVBoxLayout()

        # Add a box to change the Brightness
        self.brightness_groupbox = QGroupBox("Change Brightness")
        self.brightness_groupbox.setCheckable(False)
        self.brightness_groupbox.setMaximumWidth(200)
        self.options_groupbox.addWidget(self.brightness_groupbox)

        self.brightness_vbox = QVBoxLayout()
        self.brightness_groupbox.setLayout(self.brightness_vbox)

        self.brightness_hbox_1 = QHBoxLayout()
        self.brightness_vbox.addLayout(self.brightness_hbox_1)

        self.brightness_input_field = QLineEdit()
        self.brightness_input_field.setMaximumWidth(60)
        self.brightness_hbox_1.addWidget(self.brightness_input_field)

        self.brightness_confirm_button = QPushButton("Set")
        self.brightness_confirm_button.setMaximumWidth(100)
        self.brightness_confirm_button.clicked.connect(
            lambda: self.set_property(
                cv2.CAP_PROP_BRIGHTNESS,
                self.brightness_input_field.text(),
                config["camera_brightness_min"],
                config["camera_brightness_max"],
            )
        )
        self.brightness_hbox_1.addWidget(self.brightness_confirm_button)

        self.brightness_hbox_2 = QHBoxLayout()
        self.brightness_vbox.addLayout(self.brightness_hbox_2)

        self.brightness_mix_max_label = QLabel()
        self.brightness_hbox_2.addWidget(self.brightness_mix_max_label)
        self.brightness_mix_max_label.setText(
            f'{config["camera_brightness_min"]} - {config["camera_brightness_max"]}'
        )
        self.brightness_mix_max_label.setMaximumWidth(60)

        self.brightness_reset_button = QPushButton("Reset")
        self.brightness_reset_button.setMaximumWidth(100)
        self.brightness_reset_button.clicked.connect(
            lambda: self.reset_property(
                cv2.CAP_PROP_BRIGHTNESS, "camera_brightness_standard"
            )
        )
        self.brightness_hbox_2.addWidget(self.brightness_reset_button)

        # Add a box to change the Contrast
        self.contrast_groupbox = QGroupBox("Change Contrast")
        self.contrast_groupbox.setCheckable(False)
        self.contrast_groupbox.setMaximumWidth(200)
        self.options_groupbox.addWidget(self.contrast_groupbox)

        self.contrast_vbox = QVBoxLayout()
        self.contrast_groupbox.setLayout(self.contrast_vbox)

        self.contrast_hbox_1 = QHBoxLayout()
        self.contrast_vbox.addLayout(self.contrast_hbox_1)

        self.contrast_input_field = QLineEdit()
        self.contrast_input_field.setMaximumWidth(60)
        self.contrast_hbox_1.addWidget(self.contrast_input_field)

        self.contrast_confirm_button = QPushButton("Set")
        self.contrast_confirm_button.setMaximumWidth(100)
        self.contrast_confirm_button.clicked.connect(
            lambda: self.set_property(
                cv2.CAP_PROP_CONTRAST,
                self.contrast_input_field.text(),
                config["camera_contrast_min"],
                config["camera_contrast_max"],
            )
        )
        self.contrast_hbox_1.addWidget(self.contrast_confirm_button)

        self.contrast_hbox_2 = QHBoxLayout()
        self.contrast_vbox.addLayout(self.contrast_hbox_2)

        self.contrast_mix_max_label = QLabel()
        self.contrast_hbox_2.addWidget(self.contrast_mix_max_label)
        self.contrast_mix_max_label.setText(
            f'{config["camera_contrast_min"]} - {config["camera_contrast_max"]}'
        )
        self.contrast_mix_max_label.setMaximumWidth(60)

        self.contrast_reset_button = QPushButton("Reset")
        self.contrast_reset_button.setMaximumWidth(100)
        self.contrast_reset_button.clicked.connect(
            lambda: self.reset_property(
                cv2.CAP_PROP_CONTRAST, "camera_contrast_standard"
            )
        )
        self.contrast_hbox_2.addWidget(self.contrast_reset_button)

        # Add a box to change the Saturation
        self.saturation_groupbox = QGroupBox("Change Saturation")
        self.saturation_groupbox.setCheckable(False)
        self.saturation_groupbox.setMaximumWidth(200)
        self.options_groupbox.addWidget(self.saturation_groupbox)

        self.saturation_vbox = QVBoxLayout()
        self.saturation_groupbox.setLayout(self.saturation_vbox)

        self.saturation_hbox_1 = QHBoxLayout()
        self.saturation_vbox.addLayout(self.saturation_hbox_1)

        self.saturation_input_field = QLineEdit()
        self.saturation_input_field.setMaximumWidth(60)
        self.saturation_hbox_1.addWidget(self.saturation_input_field)

        self.saturation_confirm_button = QPushButton("Set")
        self.saturation_confirm_button.setMaximumWidth(100)
        self.saturation_confirm_button.clicked.connect(
            lambda: self.set_property(
                cv2.CAP_PROP_SATURATION,
                self.saturation_input_field.text(),
                config["camera_saturation_min"],
                config["camera_saturation_max"],
            )
        )
        self.saturation_hbox_1.addWidget(self.saturation_confirm_button)

        self.saturation_hbox_2 = QHBoxLayout()
        self.saturation_vbox.addLayout(self.saturation_hbox_2)

        self.saturation_mix_max_label = QLabel()
        self.saturation_hbox_2.addWidget(self.saturation_mix_max_label)
        self.saturation_mix_max_label.setText(
            f'{config["camera_saturation_min"]} - {config["camera_saturation_max"]}'
        )
        self.saturation_mix_max_label.setMaximumWidth(60)

        self.saturation_reset_button = QPushButton("Reset")
        self.saturation_reset_button.setMaximumWidth(100)
        self.saturation_reset_button.clicked.connect(
            lambda: self.reset_property(
                cv2.CAP_PROP_SATURATION, "camera_saturation_standard"
            )
        )
        self.saturation_hbox_2.addWidget(self.saturation_reset_button)

        # Add a box to change the Hue
        self.hue_groupbox = QGroupBox("Change Hue")
        self.hue_groupbox.setCheckable(False)
        self.hue_groupbox.setMaximumWidth(200)
        self.options_groupbox.addWidget(self.hue_groupbox)

        self.hue_vbox = QVBoxLayout()
        self.hue_groupbox.setLayout(self.hue_vbox)

        self.hue_hbox_1 = QHBoxLayout()
        self.hue_vbox.addLayout(self.hue_hbox_1)

        self.hue_input_field = QLineEdit()
        self.hue_input_field.setMaximumWidth(60)
        self.hue_hbox_1.addWidget(self.hue_input_field)

        self.hue_confirm_button = QPushButton("Set")
        self.hue_confirm_button.setMaximumWidth(100)
        self.hue_confirm_button.clicked.connect(
            lambda: self.set_property(
                cv2.CAP_PROP_HUE,
                self.hue_input_field.text(),
                config["camera_hue_min"],
                config["camera_hue_max"],
            )
        )
        self.hue_hbox_1.addWidget(self.hue_confirm_button)

        self.hue_hbox_2 = QHBoxLayout()
        self.hue_vbox.addLayout(self.hue_hbox_2)

        self.hue_mix_max_label = QLabel()
        self.hue_hbox_2.addWidget(self.hue_mix_max_label)
        self.hue_mix_max_label.setText(
            f'{config["camera_hue_min"]} - {config["camera_hue_max"]}'
        )
        self.hue_mix_max_label.setMaximumWidth(60)

        self.hue_reset_button = QPushButton("Reset")
        self.hue_reset_button.setMaximumWidth(100)
        self.hue_reset_button.clicked.connect(
            lambda: self.reset_property(cv2.CAP_PROP_HUE, "camera_hue_standard")
        )
        self.hue_hbox_2.addWidget(self.hue_reset_button)

        # Add a box to add a threshold
        self.threshold_groupbox = QGroupBox("Add Threshold")
        self.threshold_groupbox.setCheckable(True)
        self.threshold_groupbox.setChecked(False)
        self.threshold_groupbox.setMaximumWidth(200)

        self.options_groupbox.addWidget(self.threshold_groupbox)

        self.threshold_vbox = QVBoxLayout(self.threshold_groupbox)
        self.threshold_groupbox.setLayout(self.threshold_vbox)

        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setMinimum(0)
        self.threshold_slider.setMaximum(255)
        self.threshold_slider.setTickInterval(1)
        self.threshold_slider.setValue(128)
        self.threshold_slider.setMaximumWidth(200)
        self.threshold_slider.valueChanged.connect(self.change_slider_value)
        self.threshold_vbox.addWidget(self.threshold_slider)

        self.value_threshold_label = QLabel()
        self.value_threshold_label.setAlignment(Qt.AlignCenter)
        self.threshold_vbox.addWidget(self.value_threshold_label)
        self.value_threshold_label.setText(f"Threshold: 128")
        self.value_threshold = 128

        # Add a box to change the color space
        self.colorspace_groupbox = QGroupBox("Change Color Space")
        self.colorspace_groupbox.setCheckable(True)
        self.colorspace_groupbox.setChecked(False)
        self.options_groupbox.addWidget(self.colorspace_groupbox)

        self.colorspace_vbox = QVBoxLayout(self.colorspace_groupbox)
        self.colorspace_groupbox.setLayout(self.colorspace_vbox)

        self.color_radiobutton = QRadioButton("Color")
        self.color_radiobutton.setChecked(True)
        self.colorspace_vbox.addWidget(self.color_radiobutton)

        self.greyscale_radiobutton = QRadioButton("Greyscale")
        self.colorspace_vbox.addWidget(self.greyscale_radiobutton)

        # Add a box to choose a deep learning model for predictions
        self.model_groupbox = QGroupBox("Choose Model")
        self.model_groupbox.setCheckable(False)
        self.options_groupbox.addWidget(self.model_groupbox)

        self.model_vbox = QVBoxLayout(self.model_groupbox)
        self.model_groupbox.setLayout(self.model_vbox)

        self.model_combobox = QComboBox()
        self.model_combobox.addItems(["No Model", "Blood Cell Count", "Leishmania"])
        self.model_vbox.addWidget(self.model_combobox)
        self.model_combobox.currentTextChanged.connect(self.on_model_combobox_change)
        self.choosed_model = "no_model"

        # Add a stretch to move boxes to the top
        self.options_groupbox.addStretch()

        # Add options box to the second row
        self.middle_GUI_layout.addLayout(self.options_groupbox)

        # Add a scrollable area with the livestream inside, so it works on small desktops
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.video_label)

        self.middle_GUI_layout.addWidget(self.scroll_area)

        self.output_vgroupbox = QVBoxLayout()

        # Add a box for outputs and settings of the current model
        self.output_groupbox = QGroupBox("Model Settings")
        self.output_groupbox.setCheckable(False)
        self.output_groupbox.setFixedWidth(200)
        self.output_vgroupbox.addWidget(self.output_groupbox)

        self.output_vbox = QVBoxLayout(self.output_groupbox)
        self.output_groupbox.setLayout(self.output_vbox)

        self.output_vgroupbox.addStretch()

        self.middle_GUI_layout.addLayout(self.output_vgroupbox)

        self.layout.addLayout(self.middle_GUI_layout)

        # setup for the stream
        self.is_threshold = False
        self.cap = cv2.VideoCapture(1)  # Open default camera
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config["camera_width"])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config["camera_height"])
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        # self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
        self.is_streaming = True
        self.start_time = time.time()
        self.fps_hist = []

        if not self.cap.isOpened():
            print("Error: Could not open camera.")
            sys.exit()

        self.showMaximized()

    def start_stop_stream(self):
        """Small funktion to start or stop the stream"""
        if not self.is_streaming:
            self.timer.start(30)
            self.is_streaming = True
        else:
            self.timer.stop()
            self.is_streaming = False

    def snap_image(self):
        """Saves the current image under the path selected by set_save_path-function"""
        if self.save_path == "":
            QMessageBox.critical(
                self, "No path", "Set Save Path first!", QMessageBox.Ok
            )
            self.snap_image_is_clicked = False
            return
        n = 1
        while os.path.exists(f"{self.save_path}/image_{n}.tif"):
            n += 1
        cv2.imwrite(
            f"{self.save_path}/image_{n}.tif",
            cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB),
        )
        self.snap_image_is_clicked = False

    def set_save_path(self):
        """Set the save path for snapping images"""
        self.save_path = QFileDialog.getExistingDirectory(self)

    def update_frame(self):
        ret, self.frame = self.cap.read()
        if ret:
            width, height = self.frame.shape[:2]
            self.frame = self.frame[
                int((width - config["stream_width"]) / 2) : int(
                    (width + config["stream_width"]) / 2
                ),
                int((height - config["stream_height"]) / 2) : int(
                    (height + config["stream_height"]) / 2
                ),
            ]
            self.frame = cv2.resize(
                self.frame, (config["stream_width"], config["stream_height"])
            )
            if self.threshold_groupbox.isChecked():
                if self.choosed_model != "no_model":
                    self.model_combobox.setCurrentText("No Model")
                    QMessageBox.critical(
                        self,
                        "Can't activate Model",
                        "Can't use a model while Threshold ist active!",
                        QMessageBox.Ok,
                    )
                if self.colorspace_groupbox.isChecked() == True:
                    self.colorspace_groupbox.setChecked(False)
                    QMessageBox.critical(
                        self,
                        "Color Space Reset",
                        "Color space deactivated!",
                        QMessageBox.Ok,
                    )
                self.update_frame_threshold()
            elif (
                self.greyscale_radiobutton.isChecked()
                and self.colorspace_groupbox.isChecked()
            ):
                if self.choosed_model != "no_model":
                    self.model_combobox.setCurrentText("No Model")
                    QMessageBox.critical(
                        self,
                        "Can't activate Model",
                        "Can't use a model while color space is changed!",
                        QMessageBox.Ok,
                    )
                self.update_frame_greyscale()
            elif self.choosed_model == "blood_cell_count":
                update_frame_blood_cell_count(self)
            elif self.choosed_model == "leishmania":
                update_frame_leishmania(self)
            else:
                self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                h, w, ch = self.frame.shape
                bytes_per_line = ch * w
                qt_img = QImage(
                    self.frame.data, w, h, bytes_per_line, QImage.Format_RGB888
                )
                self.video_label.setPixmap(QPixmap.fromImage(qt_img))
                if self.snap_image_is_clicked == True:
                    self.snap_image(self.frame)

        # Calculate FPS
        curr_time = time.time()
        self.fps_hist.append((1 / (curr_time - self.start_time)))
        if len(self.fps_hist) > 50:
            self.fps_hist = self.fps_hist[-50:]
        avg_fps = sum(self.fps_hist) / len(self.fps_hist)
        self.fps_label.setText(f"FPS: {avg_fps:.2f}")
        self.start_time = time.time()

    def update_frame_threshold(self):
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        self.frame[self.frame <= self.value_threshold] = 0
        self.frame[self.frame > self.value_threshold] = 255
        h, w = self.frame.shape
        bytes_per_line = w
        qt_img = QImage(self.frame.data, w, h, bytes_per_line, QImage.Format_Grayscale8)
        self.video_label.setPixmap(QPixmap.fromImage(qt_img))

    def update_frame_greyscale(self):
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        h, w = self.frame.shape
        bytes_per_line = w
        qt_img = QImage(self.frame.data, w, h, bytes_per_line, QImage.Format_Grayscale8)
        self.video_label.setPixmap(QPixmap.fromImage(qt_img))

    def change_slider_value(self, value):
        self.value_threshold_label.setText(f"Threshold: {value}")
        self.value_threshold = value

    def set_property(self, property, input_field, min, max):
        try:
            if float(input_field) not in range(min, max + 1):
                QMessageBox.critical(
                    self,
                    "Wrong Input",
                    "Number is outside the working range!",
                    QMessageBox.Ok,
                )
                return
            self.cap.set(property, float(input_field))
        except:
            QMessageBox.critical(
                self, "Wrong Input", "Please enter a valid number!", QMessageBox.Ok
            )

    def reset_property(self, property, property_in_config):
        self.cap.set(property, config[property_in_config])

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

    def on_model_combobox_change(self, model):
        if model == "No Model":
            self.activate_no_model()
            self.choosed_model = "no_model"
        elif model == "Blood Cell Count":
            activate_blood_cell_count(self, config)
            self.choosed_model = "blood_cell_count"
        elif model == "Leishmania":
            activate_leishmania(self, config)
            self.choosed_model = "leishmania"

    def activate_no_model(self):
        layout = self.output_groupbox.layout()

        if layout is not None:
            # Entferne alle Widgets im Layout
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                elif item.layout() is not None:
                    self.clear_layout(item.layout())

            # Optional: Widgets in der Tiefe löschen, falls verschachtelte Layouts vorhanden sind
            self.clear_layout(layout)

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def open_analyze_window(self):
        self.w = analyze_window()
        self.w.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoStream()
    sys.exit(app.exec_())
