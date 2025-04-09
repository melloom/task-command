"""
Build Script for Task Master Pro

This script creates standalone executables for Windows, macOS, and Linux
using PyInstaller.

Usage:
    python build_app.py
"""

import os
import platform
import subprocess
import sys
import shutil
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import PyInstaller
        print("PyInstaller is already installed.")
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller installed successfully.")

    return True

def build_app():
    """Build standalone executable for the current platform"""
    # First check dependencies
    check_dependencies()

    print(f"Building Task Master Pro for {platform.system()}...")

    # Create build directory
    build_dir = Path("build")
    dist_dir = Path("dist")

    if not build_dir.exists():
        build_dir.mkdir()
    if not dist_dir.exists():
        dist_dir.mkdir()

    # Check for resources
    resources_dir = Path("resources")
    if not resources_dir.exists() or not any(resources_dir.iterdir()):
        print("Warning: Resources directory is empty or doesn't exist.")
        print("Icons may not be included in the final package.")

    # App name
    app_name = "TaskMasterPro"

    # Entry point
    entry_point = Path("main.py")

    # Options
    options = [
        f"--name={app_name}",
        "--clean",
        "--noconfirm",
        "--onefile",  # Create a single executable
        "--windowed",  # Don't show console window
    ]

    # Platform-specific options
    if platform.system() == "Windows":
        icon_path = resources_dir / "icon.ico"
        if icon_path.exists():
            options.append(f"--icon={icon_path}")

        options.append("--add-data=LICENSE;.")

    elif platform.system() == "Darwin":  # macOS
        icon_path = resources_dir / "icon.icns"
        if icon_path.exists():
            options.append(f"--icon={icon_path}")

        # macOS specific options
        options.extend([
            "--add-data=LICENSE:.",
            "--osx-bundle-identifier=com.melvinperalta.taskmanager"
        ])

    else:  # Linux
        icon_path = resources_dir / "icon.png"
        if icon_path.exists():
            options.append(f"--icon={icon_path}")

        options.append("--add-data=LICENSE:.")

    # Build command
    cmd = [sys.executable, "-m", "PyInstaller"] + options + [str(entry_point)]

    # Run PyInstaller
    try:
        print("Running build command:", " ".join(cmd))
        subprocess.check_call(cmd)
        print(f"Build completed successfully! Output in {dist_dir}")

        # Show additional information
        if platform.system() == "Windows":
            print(f"Executable: {dist_dir}/{app_name}.exe")
        elif platform.system() == "Darwin":
            print(f"Application: {dist_dir}/{app_name}.app")
        else:
            print(f"Executable: {dist_dir}/{app_name}")

        return True
    except subprocess.CalledProcessError as e:
        print(f"Error building app: {e}")
        return False

if __name__ == "__main__":
    # Parse command-line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print(__doc__)
        sys.exit(0)

    # Run the build process
    success = build_app()

    if success:
        print("Build process completed successfully!")
    else:
        print("Build process failed.")
        sys.exit(1)
