# Windows Build Guide

This guide explains how to manually build the SecureWipe desktop application into a standalone Windows executable (.exe).

## Prerequisites

-   Windows 10 or 11
-   Python 3.9, 3.10, or 3.11 installed (Python 3.11 is recommended)
-   `pip` (Python package manager)

## 1. Setup Environment

It is recommended to use a virtual environment to avoid conflicts.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

## 2. Install Dependencies

Install the required Python packages from the `requirements.txt` file.

```powershell
pip install -r requirements.txt
```

## 3. Install PyInstaller

PyInstaller is the tool used to package the Python script and its dependencies into a single executable.

```powershell
pip install pyinstaller
```

## 4. Build the Executable

Run the following PyInstaller command from the root of the SecureWipe project directory. This command includes all necessary hidden imports for UI libraries and cryptography modules.

```powershell
pyinstaller --onefile --windowed --name SecureWipePortable --add-data "src;src" --add-data "requirements.txt;." --hidden-import tkinter --hidden-import tkinter.ttk --hidden-import tkinter.filedialog --hidden-import tkinter.messagebox --hidden-import tkinter.simpledialog --hidden-import customtkinter --hidden-import PIL --hidden-import PIL._tkinter_finder --hidden-import reportlab --hidden-import qrcode --hidden-import cryptography --hidden-import psutil --hidden-import openai --clean secure_wipe_portable.py
```

**Flag Explanations:**
- `--onefile`: Packages everything into a single `.exe` file.
- `--windowed`: Prevents the command prompt console from appearing when the app runs.
- `--name`: Sets the output filename.
- `--add-data`: Includes necessary data folders and files.
- `--hidden-import`: Forces PyInstaller to include libraries it might not automatically detect.
- `--clean`: Cleans PyInstaller cache and temporary files before building.

## 5. Testing the Executable

After the build completes successfully, the executable will be located in the `dist/` directory.

1.  Navigate to the `dist/` folder.
2.  Double-click `SecureWipePortable.exe` to run the application.
3.  Verify that the UI loads and functions correctly.

## Known Issues and Troubleshooting

-   **Missing Modules:** If the application fails to start and you see errors regarding missing modules (e.g., in Windows Event Viewer if `--windowed` is used), you may need to add additional `--hidden-import <module_name>` flags to the build command.
-   **Antivirus False Positives:** PyInstaller executables are sometimes flagged as false positives by antivirus software. If this occurs, you may need to add an exclusion for the build directory or sign the executable with a code signing certificate.
