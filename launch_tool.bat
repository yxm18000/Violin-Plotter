@echo off
chcp 65001 > nul

REM --- Navigate to the script's directory ---
cd /d "%~dp0"

echo.
echo ====================================
echo   Violin Plotter GUI Launch Script
echo ====================================
echo.

REM --- Check and create virtual environment ---
IF NOT EXIST venv (
    echo Virtual environment "venv" not found. Creating it...
    python -m venv venv
    IF %ERRORLEVEL% NEQ 0 (
        echo.
        echo Error: Failed to create virtual environment.
        echo Please ensure Python is installed and added to your system PATH.
        echo.
        pause
        EXIT /B 1
    )
    echo Virtual environment "venv" created successfully.
    echo.
)

REM --- Activate virtual environment ---
call venv\Scripts\activate.bat
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Failed to activate virtual environment.
    echo.
    pause
    EXIT /B 1
)
echo Virtual environment activated.
echo.

REM --- Install or update required Python libraries ---
REM Upgrade pip to the latest version
echo Upgrading pip to the latest version...
pip install --upgrade pip
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Failed to upgrade pip.
    echo.
    pause
    EXIT /B 1
)
echo pip upgrade complete.
echo.

REM Install required libraries (skipped if already installed)
echo Installing or updating required libraries (pandas, matplotlib, seaborn)...
pip install pandas matplotlib seaborn
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Failed to install required libraries.
    echo Please check your internet connection.
    echo.
    pause
    EXIT /B 1
)
echo Required libraries installed successfully.
echo.

REM --- Execute the Python script ---
echo Starting the application...
echo.

python violin_plot_gui.py

REM --- Post-application execution cleanup ---
echo.
echo Application finished.
echo This window will close automatically...

REM Wait a bit before closing the window (optional)
ping 127.0.0.1 -n 3 > nul
EXIT /B 0