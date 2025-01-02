import os
import sys

# Suppress OpenCV logging messages
os.environ["OPENCV_LOG_LEVEL"] = "SILENT"
import cv2
import ruamel.yaml


def create_config_yaml(file_path, config_variables):
    """
    Creates a YAML configuration file with the provided settings.

    Args:
        file_path (str): The path where the configuration file will be saved.
        config_variables (dict): A dictionary containing configuration settings
                                 such as camera resolutions, brightness, contrast, etc.

    Returns:
        None
    """
    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True

    # Dynamically generate the camera resolutions section
    camera_resolutions = "\n".join(
        f"- {resolution}" for resolution in config_variables["camera_resolutions"]
    )

    # Create the YAML configuration template
    config_template = f"""version: {config_variables['version']}

# Camera Settings
camera_nr: {config_variables['camera_nr']}
camera_resolutions:
{camera_resolutions}
used_camera_resolution: {config_variables['used_camera_resolution']}
camera_brightness_min: {config_variables['camera_brightness_min']}
camera_brightness_max: {config_variables['camera_brightness_max']}
camera_brightness_standard: {config_variables['camera_brightness_standard']}
camera_brightness_used: {config_variables['camera_brightness_used']}
camera_contrast_min: {config_variables['camera_contrast_min']}
camera_contrast_max: {config_variables['camera_contrast_max']}
camera_contrast_standard: {config_variables['camera_contrast_standard']}
camera_contrast_used: {config_variables['camera_contrast_used']}
camera_saturation_min: {config_variables['camera_saturation_min']}
camera_saturation_max: {config_variables['camera_saturation_max']}
camera_saturation_standard: {config_variables['camera_saturation_standard']}
camera_saturation_used: {config_variables['camera_saturation_used']}
camera_hue_min: {config_variables['camera_hue_min']}
camera_hue_max: {config_variables['camera_hue_max']}
camera_hue_standard: {config_variables['camera_hue_standard']}
camera_hue_used: {config_variables['camera_hue_used']}

# Snap Image Settings
change_scaling: {str(config_variables['change_scaling']).lower()}
crop_or_resize: {config_variables['crop_or_resize']}
scaling_width: {config_variables['scaling_width']}
scaling_height: {config_variables['scaling_height']}
save_path: '{config_variables['save_path']}'

# Yolact Parameters
yolact_config: {config_variables['yolact_config']}
yolact_weights: 
  {config_variables['yolact_weights']}

# Yolo Parameters
yolo_weights: 
  {config_variables['yolo_weights']}
"""

    # Write the generated configuration to a file
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(config_template)


def checkPorts(num_ports=10):
    """
    Checks for available camera ports by attempting to open each port.

    Args:
        num_ports (int): The number of camera ports to check.

    Returns:
        list: A list of available camera ports.
    """
    available_ports = []
    for port in range(num_ports):
        cap = cv2.VideoCapture(port)
        if cap.isOpened():
            available_ports.append(port)
        cap.release()
    return available_ports


def test_camera_settings(port):
    """
    Tests and retrieves the adjustable settings for a camera.

    Args:
        port (int): The camera port to test.

    Returns:
        tuple: A dictionary of default settings and a dictionary of adjustable ranges.
    """
    cap = cv2.VideoCapture(port)

    # Default camera settings
    default_list = {
        "Brightness": cap.get(cv2.CAP_PROP_BRIGHTNESS),
        "Contrast": cap.get(cv2.CAP_PROP_CONTRAST),
        "Saturation": cap.get(cv2.CAP_PROP_SATURATION),
        "Hue": cap.get(cv2.CAP_PROP_HUE),
    }

    # Initialize lists for adjustable ranges
    properties_list = {
        "Brightness": [],
        "Contrast": [],
        "Saturation": [],
        "Hue": [],
    }

    properties = [
        cv2.CAP_PROP_BRIGHTNESS,
        cv2.CAP_PROP_CONTRAST,
        cv2.CAP_PROP_SATURATION,
        cv2.CAP_PROP_HUE,
    ]
    if not cap.isOpened():
        print("Error opening the camera")
    else:
        # Test each property within a specified range
        for value in range(-1000, 1000):
            for property in properties:
                cap.set(property, value)
                actual_property = cap.get(property)
                if int(actual_property) == value:
                    if properties[0] == property:
                        properties_list["Brightness"].append(value)
                    elif properties[1] == property:
                        properties_list["Contrast"].append(value)
                    elif properties[2] == property:
                        properties_list["Saturation"].append(value)
                    elif properties[3] == property:
                        properties_list["Hue"].append(value)

    # Restore default settings
    for i in range(len(default_list)):
        cap.set(properties[i], list(default_list.values())[i])

    cap.release()

    return default_list, properties_list


def resolution_test(port):
    """
    Tests the supported resolutions of a camera.

    Args:
        port (int): The camera port to test.

    Returns:
        list: A list of supported resolutions.
    """
    cap = cv2.VideoCapture(port)

    if not cap.isOpened():
        print("Error opening the camera")
    else:
        # List of common resolutions to test
        common_resolutions = [
            (320, 200),
            (320, 240),
            (340, 256),
            (480, 320),
            (640, 480),
            (648, 486),
            (680, 512),
            (720, 480),
            (720, 576),
            (800, 480),
            (800, 600),
            (854, 480),
            (1024, 600),
            (1024, 768),
            (1136, 768),
            (1280, 720),
            (1280, 800),
            (1280, 960),
            (1280, 1024),
            (1296, 972),
            (1360, 1024),
            (1400, 1050),
            (1440, 900),
            (1440, 960),
            (1440, 1080),
            (1600, 1200),
            (1680, 1050),
            (1920, 1080),
            (1920, 1200),
            (2048, 1080),
            (2048, 1536),
            (2560, 1440),
            (2560, 2048),
            (2592, 1944),
            (3840, 2160),
        ]

        supported_resolutions = []

        for resolution in common_resolutions:
            width, height = resolution
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            if int(actual_width) == width and int(actual_height) == height:
                supported_resolutions.append([int(actual_width), int(actual_height)])

    cap.release()

    return supported_resolutions


# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    # Check available camera ports
    ports = checkPorts()
    if len(ports) > 1:
        print(
            f"{len(ports)} cameras were found. Please enter a number from 1-{len(ports)} to select the camera for which the configuration should be carried out."
        )
        while True:
            user_input = input("Camera number: ")
            try:
                used_port = int(user_input)
                if 1 <= used_port <= len(ports):
                    used_port -= 1
                    break
                else:
                    print(f"Please enter a number between 1 and {len(ports)}.")
            except ValueError:
                print("This is not a valid number. Please try again.")
    elif len(ports) == 0:
        sys.exit(
            "Creation of the configuration file canceled because no cameras were found."
        )
    else:
        used_port = 0

    # Test camera settings
    default_list, properties_list = test_camera_settings(used_port)

    # Test supported resolutions
    resolutions = resolution_test(used_port)
    if len(resolutions) == 0:
        sys.exit(
            "Creation of the configuration file aborted as no suitable resolutions were found."
        )

    # Prepare configuration variables
    config_variables = {
        "version": 1.0,
        "camera_nr": used_port,
        "camera_resolutions": resolutions,
        "used_camera_resolution": 0,
        "camera_brightness_min": int(
            f"{(min(properties_list[list(properties_list.keys())[0]]))}"
        ),
        "camera_brightness_max": int(
            f"{(max(properties_list[list(properties_list.keys())[0]]))}"
        ),
        "camera_brightness_standard": int(
            float(f"{default_list[list(default_list.keys())[0]]}")
        ),
        "camera_brightness_used": int(
            float(f"{default_list[list(default_list.keys())[0]]}")
        ),
        "camera_contrast_min": int(
            f"{(min(properties_list[list(properties_list.keys())[1]]))}"
        ),
        "camera_contrast_max": int(
            f"{(max(properties_list[list(properties_list.keys())[1]]))}"
        ),
        "camera_contrast_standard": int(
            float(f"{default_list[list(default_list.keys())[1]]}")
        ),
        "camera_contrast_used": int(
            float(f"{default_list[list(default_list.keys())[1]]}")
        ),
        "camera_saturation_min": int(
            f"{(min(properties_list[list(properties_list.keys())[2]]))}"
        ),
        "camera_saturation_max": int(
            f"{(max(properties_list[list(properties_list.keys())[2]]))}"
        ),
        "camera_saturation_standard": int(
            float(f"{default_list[list(default_list.keys())[2]]}")
        ),
        "camera_saturation_used": int(
            float(f"{default_list[list(default_list.keys())[2]]}")
        ),
        "camera_hue_min": int(
            f"{(min(properties_list[list(properties_list.keys())[3]]))}"
        ),
        "camera_hue_max": int(
            f"{(max(properties_list[list(properties_list.keys())[3]]))}"
        ),
        "camera_hue_standard": int(
            float(f"{default_list[list(default_list.keys())[3]]}")
        ),
        "camera_hue_used": int(float(f"{default_list[list(default_list.keys())[3]]}")),
        "change_scaling": False,
        "crop_or_resize": "crop",
        "scaling_width": resolutions[0][0],
        "scaling_height": resolutions[0][1],
        "save_path": f"{script_dir}\\snapped_images",
        "yolact_config": "yolact_resnet101_blood_config",
        "yolact_weights": f"{script_dir}\\weights\\yolact_resnet101_blood_6399_96000.pth",
        "yolo_weights": f"{script_dir}\\weights\\leishmania_finetuning.pt",
    }

    # Create the configuration YAML
    file_path = f"{script_dir}\\config.yml"
    create_config_yaml(file_path, config_variables)
    print(f"The configuration file was successfully created.")
