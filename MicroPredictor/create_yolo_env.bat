@echo off
setlocal

REM ===== Einstellungen =====
set "ENV_NAME=yolo-gpu"
set "PY_VER=3.10"
REM =========================

echo ==^> Erstelle neue Umgebung "%ENV_NAME%" mit Python %PY_VER% ...
conda create -y -n "%ENV_NAME%" python=%PY_VER%
if errorlevel 1 goto :err

echo ==^> Installiere PyTorch 2.1.0 + Torchvision 0.16.0 + Torchaudio 2.1.0 + CUDA 12.1 in %ENV_NAME% ...
conda install -y -n "%ENV_NAME%" -c pytorch -c nvidia ^
  pytorch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 pytorch-cuda=12.1
if errorlevel 1 goto :err

echo ==^> Upgrade pip in %ENV_NAME% ...
conda run -n "%ENV_NAME%" python -m pip install --upgrade pip
if errorlevel 1 goto :err

echo ==^> Installiere PyQt5, Ultralytics, ruamel.yaml, OpenCV in %ENV_NAME% ...
conda run -n "%ENV_NAME%" python -m pip install ^
  PyQt5==5.15.10 ultralytics==8.2.76 ruamel.yaml==0.18.6 opencv-python
if errorlevel 1 goto :err

echo.
echo ==^> Fertig! Umgebung "%ENV_NAME%" ist installiert.
echo Zum Verwenden im Terminal:
echo     conda activate %ENV_NAME%
echo.
exit /b 0

:err
echo.
echo [FEHLER] Installation abgebrochen. Siehe Meldungen oben.
exit /b 1
