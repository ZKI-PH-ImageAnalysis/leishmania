# Decision-support system for live detection of Leishmania parasites from microscopic images with Deep Learning

Key Features:
- Real-time prediction of leishmania parasites
- Intuitive user interface for easy use

![GUI exmaple](GUI_example.gif)

## Setup Guide (Windows only)

*A complete step-by-step installation guide (Windows edition).*

---

### What you need
- **Windows PC**
- **Internet connection** and about **5–10 GB free disk space**
- An **NVIDIA GPU** is optional (project will also run on CPU, just slower)
- A **microscope camera** connected to your PC (required for livestream)

---

### 1) Install Miniconda
1. Download Miniconda for Windows here:  
   👉 https://docs.anaconda.com/miniconda/
2. Run the installer and just click **Next** (default options are fine).
3. After installation, close all windows and open the **Anaconda Prompt** (search for it in the Start menu).

---

### 2) Download the project from GitHub
Open the **Anaconda Prompt** and run:

```powershell
cd %USERPROFILE%\Downloads
git clone https://github.com/ZKI-PH-ImageAnalysis/leishmania.git
```

This will create a folder called **Leishmania**.  
Inside it, you will find the **MicroPredictor** folder that contains all the code.

---

### 3) Go to the project folder
Now move into the project folder:

```powershell
cd "%USERPROFILE%\Downloads\Leishmania\MicroPredictor"
```

💡 Tip: If you saved the project somewhere else, adjust the path.

---

### 4) Create the environment from `environment.yml`
Run this command inside the project folder:

```powershell
conda env create -f environment.yml
```

This installs everything needed. ⏳ It can take a few minutes.

If you already created the environment before and just want to update it:

```powershell
conda env update -f environment.yml --prune
```

---

### 5) Activate the environment
The environment name is defined inside `environment.yml`.  
For this project, it is usually **`leishmania`**.

Activate it with:

```powershell
conda activate leishmania
```

Now you should see `(leishmania)` at the beginning of the line in your Anaconda Prompt.

---

### 6) Test the installation
Check if everything works by running:

```powershell
python -c "import torch; print('CUDA available:', torch.cuda.is_available())
```

- If you see **`CUDA available: True`** → your NVIDIA GPU will be used.  
- If you see **`False`** → the project will still run, but only on CPU (slower).

---

### 7) Run the project
Make sure you are still in the project folder:

```powershell
cd "%USERPROFILE%\Downloads\Leishmania\MicroPredictor"
```

⚠️ **Important:** Ensure that your microscope camera is connected to your PC **before** creating the config file.

1. Create the configuration file automatically (only needed once):
   ```powershell
   python create_config.py
   ```

2. Start the livestream:
   ```powershell
   python livestream.py
   ```

---

### 8) Everyday usage
Whenever you want to use the project again:

```powershell
conda activate leishmania
cd "%USERPROFILE%\Downloads\Leishmania\MicroPredictor"
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

- **Camera not working**  
  → Double-check that your microscope camera is plugged in **before** running `create_config.py`. If not, close everything, connect the camera, and run the command again.

---

✅ Done! You now have everything set up on Windows.  
Remember: **1) Open Anaconda Prompt → 2) Activate environment → 3) Go to project folder → 4) Run livestream.**
## Developing

### Built With
- Python 3.8
- PyTorch 2.1.0
- Torchaudio 2.1.0
- Torchvision 0.16.0
- Cuda 12.1
- PyQt5 5.15.10
- Ultralytics 8.2.76
- ruamel.yaml 0.18.6
- OpenCV 4.10.0

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
save_path: 'd:\Downloads\Leishmania\MicroPredictor\snapped_images'

# Yolact Parameters
yolact_config: yolact_resnet101_blood_config
yolact_weights: 
  path\to\folder\weights\yolact_resnet101_blood_6399_96000.pth

# Yolo Parameters
yolo_weights: 
  path\to\folder\weights\leishmania_finetuning.pt
```

## Dataset

**Dataset available at:** LINK EINFÜGEN

### 1. Overview  
This dataset consists of **microscopic images of Giemsa-stained skin smears** obtained from Libyan patients diagnosed with cutaneous leishmaniasis (CL).  
It is organized into two main parts:  

- **Dataset 1** → Collected with a **Keyence BZ9000E digital microscope** (lab-based).  
- **Dataset 2** → Extended dataset including **all images from Dataset 1**, plus an additional set collected with a **Bresser Erudit DLX microscope** (portable, low-cost).  

Both datasets contain paired **Images** (`.png`) and **Labels** (`.txt`), split into `train`, `val`, and `test` subsets.

---

### 2. Data Acquisition  

#### Dataset 1  
- **Patients**: 244 Libyan CL patients (confirmed by PCR at Tripoli University Hospital).  
- **Samples**: Skin lesion smears (slit-skin or touch smears).  
- **Preparation**: Air-dried, methanol-fixed, Giemsa-stained slides.  
- **Imaging Setup**:  
  - Microscope: Keyence BZ9000E (lab-grade)  
  - Magnification: 100× oil immersion objective  
  - Numerical Aperture (NA): 1.3  
  - Resolution: 0.21 μm  
- **Image Count**:  
  - 350 positive images (parasite densities: 1–100 amastigotes per image)  
  - 220 negative images (no parasites, controls)  
  - **Total: 570 images**

#### Dataset 2  
- **Patients**: Additional cohort (xx patients). **<- NOCH EINFÜGEN!!!** 
- **Samples**: Same smear preparation method.  
- **Imaging Setup**:  
  - Microscope: Bresser Erudit DLX (portable, battery-powered)  
  - Camera: BRESSER MikroCam SP 5.0  
  - Magnification: 100× oil immersion objective  
  - Numerical Aperture (NA): 1.25  
  - Resolution: 0.22 μm  
- **Image Count**:  
  - 106 positive images  
  - 58 negative images  
  - **Total: 164 images**  

👉 **Dataset 2 folder = Dataset 1 images + Dataset 2 images (extended dataset).**

---

### 3. Directory Structure
```text
Dataset_1/
│
├── Images/
│   ├── train/   # dataset_1_image_1.png ... dataset_1_image_398.png
│   ├── val/     # continues numbering from train
│   └── test/
│
├── Labels/
│   ├── train/   # dataset_1_image_1.txt ...
│   ├── val/
│   └── test/
│
Dataset_2/
│
├── Images/
│   ├── train/   # contains both dataset_1 and dataset_2 images
│   ├── val/
│   └── test/
│
├── Labels/
│   ├── train/
│   ├── val/
│   └── test/
```
- **Naming Convention**:  
  - `dataset_1_image_X.png` for Dataset 1 images  
  - `dataset_2_image_X.png` for Dataset 2 additional images  
  - Labels follow the same numbering with `.txt` extension  

- **Splits**:  
  - Train, validation, and test sets are sequential.  
  - Example: Train = images 1–398, Val = 399–…, Test = continues onward.  

---

## 4. Labels & Schema  

- **Image format**: `.png`  
- **Label format**: `.txt` (YOLO-style bounding boxes).  
- Each line = one object (parasite body).  

Format: 

- `class_id`:  
  - 0 = parasite  
- Coordinates are **normalized** by image width and height.  
- After `class_id`, the values are given in pairs:  
  `(x1 y1 x2 y2 … x4 y4)`
- Every `.png` has a corresponding `.txt` file in the same split (`train/`, `val/`, `test/`).

---

## 5. Dataset Relations  

- **Dataset 1** = base dataset (lab microscope, high-quality).  
- **Dataset 2** = superset (Dataset_1 + portable microscope data).  
- **Train/Val/Test** subsets are **disjoint** (sequential indexing prevents data leakage).  

---

## Licensing

noch einfügen
