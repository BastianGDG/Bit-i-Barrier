@echo off
:: Gather all requirements from requirements.txt
if exist requirements.txt (
    echo Installing requirements...
    pip install -r requirements.txt
) else (
    echo requirements.txt not found. Skipping installation.
)

:: Run the Python script to_csv.py
if exist package/ui.py (
    echo Running to_package.py...
    python package/ui.py
) else (
    echo ui.py not found. Exiting.
)