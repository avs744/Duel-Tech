@echo off
echo Setting up and running DuelTech application...

REM Check if virtual environment exists, create if not
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt

REM Run the application
echo Starting the application...
python run_app.py

REM Deactivate virtual environment on exit
call venv\Scripts\deactivate.bat
