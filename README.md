# Decision-support system for live detection of Leishmania parasites from microscopic images with Deep Learning

Key Features:
- Real-time prediction of leishmania parasites
- Intuitive user interface for easy use

![GUI exmaple](./GUI_example_video2.gif)

## Installing / Getting started

A quick introduction of the minimal setup you need to get the livestream running.

Download and install miniconda
https://docs.anaconda.com/miniconda/
```shell
conda create --name leishmania python=3.8
```
```shell
conda activate leishmania
```
```shell
conda install pytorch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 pytorch-cuda=12.1 -c pytorch -c nvidia
```
Test if PyTorch has been installed correctly
```shell
python
```
```shell
import torch
```
```shell
torch.cuda.is_available()
```
Output should be True
```shell
exit()
```
```shell
pip install cython==3.0.10 matplotlib opencv-python pillow==6.2.2 numpy==1.23.1 PyQt5==5.15.10 pycocotools==2.0.7 ultralytics==8.2.76 ruamel.yaml==0.18.6
```
```shell
cd path_to_MicroPredictor_folder
```
Under Windows, you can have the configuration file created automatically.
```shell
python create_config.py
```
```shell
python livestream.py
```

## Developing

### Built With
- Python 3.8
- PyTorch 2.1.0
- Torchaudio 2.1.0
- Torchvision 0.16.0
- Cuda 12.1
- NumPy 1.23.1
- Cython 3.0.10
- Pillow 6.2.2
- PyQt5 5.15.10
- pycocotools 2.0.7
- Ultralytics 8.2.76
- ruamel.yaml 0.18.6

<!---
### Setting up Dev

Here's a brief intro about what a developer must do in order to start developing
the project further:

```shell
git clone https://github.com/your/your-project.git
cd your-project/
packagemanager install
```

And state what happens step-by-step. If there is any virtual environment, local server or database feeder needed, explain here.

### Building

If your project needs some additional steps for the developer to build the
project after some code changes, state them here. for example:

```shell
./configure
make
make install
```

Here again you should state what actually happens when the code above gets
executed.

### Deploying / Publishing
give instructions on how to build and release a new version
In case there's some step you have to take that publishes this project to a
server, this is the right time to state it.

```shell
packagemanager deploy your-project -s server.com -u username -p password
```

And again you'd need to tell what the previous code actually does.

## Versioning

We can maybe use [SemVer](http://semver.org/) for versioning. For the versions available, see the [link to tags on this repository](/tags).
-->

## Configuration

Below you can see what a configuration file should look like. If create_config.py does not work for you, you can create the file manually and fill it out with the help of cameratest.ipynb.
```shell
version: 1.0

# Camera Settings
camera_nr: 0
camera_resolutions:
- [648, 486]
- [1296, 972]
- [2592, 1944]
used_camera_resolution: 2
camera_brightness_min: -64
camera_brightness_max: 64
camera_brightness_standard: 0
camera_brightness_used: 0
camera_contrast_min: -100
camera_contrast_max: 100
camera_contrast_standard: 0
camera_contrast_used: 0
camera_saturation_min: 0
camera_saturation_max: 255
camera_saturation_standard: 128
camera_saturation_used: 128
camera_hue_min: -180
camera_hue_max: 180
camera_hue_standard: 0
camera_hue_used: 0

# Snap Image Settings
change_scaling: false
crop_or_resize: crop
scaling_width: 648
scaling_height: 486
save_path: 'd:\Leischmanien\MicroPredictor-main\MicroPredictor\snapped_images'

# Yolact Parameters
yolact_config: yolact_resnet101_blood_config
yolact_weights: 
  path\to\folder\weights\yolact_resnet101_blood_6399_96000.pth

# Yolo Parameters
yolo_weights: 
  path\to\folder\weights\leishmania_finetuning.pt
```

<!---
## Tests

Describe and show how to run the tests with code examples.
Explain what these tests test and why.

```shell
Give an example
```

## Style guide

Explain your code style and show how to check it.

## Api Reference

If the api is external, link to api documentation. If not describe your api including authentication methods as well as explaining all the endpoints with their required parameters.


## Database

Explaining what database (and version) has been used. Provide download links.
Documents your database design and schemas, relations etc... 

## Licensing

State what the license is and how to find the text version of the license.
-->
