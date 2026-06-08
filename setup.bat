@echo off
setlocal

cd /d "%~dp0"

echo Installation des dependances...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo Erreur pendant l'installation des dependances.
    pause
    exit /b 1
)

echo.
echo Lancement de l'application...
python main.py
if errorlevel 1 (
    echo.
    echo Erreur pendant le lancement de l'application.
    pause
    exit /b 1
)

endlocal
