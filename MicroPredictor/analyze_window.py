import sys

from PyQt5.QtCore import QProcess, QSize, Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from models import analyze_leishmania


class CalculationThread(QThread):
    """
    A QThread subclass to handle analysis of images or videos in a separate thread.
    """

    # Signal to update the progress in the main thread
    progress_updated = pyqtSignal(int)

    def __init__(self, files, is_image, save_path):
        """
        Initialize the CalculationThread.

        Parameters:
            files (list): List of file paths to analyze.
            is_image (bool): True if files are images, False if they are videos.
            save_path (str): Path to save analysis results.
        """
        super().__init__()
        self.files = files
        self.is_image = is_image
        self.save_path = save_path

    def run(self):
        """
        Perform the analysis on the given files.

        Emits progress updates as the files are processed.
        """
        total_files = len(self.files)  # Total number of files to process
        for i, file_path in enumerate(self.files, start=1):
            # Analyze the file based on whether it's an image or video
            analyze_leishmania(self, file_path, self.is_image, self.save_path)
            # Emit progress as a percentage
            self.progress_updated.emit(int((i / total_files) * 100))


class analyze_window(QWidget):
    """
    A QWidget subclass for the Analyze Image/Video window.

    Allows users to select a model, choose files, set save paths, and start analysis.
    """

    def __init__(self):
        """
        Initialize the analyze window and set up the UI.
        """
        super().__init__()

        # Set window title
        self.setWindowTitle("Analyze Image/Video")

        # Main layout
        layout = QVBoxLayout()

        # GroupBox for model selection
        self.model_groupbox = QGroupBox("Choose Model")
        self.model_groupbox.setCheckable(False)
        layout.addWidget(self.model_groupbox)

        # Layout for model selection
        self.model_vbox = QVBoxLayout(self.model_groupbox)
        self.model_groupbox.setLayout(self.model_vbox)

        # ComboBox for selecting a model
        self.model_combobox = QComboBox()
        self.model_combobox.addItems(["No Model", "Blood Cell Count", "Leishmania"])
        self.model_vbox.addWidget(self.model_combobox)
        self.model_combobox.currentTextChanged.connect(self.on_model_combobox_change)
        self.choosed_model = "no_model"  # Default model

        # GroupBox for selecting between image and video
        self.image_or_video_groupbox = QGroupBox("Image or Video")
        self.image_or_video_groupbox.setCheckable(False)
        self.image_or_video_groupbox.setDisabled(True)  # Disabled by default
        self.image_or_video_groupbox.setFixedWidth(350)
        layout.addWidget(self.image_or_video_groupbox)

        # Vertical layout within the GroupBox
        self.image_or_video_vbox = QVBoxLayout()
        self.image_or_video_groupbox.setLayout(self.image_or_video_vbox)

        # Horizontal layout for radio buttons
        self.image_or_video_hbox = QHBoxLayout()
        self.image_or_video_vbox.addLayout(self.image_or_video_hbox)

        # RadioButton for selecting "Image"
        self.image_radiobutton = QRadioButton("Image")
        self.image_radiobutton.setChecked(True)  # Default selection
        self.image_radiobutton.toggled.connect(self.update_format_label)
        self.image_or_video_hbox.addWidget(self.image_radiobutton)

        # RadioButton for selecting "Video"
        self.video_radiobutton = QRadioButton("Video")
        self.video_radiobutton.toggled.connect(self.update_format_label)
        self.image_or_video_hbox.addWidget(self.video_radiobutton)

        # Add spacing to align the radio buttons
        self.image_or_video_hbox.addStretch()

        # Label to display supported file formats
        self.format_label = QLabel("Formats:")
        self.image_or_video_vbox.addWidget(self.format_label)

        # Horizontal layout for file selection
        self.choose_file_hbox = QHBoxLayout()
        layout.addLayout(self.choose_file_hbox)

        # Button to choose files
        self.choose_file_button = QPushButton("Choose Files")
        self.choose_file_button.setFixedWidth(100)
        self.choose_file_button.clicked.connect(self.choose_files)
        self.choose_file_button.setDisabled(True)  # Disabled by default
        self.choose_file_hbox.addWidget(self.choose_file_button)

        # Label to display the number of selected files
        self.choose_files_label = QLabel("")
        self.choose_file_hbox.addWidget(self.choose_files_label)

        # Add spacing to align elements
        self.choose_file_hbox.addStretch()

        # Horizontal layout for setting save path
        self.save_path_hbox = QHBoxLayout()
        layout.addLayout(self.save_path_hbox)

        # Button to set save path
        self.set_save_path_button = QPushButton("Set Save Path")
        self.set_save_path_button.setMaximumWidth(100)
        self.set_save_path_button.clicked.connect(self.set_save_path)
        self.set_save_path_button.setDisabled(True)  # Disabled by default
        self.save_path_hbox.addWidget(self.set_save_path_button)

        # Label to display the save path
        self.save_path_label = QLabel("")
        self.save_path_hbox.addWidget(self.save_path_label)

        # Add spacing to align elements
        self.save_path_hbox.addStretch()

        # Start button to begin the analysis
        self.start_button = QPushButton("Start")
        self.start_button.setMaximumWidth(100)
        self.start_button.clicked.connect(self.start)
        self.start_button.setDisabled(True)  # Disabled by default
        layout.addWidget(self.start_button)

        # Progress bar to show the progress of the analysis
        self.prediction_progress_bar = QProgressBar()
        self.prediction_progress_bar.setFixedWidth(350)
        layout.addWidget(self.prediction_progress_bar)

        # Close button to exit the application
        self.close_button = QPushButton("Close")
        self.close_button.setMaximumWidth(100)
        self.close_button.clicked.connect(self.close)
        self.close_button.setDisabled(True)  # Disabled by default
        layout.addWidget(self.close_button)

        # Add stretch to push elements to the top
        layout.addStretch()

        # Set the main layout for the widget
        self.setLayout(layout)

    def update_format_label(self):
        """
        Update the format label based on the selected model and input type.
        """
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
        """
        Handle model selection changes and update the UI accordingly.
        """
        if self.model_combobox.currentText() == "No Model":
            self.format_label.setText("Formats:")
            self.image_or_video_groupbox.setDisabled(True)
            self.choose_file_button.setDisabled(True)
            self.deactivate_old()
        elif self.model_combobox.currentText() == "Blood Cell Count":
            self.format_label.setText("Formats:")
            self.image_or_video_groupbox.setDisabled(True)
            self.choose_file_button.setDisabled(True)
            self.deactivate_old()

            # Inform the user that the feature is not implemented
            not_implemented_reminder = QMessageBox()
            not_implemented_reminder.setWindowTitle("Not Implemented")
            not_implemented_reminder.setText(
                "The analysis of blood cells has not yet been implemented."
            )
            not_implemented_reminder.setIcon(QMessageBox.Information)
            not_implemented_reminder.setStandardButtons(QMessageBox.Ok)
            not_implemented_reminder.exec_()
        elif self.model_combobox.currentText() == "Leishmania":
            self.image_or_video_groupbox.setDisabled(False)
            self.video_radiobutton.setDisabled(False)
            self.update_format_label()
            self.choose_file_button.setDisabled(False)
            self.deactivate_old()

    def deactivate_old(self):
        """
        Reset the UI to its initial state.
        """
        self.set_save_path_button.setDisabled(True)
        self.start_button.setDisabled(True)
        self.files = []
        self.save_path = ""

    def choose_files(self):
        """
        Open a file dialog for selecting images or videos based on the selected model.

        Updates the UI to show the number of selected files and enables the save path button.
        """
        try:
            # Determine the file filter based on the input type (image or video)
            filter_type = ""
            if self.image_radiobutton.isChecked():
                filter_type = "Images (*.bmp *.dng *.jpeg *.jpg *.mpo *.png *.tif *.tiff *.webp *.pfm)"
            elif self.video_radiobutton.isChecked():
                filter_type = "Video (*.asf *.avi *.gif *.m4v *.mkv *.mov *.mp4 *.mpeg *.mpg *.ts *.wmv *.webm)"

            # Open a file dialog to select files
            files, _ = QFileDialog.getOpenFileNames(
                self,
                "Choose Files",
                filter=filter_type,
            )

            # If no files were selected, exit the method
            if not files:
                return

            # Update the file list and label to show the number of selected files
            self.files = files
            self.choose_files_label.setText(
                f"\u2714   {len(self.files)} files selected!"
            )
            # Enable the save path button
            self.set_save_path_button.setDisabled(False)

        except Exception as e:
            print(f"Error while choosing files: {e}")

    def set_save_path(self):
        """
        Open a file dialog to set the save path for analyzed results.

        Updates the UI to enable the start button and show the selected path.
        """
        try:
            # Open a dialog to select the save directory
            save_path = QFileDialog.getExistingDirectory(self, "Select Save Path")

            # If no directory was selected, exit the method
            if not save_path:
                return

            # Update the save path and enable the start button
            self.save_path = save_path
            self.start_button.setDisabled(False)
            self.save_path_label.setText(f"\u2714")

        except Exception as e:
            print(f"Error while setting save path: {e}")

    def start(self):
        """
        Start the analysis process by initializing the CalculationThread.

        Disables UI controls and updates the progress bar during the analysis.
        """
        # Reset the progress bar
        self.prediction_progress_bar.setValue(0)

        # Disable UI controls while the analysis is running
        self.model_groupbox.setDisabled(True)
        self.image_or_video_groupbox.setDisabled(True)
        self.choose_file_button.setDisabled(True)
        self.set_save_path_button.setDisabled(True)
        self.start_button.setDisabled(True)

        # Determine whether the input is an image or video
        is_image = self.image_radiobutton.isChecked()

        # Initialize the calculation thread
        self.calculation_thread = CalculationThread(
            self.files, is_image, self.save_path
        )
        # Connect signals for progress updates and thread completion
        self.calculation_thread.progress_updated.connect(self.update_progress)
        self.calculation_thread.finished.connect(self.on_thread_finished)
        # Start the thread
        self.calculation_thread.start()

    def update_progress(self, value):
        """
        Update the progress bar based on the current progress.

        Parameters:
            value (int): The progress percentage (0-100).
        """
        self.prediction_progress_bar.setValue(value)

    def on_thread_finished(self):
        """
        Handle the completion of the analysis process.

        Enables the close button to allow the user to exit the application.
        """
        self.close_button.setDisabled(False)


if __name__ == "__main__":
    """
    Entry point for the application.

    Initializes the QApplication and opens the Analyze Window.
    """
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = analyze_window()
    window.show()
    sys.exit(app.exec_())
