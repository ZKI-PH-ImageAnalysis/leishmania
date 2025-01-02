import os
import sys
import time

import cv2
import numpy as np
from PIL import Image
from PyQt5.QtCore import QProcess, QSize, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
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
    QSizePolicy,
    QSlider,
    QToolBar,
    QVBoxLayout,
    QWidget,
)
from ruamel.yaml import YAML

from models import (
    YolactWorker,
    activate_blood_cell_output,
    activate_leishmania,
    update_frame_blood_cell_count,
    update_frame_leishmania,
)

# Loading the config File
main_path = os.path.dirname(os.path.abspath(__file__))

# YAML object for loading and saving
yaml = YAML()
yaml.preserve_quotes = True  # Keep quotation marks


def load_config() -> None:
    """Load the configuration file"""
    global config
    try:
        with open(os.path.join(main_path, "config.yml"), "r") as file:
            config = yaml.load(file)
    except FileNotFoundError:
        sys.exit(
            "Please execute create_config.py first to create the configuration file!"
        )


def update_yaml_parameter(file_path: str, key: str, new_value: int) -> None:
    """Update parameters in the configuration file"""
    if key in config:
        config[key] = new_value
    else:
        raise KeyError(f"Key '{key}' not found in the YAML file.")

    # Save YAML file
    with open(file_path, "w") as file:
        yaml.dump(config, file)


load_config()


class Settings(QWidget):
    """
    A QWidget subclass for managing application settings.

    This window allows the user to adjust the camera resolution settings.
    """

    def __init__(self):
        """
        Initialize the Settings window.

        Sets up the layout, UI components, and connects signals for user interactions.
        """
        super().__init__()

        # Main layout for the Settings window
        self.layout = QVBoxLayout()
        self.setWindowTitle("Settings")  # Set the window title

        # Create a vertical layout for settings options
        self.options_groupbox = QVBoxLayout()

        # Group box for resolution settings
        self.resolution_groupbox = QGroupBox("Change Resolution")
        self.resolution_groupbox.setCheckable(False)  # Disable checkbox functionality

        # Layout for the resolution group box
        self.resolution_layout = QVBoxLayout()
        self.resolution_groupbox.setLayout(self.resolution_layout)

        # Create a combo box to list available camera resolutions
        self.resolution_combobox = QComboBox()
        for res in config["camera_resolutions"]:
            # Add each resolution option to the combo box
            self.resolution_combobox.addItem(f"{res[0]} x {res[1]}")
        # Set the current index to the resolution in use
        self.resolution_combobox.setCurrentIndex(config["used_camera_resolution"])

        # Add the combo box to the resolution group box layout
        self.resolution_layout.addWidget(self.resolution_combobox)

        # Add the resolution group box to the main settings layout
        self.options_groupbox.addWidget(self.resolution_groupbox)

        # Connect the combo box signal to the resolution change handler
        self.resolution_combobox.currentTextChanged.connect(self.change_resolution)

        # Add the options layout to the main layout
        self.layout.addLayout(self.options_groupbox)

        # Set the main layout for the Settings widget
        self.setLayout(self.layout)

    def change_resolution(self) -> None:
        """
        Handle resolution changes triggered by the combo box.

        Updates the resolution setting in the configuration file and reminds
        the user to restart the stream for changes to take effect.
        """
        # Update the resolution setting in the YAML configuration file
        update_yaml_parameter(
            os.path.join(main_path, "config.yml"),
            "used_camera_resolution",
            self.resolution_combobox.currentIndex(),
        )

        # Display a message box reminding the user to restart the stream
        restart_reminder = QMessageBox()
        restart_reminder.setWindowTitle("Restart Stream")
        restart_reminder.setText(
            "Stream must be restarted for the changes to take effect."
        )
        restart_reminder.setIcon(QMessageBox.Information)  # Set information icon
        restart_reminder.setStandardButtons(QMessageBox.Ok)  # Add an OK button
        restart_reminder.exec_()  # Show the message box


class SnapSettings(QWidget):
    """
    A QWidget subclass for managing snapshot settings.

    This window allows the user to configure scaling and cropping options
    for captured snapshots.
    """

    def __init__(self):
        """
        Initialize the Snap Settings window.

        Sets up the layout, UI components, and connects signals for user interactions.
        """
        super().__init__()

        # Main layout for the Snap Settings window
        self.layout = QVBoxLayout()
        self.setWindowTitle("Snap Image Settings")  # Set the window title

        # Create a vertical layout for the options group box
        self.options_groupbox = QVBoxLayout()

        # Group box for scaling options
        self.scaling_groupbox = QGroupBox("Change Scaling")
        self.scaling_groupbox.setCheckable(True)  # Allow toggling the scaling feature
        self.scaling_groupbox.setChecked(
            config["change_scaling"]
        )  # Set initial checkbox state from config
        self.scaling_groupbox.toggled.connect(
            self.scaling_groupbox_toggled
        )  # Connect toggle event to handler
        self.options_groupbox.addWidget(self.scaling_groupbox)

        # Layout for the scaling group box
        self.scaling_vbox = QVBoxLayout()
        self.scaling_groupbox.setLayout(self.scaling_vbox)

        # Add radio buttons for crop or resize options
        self.scaling_hbox_radiobuttons = QHBoxLayout()
        self.scaling_vbox.addLayout(self.scaling_hbox_radiobuttons)

        self.crop_radiobutton = QRadioButton("Crop")
        self.scaling_hbox_radiobuttons.addWidget(self.crop_radiobutton)

        self.resize_radiobutton = QRadioButton("Resize")
        self.scaling_hbox_radiobuttons.addWidget(self.resize_radiobutton)

        # Set the default selected option based on the config
        if config["crop_or_resize"] == "crop":
            self.crop_radiobutton.setChecked(True)
        else:
            self.resize_radiobutton.setChecked(True)

        # Connect the toggle event for the crop/resize radio buttons
        self.crop_radiobutton.toggled.connect(self.scaling_radiobuttons_toggled)

        # Add spacing to align the radio buttons
        self.scaling_hbox_radiobuttons.addStretch()

        # Add input fields for width and height
        self.scaling_hbox_1 = QHBoxLayout()
        self.scaling_vbox.addLayout(self.scaling_hbox_1)

        self.width_input_field = QLineEdit()
        self.width_input_field.setMaximumWidth(50)
        self.width_input_field.setPlaceholderText(
            "Width"
        )  # Placeholder text for width input
        self.scaling_hbox_1.addWidget(self.width_input_field)

        self.height_input_field = QLineEdit()
        self.height_input_field.setMaximumWidth(50)
        self.height_input_field.setPlaceholderText(
            "Height"
        )  # Placeholder text for height input
        self.scaling_hbox_1.addWidget(self.height_input_field)

        # Add spacing to align the input fields
        self.scaling_hbox_1.addStretch()

        # Add a "Set" button to confirm scaling updates
        self.scaling_hbox_2 = QHBoxLayout()
        self.scaling_vbox.addLayout(self.scaling_hbox_2)

        self.scaling_set_button = QPushButton("Set")
        self.scaling_set_button.setMaximumWidth(50)
        self.scaling_set_button.clicked.connect(
            self.scaling_snaps_update
        )  # Connect button to scaling update handler
        self.scaling_hbox_2.addWidget(self.scaling_set_button)

        # Add spacing to align the button
        self.scaling_hbox_2.addStretch()

        # Add a label to display the current camera resolution
        self.scaling_hbox_3 = QHBoxLayout()
        self.scaling_vbox.addLayout(self.scaling_hbox_3)

        self.scaling_current_resolution_label = QLabel()
        self.scaling_hbox_3.addWidget(self.scaling_current_resolution_label)
        self.scaling_current_resolution_label.setText(
            f'Current Resolution: {config["camera_resolutions"][config["used_camera_resolution"]][0]} x {config["camera_resolutions"][config["used_camera_resolution"]][1]}',
        )

        # Add spacing for alignment
        self.scaling_hbox_3.addStretch()

        # Add a label to display the current scaling/cropping resolution
        self.scaling_hbox_4 = QHBoxLayout()
        self.scaling_vbox.addLayout(self.scaling_hbox_4)

        self.scaling_snap_resolution_label = QLabel()
        self.scaling_hbox_4.addWidget(self.scaling_snap_resolution_label)

        # Set the initial label for scaling resolution
        self.set_scaling_resolution_label()

        # Add spacing for alignment
        self.scaling_hbox_4.addStretch()

        # Add the options group box to the main layout
        self.layout.addLayout(self.options_groupbox)

        # Set the main layout for the widget
        self.setLayout(self.layout)

    def scaling_groupbox_toggled(self):
        """
        Handle toggling of the scaling group box.

        Updates the configuration and reloads the settings.
        """
        update_yaml_parameter(
            os.path.join(main_path, "config.yml"),
            "change_scaling",
            self.scaling_groupbox.isChecked(),
        )
        load_config()  # Reload the configuration to reflect changes

    def scaling_radiobuttons_toggled(self):
        """
        Handle toggling between "Crop" and "Resize" modes.

        Updates the configuration and refreshes the scaling resolution label.
        """
        if self.crop_radiobutton.isChecked():
            update_yaml_parameter(
                os.path.join(main_path, "config.yml"),
                "crop_or_resize",
                "crop",
            )
        else:
            update_yaml_parameter(
                os.path.join(main_path, "config.yml"),
                "crop_or_resize",
                "resize",
            )
        load_config()  # Reload the configuration
        self.set_scaling_resolution_label()  # Update the resolution label

    def set_scaling_resolution_label(self):
        """
        Update the label displaying the current crop or resize resolution.
        """
        if config["crop_or_resize"] == "crop":
            if config["scaling_width"] is None or config["scaling_height"] is None:
                self.scaling_snap_resolution_label.setText("Crop Resolution: Not Set")
            else:
                self.scaling_snap_resolution_label.setText(
                    f"Crop Resolution: {config['scaling_width']} x {config['scaling_height']}",
                )
        else:
            if config["scaling_width"] is None or config["scaling_height"] is None:
                self.scaling_snap_resolution_label.setText("Resize Resolution: Not Set")
            else:
                self.scaling_snap_resolution_label.setText(
                    f"Resize Resolution: {config['scaling_width']} x {config['scaling_height']}",
                )

    def scaling_snaps_update(self):
        """
        Update the scaling resolution based on the input fields.

        Validates user input and updates the configuration with the new values.
        """
        # Validate and update the width input
        if (
            self.width_input_field.text() != ""
            and self.width_input_field.text().isdigit()
            and int(self.width_input_field.text())
            <= config["camera_resolutions"][config["used_camera_resolution"]][0]
        ):
            update_yaml_parameter(
                os.path.join(main_path, "config.yml"),
                "scaling_width",
                int(self.width_input_field.text()),
            )

        # Validate and update the height input
        if (
            self.height_input_field.text() != ""
            and self.height_input_field.text().isdigit()
            and int(self.height_input_field.text())
            <= config["camera_resolutions"][config["used_camera_resolution"]][1]
        ):
            update_yaml_parameter(
                os.path.join(main_path, "config.yml"),
                "scaling_height",
                int(self.height_input_field.text()),
            )

        load_config()  # Reload the configuration to reflect changes
        self.set_scaling_resolution_label()  # Update the resolution label


class FileDialogWorker(QThread):
    """
    A QThread subclass for handling file dialog operations in a separate thread.

    This class allows the execution of a file dialog without blocking the main GUI thread.
    """

    def run(self) -> None:
        """
        Execute the file dialog in a worker thread.

        Opens a directory selection dialog and emits a signal with the selected directory
        path when the user completes their selection.
        """
        # Open a directory selection dialog and store the selected path
        selected_dir = QFileDialog.getExistingDirectory()

        if selected_dir != "":
            # Emit the signal to send the selected directory back to the main thread
            update_yaml_parameter(
                os.path.join(main_path, "config.yml"),
                "save_path",
                selected_dir,
            )


class CameraThread(QThread):
    # Signal sent by the captured image
    frame_ready = pyqtSignal(QImage, float)
    send_count_update = pyqtSignal(int, int, int)
    open_dialog_signal = pyqtSignal()

    def __init__(self, value_threshold: int) -> None:
        super().__init__()
        # setup for the stream
        self.cap = cv2.VideoCapture(config["camera_nr"])  # Open default camera
        self.cap.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            config["camera_resolutions"][config["used_camera_resolution"]][0],
        )
        self.cap.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            config["camera_resolutions"][config["used_camera_resolution"]][1],
        )
        self.is_streaming = True
        self.last_frame_time = None
        self.threshold = False
        self.color_space = False
        self.choosen_color_space = 0
        self.value_threshold = value_threshold
        self.choosed_model = "no_model"
        self.fit_image = True
        self.stream_is_paused = False
        self.snap_image_is_clicked = False

        if not self.cap.isOpened():
            print("Error: Could not open camera.")
            sys.exit()

    def run(self) -> None:
        """
        Run the livestream and process frames continuously.

        This function manages the livestream, processes each frame (e.g., applying thresholds,
        converting color spaces, or making model predictions), and emits the processed frames
        and FPS to the main thread.
        """
        while self.is_streaming:
            if self.stream_is_paused:
                continue  # Skip processing if the stream is paused

            ret, frame = self.cap.read()  # Capture a frame from the video stream
            if ret:
                # Calculate FPS
                current_time = time.time()
                if self.last_frame_time is not None:
                    if current_time - self.last_frame_time == 0:
                        return
                    fps = 1.0 / (current_time - self.last_frame_time)
                else:
                    fps = 0.0
                self.last_frame_time = current_time

                # Process the frame based on active settings
                if self.threshold:
                    frame = self.update_frame_threshold(frame)
                elif self.color_space and self.choosen_color_space == 1:
                    frame = self.update_frame_greyscale(frame)
                elif self.choosed_model == "blood_cell_count":
                    prediction_factor = self.get_prediction_factor(1000, 1000)
                    prediction_frame = self.get_prediction_frame(
                        frame, prediction_factor
                    )
                    masked_frame, RBC, WBC, PLT = update_frame_blood_cell_count(
                        self,
                        prediction_frame,
                        self.model,
                        self.RBC_color,
                        self.WBC_color,
                        self.PLT_color,
                    )
                    frame = self.put_mask_on_original_frame(
                        frame, prediction_frame, masked_frame
                    )
                    self.send_count_update.emit(RBC, WBC, PLT)  # Emit cell count data
                elif self.choosed_model == "leishmania":
                    prediction_factor = self.get_prediction_factor(1920, 1440)
                    prediction_frame = self.get_prediction_frame(
                        frame, prediction_factor
                    )
                    masked_frame = update_frame_leishmania(self, prediction_frame)
                    frame = self.put_mask_on_original_frame(
                        frame, prediction_frame, masked_frame
                    )

                # Check if an image should be saved
                if self.snap_image_is_clicked:
                    self.snap_image(frame)

                # Convert the frame to RGB format for display
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Adjust frame size if necessary
                if self.fit_image:
                    frame = self.fit_image_size(frame)

                # Determine the image format and prepare it for display
                if len(frame.shape) == 3:  # Color image
                    h, w, ch = frame.shape
                    bytes_per_line = ch * w
                    image_format = QImage.Format_RGB888
                elif len(frame.shape) == 2:  # Grayscale image
                    h, bytes_per_line = frame.shape
                    image_format = QImage.Format_Grayscale8

                qt_img = QImage(frame.data, w, h, bytes_per_line, image_format)

                # Emit the processed frame and FPS to the main thread
                self.frame_ready.emit(qt_img, fps)

        # Release the video capture object when streaming ends
        self.cap.release()

    def pause_stream(self, pause: bool) -> None:
        """
        Pause or resume the livestream.

        Parameters:
            pause (bool): True to pause the stream, False to resume.
        """
        self.stream_is_paused = pause

    def set_property(self, property: int, value: float) -> None:
        """
        Update a camera property and save the updated value to the configuration file.

        Parameters:
            property (int): The OpenCV property identifier.
            value (float): The new value for the property.
        """
        self.cap.set(property, float(value))  # Set the property in the video capture
        # Update the corresponding configuration value
        if property == 10:  # Brightness
            update_yaml_parameter(
                os.path.join(main_path, "config.yml"),
                "camera_brightness_used",
                int(value),
            )
        elif property == 11:  # Contrast
            update_yaml_parameter(
                os.path.join(main_path, "config.yml"),
                "camera_contrast_used",
                int(value),
            )
        elif property == 12:  # Saturation
            update_yaml_parameter(
                os.path.join(main_path, "config.yml"),
                "camera_saturation_used",
                int(value),
            )
        elif property == 13:  # Hue
            update_yaml_parameter(
                os.path.join(main_path, "config.yml"),
                "camera_hue_used",
                int(value),
            )

    def fit_image_size(self, frame: np.ndarray) -> np.ndarray:
        """
        Resize the frame to fit within the specified image size while maintaining aspect ratio.

        Parameters:
            frame (np.ndarray): The frame to resize.

        Returns:
            np.ndarray: The resized frame.
        """
        if (self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) / self.image_size[0]) > (
            self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / self.image_size[1]
        ):
            image_factor = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) / self.image_size[0]
        else:
            image_factor = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / self.image_size[1]

        if image_factor > 1:
            frame = cv2.resize(
                frame,
                (
                    int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) / image_factor) - 2,
                    int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / image_factor) - 2,
                ),
            )
        return frame

    def update_image_size(self, width: int, height: int) -> None:
        """
        Update the target image size for display.

        Parameters:
            width (int): The target width.
            height (int): The target height.
        """
        self.image_size = (width, height)

    def get_prediction_factor(
        self, prediction_width: int, prediction_height: int
    ) -> float:
        """
        Calculate the scaling factor to resize the frame for prediction.

        Parameters:
            prediction_width (int): The target prediction width.
            prediction_height (int): The target prediction height.

        Returns:
            float: The calculated scaling factor.
        """
        if (self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) / prediction_width) >= (
            self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / prediction_height
        ):
            return self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / prediction_height
        else:
            return self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) / prediction_width

    def get_prediction_frame(self, frame: np.ndarray, factor: float) -> np.ndarray:
        """
        Resize the frame based on the prediction scaling factor.

        Parameters:
            frame (np.ndarray): The original frame.
            factor (float): The scaling factor.

        Returns:
            np.ndarray: The resized frame.
        """
        return cv2.resize(
            frame,
            (
                int(round(frame.shape[1] / factor)),
                int(round((frame.shape[0] / factor))),
            ),
        )

    def put_mask_on_original_frame(
        self,
        original_image: np.ndarray,
        small_image_without_mask: np.ndarray,
        small_image_with_mask: np.ndarray,
    ) -> np.ndarray:
        """
        Apply a mask to the original frame.

        Parameters:
            original_image (np.ndarray): The original frame.
            small_image_without_mask (np.ndarray): The small frame without the mask.
            small_image_with_mask (np.ndarray): The small frame with the mask.

        Returns:
            np.ndarray: The combined frame with the mask applied.
        """
        # Calculate the difference to create a binary mask
        mask_diff = cv2.absdiff(small_image_with_mask, small_image_without_mask)
        gray_mask = cv2.cvtColor(mask_diff, cv2.COLOR_BGR2GRAY)
        _, binary_mask = cv2.threshold(gray_mask, 1, 255, cv2.THRESH_BINARY)

        # Resize the mask and the masked image to the original size
        large_mask = cv2.resize(
            binary_mask,
            (original_image.shape[1], original_image.shape[0]),
            interpolation=cv2.INTER_NEAREST,
        )
        large_image_with_mask = cv2.resize(
            small_image_with_mask,
            (original_image.shape[1], original_image.shape[0]),
            interpolation=cv2.INTER_NEAREST,
        )

        # Apply the mask
        inverse_large_mask = cv2.bitwise_not(large_mask)
        background = cv2.bitwise_and(
            original_image, original_image, mask=inverse_large_mask
        )
        masked_foreground = cv2.bitwise_and(
            large_image_with_mask, large_image_with_mask, mask=large_mask
        )

        # Combine the background and masked foreground
        return cv2.add(background, masked_foreground)

    def change_to_full_resolution_image(self, full_resolution: bool) -> None:
        """
        Toggle between fitting the image to the display or showing it in full resolution.

        Parameters:
            full_resolution (bool): True for full resolution, False to fit the display.
        """
        self.fit_image = not full_resolution  # Invert the logic to match the toggle

    def update_frame_threshold(self, frame: np.ndarray) -> np.ndarray:
        """
        Apply a threshold filter to the frame.

        Pixels below or above the threshold value are set to either black or white.

        Parameters:
            frame (np.ndarray): The original frame.

        Returns:
            np.ndarray: The thresholded frame.
        """
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
        frame[frame <= self.value_threshold] = 0  # Set pixels below threshold to black
        frame[frame > self.value_threshold] = 255  # Set pixels above threshold to white
        return frame

    def threshold_toggled(self, checked: bool) -> None:
        """
        Enable or disable the thresholding functionality.

        Parameters:
            checked (bool): True to enable thresholding, False to disable.
        """
        self.threshold = checked

    def set_threshold(self, value: int) -> None:
        """
        Set the threshold value for frame processing.

        Parameters:
            value (int): The new threshold value.
        """
        self.value_threshold = value

    def update_frame_greyscale(self, frame: np.ndarray) -> np.ndarray:
        """
        Convert the frame to grayscale.

        Parameters:
            frame (np.ndarray): The original frame.

        Returns:
            np.ndarray: The grayscale frame.
        """
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def color_space_toggled(self, checked: bool) -> None:
        """
        Enable or disable the color space conversion.

        Parameters:
            checked (bool): True to enable color space conversion, False to disable.
        """
        self.color_space = checked

    def choose_color_space(self, choice: int) -> None:
        """
        Choose the color space for frame processing.

        Parameters:
            choice (int): 0 for RGB, 1 for grayscale.
        """
        self.choosen_color_space = choice

    def chosen_model(self, model: str) -> None:
        """
        Set the selected model for frame analysis.

        Parameters:
            model (str): The name of the selected model.
                        "No Model", "Blood Cell Count", or "Leishmania".
        """
        if model == "No Model":
            self.choosed_model = "no_model"
        elif model == "Blood Cell Count":
            # Initialize worker thread for blood cell count model
            self.worker = YolactWorker(config)
            self.worker.model_initialized.connect(self.on_model_initialized)
            self.worker.error_occurred.connect(self.on_error_occurred)
            self.worker.start()  # Start the worker thread
        elif model == "Leishmania":
            activate_leishmania(self, config)
            self.choosed_model = "leishmania"

    def on_model_initialized(self, model) -> None:
        """
        Handle the initialization of the model.

        Parameters:
            model: The initialized model object.
        """
        self.model = model
        self.RBC_color = (0, 0, 255)  # Red for RBC
        self.WBC_color = (255, 0, 0)  # Blue for WBC
        self.PLT_color = (0, 255, 0)  # Green for PLT
        self.choosed_model = "blood_cell_count"

    def change_blood_cell_color(self, cell_type: str, color: tuple) -> None:
        """
        Change the color representation for specific blood cell types.

        Parameters:
            cell_type (str): The cell type ("RBC", "WBC", or "PLT").
            color (tuple): The new color in (B, G, R) format.
        """
        if cell_type == "RBC":
            self.RBC_color = color
        elif cell_type == "WBC":
            self.WBC_color = color
        elif cell_type == "PLT":
            self.PLT_color = color

    def on_error_occurred(self, error_message: str) -> None:
        """
        Handle errors that occur during model initialization or processing.

        Parameters:
            error_message (str): The error message to display.
        """
        print(f"Error during model initialization: {error_message}")

    def snap_image_clicked(self) -> None:
        """
        Mark that an image should be captured on the next frame.
        """
        self.snap_image_is_clicked = True

    def snap_image(self, frame: np.ndarray) -> None:
        """
        Save the current frame as an image file.

        Parameters:
            frame (np.ndarray): The frame to save.
        """
        n = 1
        # Find the next available filename
        while os.path.exists(f"{config['save_path']}/image_{n}.tif"):
            n += 1

        # Apply scaling or cropping if enabled
        if config["change_scaling"]:
            if config["crop_or_resize"] == "crop":
                frame = self.crop_image(frame)
            else:
                frame = self.resize_image(frame)

        # Save the frame as an image
        cv2.imwrite(f"{config['save_path']}/image_{n}.tif", frame)
        self.snap_image_is_clicked = False

    def crop_image(self, frame: np.ndarray) -> np.ndarray:
        """
        Crop the frame to the specified dimensions.

        Parameters:
            frame (np.ndarray): The original frame.

        Returns:
            np.ndarray: The cropped frame.
        """
        height, width = frame.shape[:2]
        left = int((width - config["scaling_width"]) / 2)
        top = int((height - config["scaling_height"]) / 2)
        right = int((width + config["scaling_width"]) / 2)
        bottom = int((height + config["scaling_height"]) / 2)
        return frame[top:bottom, left:right]

    def resize_image(self, frame: np.ndarray) -> np.ndarray:
        """
        Resize the frame to the specified dimensions.

        Parameters:
            frame (np.ndarray): The original frame.

        Returns:
            np.ndarray: The resized frame.
        """
        return cv2.resize(frame, (config["scaling_width"], config["scaling_height"]))

    def stop(self) -> None:
        """
        Stop the livestreaming process and emit the finished signal.
        """
        self.is_streaming = False
        self.finished.emit()


class VideoStream(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window properties
        self.setWindowTitle("Micro Predictor")
        self.setGeometry(100, 100, 800, 600)
        self.stream_running = False  # Flag to indicate if the stream is running

        # Set up the central widget and main layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        # Create a menu bar
        menu = self.menuBar()

        # Set up the toolbar for the main window
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(self.toolbar)

        # Add Start Stream button to the toolbar
        self.start_button = QAction(
            QIcon(f"{main_path}\\buttons\\start_button.png"),
            "Start Stream",
            self,
        )
        self.start_button.triggered.connect(
            self.start_stream
        )  # Connect button to the start_stream method
        self.start_button.setCheckable(False)
        self.toolbar.addAction(self.start_button)

        # Add Pause Stream button to the toolbar
        self.pause_button = QAction(
            QIcon(f"{main_path}\\buttons\\pause_button.png"),
            "Pause Stream",
            self,
        )
        self.pause_button.setStatusTip("This is your button")
        self.pause_button.triggered.connect(
            self.pause_stream
        )  # Connect button to the pause_stream method
        self.pause_button.setCheckable(True)
        self.pause_button.setDisabled(True)
        self.toolbar.addAction(self.pause_button)

        # Add Stop Stream button to the toolbar
        self.stop_button = QAction(
            QIcon(f"{main_path}\\buttons\\stop_button.png"),
            "Stop Stream",
            self,
        )
        self.stop_button.triggered.connect(
            self.stop_stream
        )  # Connect button to the stop_stream method
        self.stop_button.setCheckable(False)
        self.stop_button.setDisabled(True)
        self.toolbar.addAction(self.stop_button)

        # Add Snap Image button to the toolbar
        self.snap_button = QAction(
            QIcon(f"{main_path}\\buttons\\snap_button.png"),
            "Snap Image",
            self,
        )
        self.snap_button.triggered.connect(
            self.snap_image_clicked
        )  # Connect button to snap_image_clicked method
        self.snap_button.setCheckable(False)
        self.snap_button.setDisabled(True)
        self.toolbar.addAction(self.snap_button)

        # Add Set Save Path button to the toolbar
        self.save_path_button = QAction(
            QIcon(f"{main_path}\\buttons\\save_path_button.png"),
            "Set Save Path",
            self,
        )
        self.save_path_button.triggered.connect(
            self.set_save_path
        )  # Connect button to set_save_path method
        self.save_path_button.setCheckable(False)
        self.save_path_button.setDisabled(True)
        self.toolbar.addAction(self.save_path_button)

        # Create the main menu and add options
        self.main_menu = menu.addMenu("&Menu")
        self.open_analyze_window_action = QAction("Analyze Image/Video", self)
        self.open_analyze_window_action.triggered.connect(self.open_analyze_window)
        self.main_menu.addAction(self.open_analyze_window_action)

        # Create and connect the Analyze Process
        self.analyze_process = QProcess(self)

        # Add other menu items
        self.main_menu.addSeparator()
        self.settings_action = QAction("Settings", self)
        self.settings_action.triggered.connect(self.open_settings)
        self.main_menu.addAction(self.settings_action)
        self.main_menu.addSeparator()
        self.quit_action = QAction("Quit", self)
        self.quit_action.triggered.connect(self.close)
        self.main_menu.addAction(self.quit_action)
        self.main_menu.addSeparator()

        # Create Stream Control menu and add stream actions
        self.stream_control_menu = menu.addMenu("&Stream Control")
        self.stream_control_menu.addAction(self.start_button)
        self.stream_control_menu.addAction(self.pause_button)
        self.stream_control_menu.addAction(self.stop_button)

        # Create Snap menu and add snap actions
        self.snap_menu = menu.addMenu("&Snap")
        self.snap_menu.addAction(self.snap_button)
        self.snap_menu.addAction(self.save_path_button)

        # Add Snap Settings to the Snap menu
        self.snap_settings_action = QAction("Snap Image Settings", self)
        self.snap_settings_action.triggered.connect(self.open_snap_settings)
        self.snap_menu.addAction(self.snap_settings_action)

        # Add spacer to the toolbar to push elements to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.toolbar.addWidget(spacer)

        # Add FPS label to the toolbar
        self.fps_label = QLabel("")
        self.toolbar.addWidget(self.fps_label)

        # Create layout for GUI elements below the toolbar
        self.middle_GUI_layout = QHBoxLayout()

        # Add vertical box for settings and sliders (options panel)
        self.options_groupbox = QVBoxLayout()

        # Create a brightness control group box
        self.brightness_slider_groupbox = QGroupBox("Change Brightness")
        self.brightness_slider_groupbox.setCheckable(False)
        self.brightness_slider_groupbox.setDisabled(True)
        self.brightness_slider_groupbox.setMaximumWidth(200)
        self.options_groupbox.addWidget(self.brightness_slider_groupbox)

        # Add a slider to control brightness
        self.brightness_slider_vbox = QVBoxLayout(self.brightness_slider_groupbox)
        self.brightness_slider_groupbox.setLayout(self.brightness_slider_vbox)
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setMinimum(config["camera_brightness_min"])
        self.brightness_slider.setMaximum(config["camera_brightness_max"])
        self.brightness_slider.setTickInterval(1)
        self.brightness_slider.setValue(config["camera_brightness_used"])
        self.brightness_slider.setMaximumWidth(200)
        self.brightness_slider.valueChanged.connect(
            lambda: self.change_property(
                cv2.CAP_PROP_BRIGHTNESS, self.brightness_slider.value(), "brightness"
            )
        )

        # Add reset button for the brightness slider
        self.brightness_slider_reset_button = QPushButton("Reset")
        self.brightness_slider_reset_button.setMaximumWidth(50)
        self.brightness_slider_reset_button.clicked.connect(
            lambda: self.reset_property(
                cv2.CAP_PROP_BRIGHTNESS, "camera_brightness_standard", "brightness"
            )
        )

        # Add slider and reset button to the horizontal layout
        self.brightness_slider_hbox = QHBoxLayout()
        self.brightness_slider_hbox.addWidget(self.brightness_slider)
        self.brightness_slider_hbox.addWidget(self.brightness_slider_reset_button)
        self.brightness_slider_vbox.addLayout(self.brightness_slider_hbox)

        # Add a label to show brightness value
        self.value_brightness_slider_label = QLabel()
        self.value_brightness_slider_label.setAlignment(Qt.AlignLeft)
        self.value_brightness_slider_label.setText(
            f"Brightness: {config['camera_brightness_used']}"
        )
        self.brightness_slider_vbox.addWidget(self.value_brightness_slider_label)

        # Add a box to change the Contrast
        self.contrast_slider_groupbox = QGroupBox("Change Contrast")
        self.contrast_slider_groupbox.setCheckable(
            False
        )  # Disable group box checkbox functionality
        self.contrast_slider_groupbox.setDisabled(
            True
        )  # Disable the group box by default
        self.contrast_slider_groupbox.setMaximumWidth(
            200
        )  # Limit the width of the group box

        # Add the contrast group box to the options layout
        self.options_groupbox.addWidget(self.contrast_slider_groupbox)

        # Create a vertical layout for the contrast group box
        self.contrast_slider_vbox = QVBoxLayout(self.contrast_slider_groupbox)
        self.contrast_slider_groupbox.setLayout(self.contrast_slider_vbox)

        # Create the contrast slider
        self.contrast_slider = QSlider(
            Qt.Horizontal
        )  # Horizontal slider for contrast adjustment
        self.contrast_slider.setMinimum(
            config["camera_contrast_min"]
        )  # Set minimum contrast value
        self.contrast_slider.setMaximum(
            config["camera_contrast_max"]
        )  # Set maximum contrast value
        self.contrast_slider.setTickInterval(1)  # Set the step size for the slider
        self.contrast_slider.setValue(
            config["camera_contrast_used"]
        )  # Set initial contrast value
        self.contrast_slider.setMaximumWidth(200)  # Limit the slider width
        self.contrast_slider.valueChanged.connect(
            lambda: self.change_property(
                cv2.CAP_PROP_CONTRAST, self.contrast_slider.value(), "contrast"
            )
        )  # Update contrast property when the slider value changes

        # Create a horizontal layout for the slider and its reset button
        self.contrast_slider_hbox = QHBoxLayout()

        # Create a reset button for the contrast slider
        self.contrast_slider_reset_button = QPushButton("Reset")
        self.contrast_slider_reset_button.setMaximumWidth(50)  # Limit the button width
        self.contrast_slider_reset_button.clicked.connect(
            lambda: self.reset_property(
                cv2.CAP_PROP_CONTRAST, "camera_contrast_standard", "contrast"
            )
        )  # Reset contrast property to its default value

        # Add the slider and reset button to the horizontal layout
        self.contrast_slider_hbox.addWidget(self.contrast_slider)
        self.contrast_slider_hbox.addWidget(self.contrast_slider_reset_button)

        # Add the horizontal layout to the vertical layout of the group box
        self.contrast_slider_vbox.addLayout(self.contrast_slider_hbox)

        # Create a label to display the current contrast value
        self.value_contrast_slider_label = QLabel()
        self.value_contrast_slider_label.setAlignment(
            Qt.AlignLeft
        )  # Align text to the left
        self.value_contrast_slider_label.setText(
            f"Contrast: {config['camera_contrast_used']}"
        )  # Set initial label text with contrast value

        # Add the contrast value label to the vertical layout
        self.contrast_slider_vbox.addWidget(self.value_contrast_slider_label)

        # Add a box to change the Saturation
        self.saturation_slider_groupbox = QGroupBox("Change Saturation")
        self.saturation_slider_groupbox.setCheckable(False)
        self.saturation_slider_groupbox.setDisabled(True)
        self.saturation_slider_groupbox.setMaximumWidth(200)

        # Add the saturation group box to the options layout
        self.options_groupbox.addWidget(self.saturation_slider_groupbox)

        # Create a vertical layout for the saturation group box
        self.saturation_slider_vbox = QVBoxLayout(self.saturation_slider_groupbox)
        self.saturation_slider_groupbox.setLayout(self.saturation_slider_vbox)

        # Create the saturation slider
        self.saturation_slider = QSlider(Qt.Horizontal)
        self.saturation_slider.setMinimum(config["camera_saturation_min"])
        self.saturation_slider.setMaximum(config["camera_saturation_max"])
        self.saturation_slider.setTickInterval(1)
        self.saturation_slider.setValue(config["camera_saturation_used"])
        self.saturation_slider.setMaximumWidth(200)
        self.saturation_slider.valueChanged.connect(
            lambda: self.change_property(
                cv2.CAP_PROP_SATURATION, self.saturation_slider.value(), "saturation"
            )
        )

        # Create a horizontal layout for the slider and its reset button
        self.saturation_slider_hbox = QHBoxLayout()

        # Create a reset button for the saturation slider
        self.saturation_slider_reset_button = QPushButton("Reset")
        self.saturation_slider_reset_button.setMaximumWidth(50)
        self.saturation_slider_reset_button.clicked.connect(
            lambda: self.reset_property(
                cv2.CAP_PROP_SATURATION, "camera_saturation_standard", "saturation"
            )
        )

        # Add the slider and reset button to the horizontal layout
        self.saturation_slider_hbox.addWidget(self.saturation_slider)
        self.saturation_slider_hbox.addWidget(self.saturation_slider_reset_button)

        # Add the horizontal layout to the vertical layout of the group box
        self.saturation_slider_vbox.addLayout(self.saturation_slider_hbox)

        # Create a label to display the current saturation value
        self.value_saturation_slider_label = QLabel()
        self.value_saturation_slider_label.setAlignment(Qt.AlignLeft)
        self.value_saturation_slider_label.setText(
            f"Saturation: {config['camera_saturation_used']}"
        )

        # Add the saturation value label to the vertical layout
        self.saturation_slider_vbox.addWidget(self.value_saturation_slider_label)

        # Add a box to change the Hue
        self.hue_slider_groupbox = QGroupBox("Change hue")
        self.hue_slider_groupbox.setCheckable(False)
        self.hue_slider_groupbox.setDisabled(True)
        self.hue_slider_groupbox.setMaximumWidth(200)

        # Add the hue group box to the options layout
        self.options_groupbox.addWidget(self.hue_slider_groupbox)

        # Create a vertical layout for the hue group box
        self.hue_slider_vbox = QVBoxLayout(self.hue_slider_groupbox)
        self.hue_slider_groupbox.setLayout(self.hue_slider_vbox)

        # Create the hue slider
        self.hue_slider = QSlider(Qt.Horizontal)
        self.hue_slider.setMinimum(config["camera_hue_min"])
        self.hue_slider.setMaximum(config["camera_hue_max"])
        self.hue_slider.setTickInterval(1)
        self.hue_slider.setValue(config["camera_hue_used"])
        self.hue_slider.setMaximumWidth(200)
        self.hue_slider.valueChanged.connect(
            lambda: self.change_property(
                cv2.CAP_PROP_HUE, self.hue_slider.value(), "hue"
            )
        )

        # Create a horizontal layout for the slider and its reset button
        self.hue_slider_hbox = QHBoxLayout()

        # Create a reset button for the hue slider
        self.hue_slider_reset_button = QPushButton("Reset")
        self.hue_slider_reset_button.setMaximumWidth(50)
        self.hue_slider_reset_button.clicked.connect(
            lambda: self.reset_property(cv2.CAP_PROP_HUE, "camera_hue_standard", "hue")
        )

        # Add the slider and reset button to the horizontal layout
        self.hue_slider_hbox.addWidget(self.hue_slider)
        self.hue_slider_hbox.addWidget(self.hue_slider_reset_button)

        # Add the horizontal layout to the vertical layout of the group box
        self.hue_slider_vbox.addLayout(self.hue_slider_hbox)

        # Create a label to display the current hue value
        self.value_hue_slider_label = QLabel()
        self.value_hue_slider_label.setAlignment(Qt.AlignLeft)
        self.value_hue_slider_label.setText(f"Hue: {config['camera_hue_used']}")

        # Add the hue value label to the vertical layout
        self.hue_slider_vbox.addWidget(self.value_hue_slider_label)

        # Add a box to change the image resolution
        self.shown_image_size_groupbox = QGroupBox("Change Image Resolution")
        self.shown_image_size_groupbox.setCheckable(
            False
        )  # Disable checkbox functionality for the group box
        self.shown_image_size_groupbox.setDisabled(
            True
        )  # Disable the group box by default
        self.options_groupbox.addWidget(
            self.shown_image_size_groupbox
        )  # Add the group box to the options layout
        self.shown_image_size_groupbox.toggled.connect(
            self.color_space_checkbox_toggled
        )  # Connect toggle event to a handler

        # Create a vertical layout for the resolution options within the group box
        self.shown_image_size_vbox = QVBoxLayout(self.shown_image_size_groupbox)
        self.shown_image_size_groupbox.setLayout(self.shown_image_size_vbox)

        # Add a radio button for fitting resolution
        self.fitting_resolution_radiobutton = QRadioButton("Fitting Resolution")
        self.fitting_resolution_radiobutton.setChecked(
            True
        )  # Set as the default selected option
        self.shown_image_size_vbox.addWidget(
            self.fitting_resolution_radiobutton
        )  # Add to the vertical layout

        # Add a radio button for full resolution
        self.full_resolution_radiobutton = QRadioButton("Full Resolution")
        self.shown_image_size_vbox.addWidget(
            self.full_resolution_radiobutton
        )  # Add to the vertical layout

        # Connect the toggling of the resolution radio buttons to their handler methods
        self.fitting_resolution_radiobutton.toggled.connect(
            self.shown_image_radiobuttons_toggled
        )
        self.full_resolution_radiobutton.toggled.connect(
            self.shown_image_radiobuttons_toggled
        )

        # Add a box to configure a threshold
        self.threshold_groupbox = QGroupBox("Add Threshold")
        self.threshold_groupbox.setCheckable(
            True
        )  # Allow toggling of the threshold group box
        self.threshold_groupbox.setChecked(False)  # Initially unchecked
        self.threshold_groupbox.setDisabled(True)  # Disable the group box by default
        self.threshold_groupbox.setMaximumWidth(200)  # Limit the group box width
        self.threshold_groupbox.toggled.connect(
            self.threshold_checkbox_toggled
        )  # Connect toggle event to a handler

        # Add the threshold group box to the options layout
        self.options_groupbox.addWidget(self.threshold_groupbox)

        # Create a vertical layout for the threshold controls within the group box
        self.threshold_vbox = QVBoxLayout(self.threshold_groupbox)
        self.threshold_groupbox.setLayout(self.threshold_vbox)

        # Add a slider to adjust the threshold value
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setMinimum(0)  # Set minimum value
        self.threshold_slider.setMaximum(255)  # Set maximum value
        self.threshold_slider.setTickInterval(1)  # Set the slider step size
        self.threshold_slider.setValue(128)  # Set initial value
        self.threshold_slider.setMaximumWidth(200)  # Limit the slider width
        self.threshold_slider.valueChanged.connect(
            self.change_slider_value
        )  # Connect value change to a handler
        self.threshold_vbox.addWidget(self.threshold_slider)

        # Add a label to display the current threshold value
        self.value_threshold_label = QLabel()
        self.value_threshold_label.setAlignment(
            Qt.AlignCenter
        )  # Center-align the label text
        self.threshold_vbox.addWidget(self.value_threshold_label)
        self.value_threshold_label.setText(
            f"Threshold: 128"
        )  # Set initial text for the label
        self.value_threshold = 128  # Set the initial threshold value

        # Add a box to change the color space
        self.colorspace_groupbox = QGroupBox("Change Color Space")
        self.colorspace_groupbox.setCheckable(
            True
        )  # Allow toggling of the color space group box
        self.colorspace_groupbox.setChecked(False)  # Initially unchecked
        self.colorspace_groupbox.setDisabled(True)  # Disable the group box by default
        self.options_groupbox.addWidget(
            self.colorspace_groupbox
        )  # Add the group box to the options layout
        self.colorspace_groupbox.toggled.connect(
            self.color_space_checkbox_toggled
        )  # Connect toggle event to a handler

        # Create a vertical layout for the color space options
        self.colorspace_vbox = QVBoxLayout(self.colorspace_groupbox)
        self.colorspace_groupbox.setLayout(self.colorspace_vbox)

        # Add a radio button for "Color" mode
        self.color_radiobutton = QRadioButton("Color")
        self.color_radiobutton.setChecked(True)  # Set as the default selected option
        self.colorspace_vbox.addWidget(
            self.color_radiobutton
        )  # Add to the vertical layout

        # Add a radio button for "Greyscale" mode
        self.greyscale_radiobutton = QRadioButton("Greyscale")
        self.colorspace_vbox.addWidget(
            self.greyscale_radiobutton
        )  # Add to the vertical layout

        # Connect the toggling of the color mode radio buttons to their handler methods
        self.color_radiobutton.toggled.connect(self.color_space_radiobuttons_toggled)
        self.greyscale_radiobutton.toggled.connect(
            self.color_space_radiobuttons_toggled
        )

        # Add a box to choose a deep learning model for predictions
        self.model_groupbox = QGroupBox("Choose Model")
        self.model_groupbox.setCheckable(
            False
        )  # Disable checkbox functionality for the group box
        self.model_groupbox.setDisabled(True)  # Disable the group box by default
        self.options_groupbox.addWidget(
            self.model_groupbox
        )  # Add the group box to the options layout

        # Create a vertical layout for the model selection dropdown
        self.model_vbox = QVBoxLayout(self.model_groupbox)
        self.model_groupbox.setLayout(self.model_vbox)

        # Add a dropdown menu to select the model
        self.model_combobox = QComboBox()
        self.model_combobox.addItems(
            ["No Model", "Blood Cell Count", "Leishmania"]
        )  # Add options to the dropdown
        self.model_vbox.addWidget(self.model_combobox)  # Add to the vertical layout
        self.model_combobox.currentTextChanged.connect(
            self.on_model_combobox_change
        )  # Connect value change to a handler

        # Add a stretch to push group boxes to the top of the options layout
        self.options_groupbox.addStretch()

        # Add the options layout to the second row of the GUI
        self.middle_GUI_layout.addLayout(self.options_groupbox)

        # Create a scrollable area to display the video feed
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(
            True
        )  # Allow resizing of the scrollable area
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )  # Show horizontal scroll bar when needed
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )  # Show vertical scroll bar when needed

        # Add a label to the scrollable area to display video frames
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)  # Center-align the video content
        self.scroll_area.setWidget(self.video_label)

        # Add the scrollable area to the second row of the GUI
        self.middle_GUI_layout.addWidget(self.scroll_area)

        # Create a vertical layout for model outputs and settings
        self.output_vgroupbox = QVBoxLayout()

        # Add a box for outputs and settings of the current model
        self.output_groupbox = QGroupBox("Model Settings")
        self.output_groupbox.setCheckable(
            False
        )  # Disable checkbox functionality for the group box
        self.output_groupbox.setFixedWidth(200)  # Fix the width of the group box
        self.output_vgroupbox.addWidget(self.output_groupbox)

        # Create a vertical layout for the content inside the model settings box
        self.output_vbox = QVBoxLayout(self.output_groupbox)
        self.output_groupbox.setLayout(self.output_vbox)

        # Add a stretch to push the model settings box to the top
        self.output_vgroupbox.addStretch()

        # Add the model output layout to the second row of the GUI
        self.middle_GUI_layout.addLayout(self.output_vgroupbox)

        # Add the complete second row to the main layout
        self.layout.addLayout(self.middle_GUI_layout)

        # Maximize the window to fit the screen
        self.showMaximized()

        # Create a worker for file dialog operations
        self.save_path_worker = FileDialogWorker()

    def start_stream(self):
        """
        Start the video stream and initialize the camera thread.

        This function starts the camera thread, enabling the live video stream
        and activating all adjustable UI elements such as sliders and group boxes.
        If the stream is already paused, it resumes streaming.
        """
        if not self.stream_running:
            # Initialize and start the camera thread
            self.camera_thread = CameraThread(self.value_threshold)
            self.camera_thread.update_image_size(
                self.scroll_area.width(), self.scroll_area.height()
            )  # Set the initial image size
            self.camera_thread.frame_ready.connect(
                self.update_image
            )  # Connect frame updates to UI
            self.camera_thread.start()  # Start the camera thread
            self.stream_running = True  # Set the stream running flag

            # Enable all UI controls related to the stream
            self.brightness_slider_groupbox.setDisabled(False)
            self.contrast_slider_groupbox.setDisabled(False)
            self.saturation_slider_groupbox.setDisabled(False)
            self.threshold_groupbox.setDisabled(False)
            self.shown_image_size_groupbox.setDisabled(False)
            self.hue_slider_groupbox.setDisabled(False)
            self.colorspace_groupbox.setDisabled(False)
            self.model_groupbox.setDisabled(False)
            self.pause_button.setDisabled(False)
            self.stop_button.setDisabled(False)
            self.snap_button.setDisabled(False)
            self.save_path_button.setDisabled(False)

        # Resume stream if it is paused
        if self.pause_button.isChecked():
            self.camera_thread.pause_stream(False)
            self.pause_button.setChecked(False)

    def pause_stream(self):
        """
        Pause or resume the video stream based on the state of the pause button.

        When the pause button is checked, the stream is paused, otherwise it resumes.
        """
        if not self.stream_running:
            # Ensure the pause button remains unchecked if the stream is not running
            self.pause_button.setChecked(False)
            return

        # Pause or resume the stream depending on the button's state
        if self.pause_button.isChecked():
            self.camera_thread.pause_stream(True)  # Pause the stream
        else:
            self.camera_thread.pause_stream(False)  # Resume the stream

    def stop_stream(self):
        """
        Stop the video stream and reset the UI components.

        This function stops the camera thread, disables all adjustable UI elements,
        and resets their state to default.
        """
        if not self.stream_running:
            return

        # Stop the camera thread
        self.camera_thread.stop()
        self.camera_thread.finished.connect(
            self.clear_label
        )  # Clear the video label on finish
        self.stream_running = False  # Reset the stream running flag

        # Disable all UI controls related to the stream
        self.brightness_slider_groupbox.setDisabled(True)
        self.contrast_slider_groupbox.setDisabled(True)
        self.saturation_slider_groupbox.setDisabled(True)
        self.threshold_groupbox.setDisabled(True)
        self.shown_image_size_groupbox.setDisabled(True)
        self.hue_slider_groupbox.setDisabled(True)
        self.colorspace_groupbox.setDisabled(True)
        self.model_groupbox.setDisabled(True)
        self.pause_button.setDisabled(True)
        self.stop_button.setDisabled(True)
        self.snap_button.setDisabled(True)
        self.save_path_button.setDisabled(True)

        # Reset UI elements to their default states
        self.fitting_resolution_radiobutton.setChecked(True)
        self.threshold_groupbox.setChecked(False)
        self.colorspace_groupbox.setChecked(False)
        self.color_radiobutton.setChecked(True)
        self.model_combobox.setCurrentText("No Model")

        # Resume the stream if it was paused when stopping
        if self.pause_button.isChecked():
            self.camera_thread.pause_stream(False)
            self.pause_button.setChecked(False)

    def clear_label(self):
        """
        Clear the video display label.

        This is typically used when the video stream is stopped.
        """
        self.video_label.clear()

    def snap_image_clicked(self):
        """
        Capture a snapshot of the current video frame.

        The snapshot functionality is only available when the stream is running.
        """
        if not self.stream_running:
            return
        self.camera_thread.snap_image_clicked()  # Trigger the snapshot functionality

    def set_save_path(self):
        """
        Open a dialog to set the save path for captured snapshots.

        This functionality is only available when the stream is running.
        """
        # if not self.stream_running:
        #    return
        self.save_path_worker.start()  # Start the file dialog worker

    def shown_image_radiobuttons_toggled(self):
        """
        Handle toggling between "Fitting Resolution" and "Full Resolution" modes.

        Updates the camera thread to change the resolution mode based on the selected radio button.
        """
        if self.fitting_resolution_radiobutton.isChecked():
            self.camera_thread.change_to_full_resolution_image(
                False
            )  # Set to fitting resolution
        elif self.full_resolution_radiobutton.isChecked():
            self.camera_thread.change_to_full_resolution_image(
                True
            )  # Set to full resolution

    def update_image(self, q_image, fps):
        """
        Update the displayed video frame and FPS information.

        Parameters:
            q_image (QImage): The image to display in the QLabel.
            fps (float): The current frames per second.
        """
        # Convert QImage to QPixmap and update the QLabel
        pixmap = QPixmap.fromImage(q_image)
        self.video_label.setPixmap(pixmap)

        # Update the FPS label with the current value
        self.fps_label.setText(f"FPS: {fps:.2f}")

    def threshold_checkbox_toggled(self):
        """
        Enable or disable the threshold feature.

        This toggles the threshold functionality in the camera thread and disables
        conflicting controls when the threshold feature is active.
        """
        if self.stream_running:
            if self.threshold_groupbox.isChecked():
                self.camera_thread.threshold_toggled(True)  # Enable threshold mode
                self.colorspace_groupbox.setDisabled(
                    True
                )  # Disable color space controls
                self.model_groupbox.setDisabled(True)  # Disable model selection
            else:
                self.camera_thread.threshold_toggled(False)  # Disable threshold mode
                self.colorspace_groupbox.setDisabled(False)
                self.model_groupbox.setDisabled(False)

    def change_slider_value(self, value):
        """
        Update the threshold value based on the slider's position.

        Parameters:
            value (int): The new threshold value.
        """
        self.value_threshold = value  # Update the internal threshold value
        self.value_threshold_label.setText(f"Threshold: {value}")  # Update the label
        self.camera_thread.set_threshold(
            value
        )  # Update the camera thread with the new value

    def color_space_checkbox_toggled(self):
        """
        Enable or disable the color space feature.

        This toggles the color space functionality in the camera thread and disables
        conflicting controls when the color space feature is active.
        """
        if self.stream_running:
            if self.colorspace_groupbox.isChecked():
                self.camera_thread.color_space_toggled(True)  # Enable color space mode
                self.threshold_groupbox.setDisabled(True)  # Disable threshold controls
                self.model_groupbox.setDisabled(True)  # Disable model selection
            else:
                self.camera_thread.color_space_toggled(
                    False
                )  # Disable color space mode
                self.threshold_groupbox.setDisabled(False)
                self.model_groupbox.setDisabled(False)

    def color_space_radiobuttons_toggled(self):
        """
        Handle toggling between "Color" and "Greyscale" modes.

        Updates the camera thread with the selected color space mode.
        """
        if self.color_radiobutton.isChecked():
            self.camera_thread.choose_color_space(0)  # Set to color mode
        elif self.greyscale_radiobutton.isChecked():
            self.camera_thread.choose_color_space(1)  # Set to greyscale mode

    def change_property(self, property, input_field, slider):
        """
        Update a camera property to a new value based on user input.

        Parameters:
            property: The camera property to change (e.g., brightness, contrast).
            input_field: The new value for the property.
            slider: The associated slider label to update.
        """
        # Set the camera property to the specified value
        self.camera_thread.set_property(property, float(input_field))
        # Update the corresponding slider label with the new value
        self.update_property_label(slider)

    def reset_property(self, property, property_in_config, slider):
        """
        Reset a camera property to its default value from the configuration.

        Parameters:
            property: The camera property to reset (e.g., brightness, contrast).
            property_in_config: The corresponding key in the configuration dictionary.
            slider: The associated slider label to update.
        """
        # Reset the property value to the default configuration value
        self.camera_thread.set_property(property, float(config[property_in_config]))

        # Update the slider and label for the specified property
        if slider == "brightness":
            self.brightness_slider.setValue(config["camera_brightness_standard"])
            self.update_property_label(slider)
        elif slider == "contrast":
            self.contrast_slider.setValue(config["camera_contrast_standard"])
            self.update_property_label(slider)
        elif slider == "saturation":
            self.saturation_slider.setValue(config["camera_saturation_standard"])
            self.update_property_label(slider)
        elif slider == "hue":
            self.hue_slider.setValue(config["camera_hue_standard"])
            self.update_property_label(slider)

    def update_property_label(self, slider):
        """
        Update the label for a specific camera property slider.

        Parameters:
            slider: The name of the slider whose label needs updating.
        """
        if slider == "brightness":
            self.value_brightness_slider_label.setText(
                f"Brightness: {self.brightness_slider.value()}"
            )
        elif slider == "contrast":
            self.value_contrast_slider_label.setText(
                f"Contrast: {self.contrast_slider.value()}"
            )
        elif slider == "saturation":
            self.value_saturation_slider_label.setText(
                f"Saturation: {self.saturation_slider.value()}"
            )
        elif slider == "hue":
            self.value_hue_slider_label.setText(f"Hue: {self.hue_slider.value()}")

    def closeEvent(self, event):
        """
        Handle the event when the main window is closed.

        Stops the camera thread if the stream is running and waits for the thread to terminate.

        Parameters:
            event: The close event object.
        """
        if self.stream_running:
            self.camera_thread.stop()  # Stop the camera thread
            self.camera_thread.finished.connect(
                QApplication.quit
            )  # Quit the application after the thread stops
            self.camera_thread.wait()  # Wait for the thread to finish
        event.accept()  # Accept the close event

    def on_model_combobox_change(self, model):
        """
        Handle the event when the model is changed via the combo box.

        Configures the camera thread and UI based on the selected model.

        Parameters:
            model: The selected model name from the combo box.
        """

        def update_blood_cell_count(RBC, WBC, PLT):
            """
            Update the labels for blood cell count predictions.

            Parameters:
                RBC: Red Blood Cell count.
                WBC: White Blood Cell count.
                PLT: Platelet count.
            """
            if hasattr(self, "RBC_output_label") and self.RBC_output_label is not None:
                self.RBC_output_label.setText(f"RBC: {RBC}")
            if hasattr(self, "WBC_output_label") and self.WBC_output_label is not None:
                self.WBC_output_label.setText(f"WBC: {WBC}")
            if hasattr(self, "PLT_output_label") and self.PLT_output_label is not None:
                self.PLT_output_label.setText(f"PLT: {PLT}")

        if self.stream_running:
            if model == "No Model":
                self.reset_model()
                self.camera_thread.chosen_model("No Model")
                self.threshold_groupbox.setDisabled(False)
                self.colorspace_groupbox.setDisabled(False)
            elif model == "Blood Cell Count":
                self.reset_model()
                activate_blood_cell_output(
                    self
                )  # Enable specific output UI for blood cell count
                self.camera_thread.send_count_update.connect(update_blood_cell_count)
                self.camera_thread.chosen_model("Blood Cell Count")
                self.threshold_groupbox.setDisabled(True)
                self.colorspace_groupbox.setDisabled(True)
            elif model == "Leishmania":
                self.reset_model()
                self.camera_thread.chosen_model("Leishmania")
                self.threshold_groupbox.setDisabled(True)
                self.colorspace_groupbox.setDisabled(True)

    def reset_model(self):
        """
        Reset the model output layout by clearing all widgets and settings.

        Ensures that the output layout is empty and UI elements are reset.
        """
        layout = self.output_groupbox.layout()

        if layout is not None:
            # Remove all widgets in the layout
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                elif item.layout() is not None:
                    self.clear_layout(item.layout())

            # Recursively clear nested layouts
            self.clear_layout(layout)

        # Reset model-specific label attributes to avoid invalid references
        self.RBC_output_label = None
        self.WBC_output_label = None
        self.PLT_output_label = None

    def clear_layout(self, layout):
        """
        Recursively clear a layout and delete all widgets within it.

        Parameters:
            layout: The layout to clear.
        """
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def resizeEvent(self, event):
        """
        Handle the event when the main window is resized.

        Updates the camera thread with the new video display area size.

        Parameters:
            event: The resize event object.
        """
        if self.stream_running:
            # Update the camera thread with the new dimensions
            self.camera_thread.update_image_size(
                self.scroll_area.width(), self.scroll_area.height()
            )

        # Call the parent class's resize event handler
        super().resizeEvent(event)

    def open_analyze_window(self):
        """
        Open the analyze window script in a new process.

        The script path is relative to the current file.
        """
        script_path = os.path.join(os.path.dirname(__file__), "analyze_window.py")
        self.analyze_process.start(
            "python",
            [script_path],
        )

    def open_snap_settings(self):
        """
        Open the Snap Settings window.

        This window allows the user to configure image cropping and other settings.
        """
        self.snap_settings_w = SnapSettings()
        self.snap_settings_w.show()

    def open_settings(self):
        """
        Open the Settings window.

        This window allows the user to adjust application-wide settings.
        """
        self.settings_w = Settings()
        self.settings_w.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(QIcon(os.path.join(main_path, "window_icon.png")))
    window = VideoStream()
    window.show()
    sys.exit(app.exec_())
