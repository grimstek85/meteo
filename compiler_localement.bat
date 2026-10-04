@echo off
setlocal
python -m pip install --upgrade pyinstaller
python -m PyInstaller --noconfirm --clean --onefile --windowed --name "MeteoLocale" meteo_widget.py
echo.
echo EXE cree dans le dossier dist\MeteoLocale.exe
pause
