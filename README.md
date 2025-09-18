# Decision-support system for live detection of Leishmania parasites from microscopic images with Deep Learning

Key Features:
- Real-time prediction of leishmania parasites
- Intuitive user interface for easy use

![GUI exmaple](GUI_example_video2.gif)

## Setup Guide (Windows only)

*A complete step-by-step installation guide (Windows edition).*

---

### 0) What you need
- **Windows PC**
- **Internet connection** and about **5–10 GB free disk space**
- An **NVIDIA GPU** is optional (project will also run on CPU, just slower)

---

### 1) Install Miniconda
1. Download Miniconda for Windows here:  
   👉 https://docs.anaconda.com/miniconda/
2. Run the installer and just click **Next** (default options are fine).
3. After installation, close all windows and open the **Anaconda Prompt** (search for it in the Start menu).

---

### 2) Go to the project folder
In the **Anaconda Prompt**, go to the folder where this project is located (the same folder where the file `environment.yml` is stored).

Example (adjust the path to where you saved the project):

```powershell
cd "C:\Users\YourName\Downloads\MicroPredictor"
```

💡 Tip: In Windows Explorer, you can **Shift + Right Click → Copy as path**, then paste it after `cd`.

---

### 3) Create the environment from `environment.yml`
Run this command inside the project folder:

```powershell
conda env create -f environment.yml
```

This installs everything needed. ⏳ It can take a few minutes.

---

### 4) Activate the environment
The environment name is defined inside `environment.yml`.  
For this project, it is **`leishmania`**.

Activate it with:

```powershell
conda activate leishmania
```

Now you should see `(leishmania)` at the beginning of the line in your Anaconda Prompt.

---

### 5) Test the installation
Check if everything works by running:

```powershell
python -c "import torch, cv2; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('OpenCV version:', cv2.__version__)"
```

- If you see **`CUDA available: True`** → your NVIDIA GPU will be used.  
- If you see **`False`** → the project will still run, but only on CPU (slower).

---

### 6) Run the project
Still inside the project folder:

1. Create the configuration file automatically (only needed once):
   ```powershell
   python create_config.py
   ```

2. Start the livestream:
   ```powershell
   python livestream.py
   ```

---

### 7) Everyday usage
Whenever you want to use the project again:

```powershell
conda activate leishmania
cd "C:\Users\YourName\Downloads\MicroPredictor"
python livestream.py
```

---

### Troubleshooting (Windows)
- **`conda` not recognized**  
  → You are not in the Anaconda Prompt. Close everything and open the **Anaconda Prompt** again.

- **`ModuleNotFoundError` (e.g. torch, cv2, PyQt5)**  
  → You forgot to activate the environment. Run `conda activate leishmania`.

- **Wrong folder**  
  → Make sure you are in the folder where `environment.yml` is located. Use `dir` to list files.

- **`CUDA available: False` but you have a GPU**  
  → Update your NVIDIA drivers. Otherwise, the project will run on CPU.

---

Done! You now have everything set up on Windows.  
Remember: **1) Open Anaconda Prompt → 2) Activate environment → 3) Go to project folder → 4) Run livestream.**

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
