"""
Task Manager Main Entry Point

This script provides a unified entry point for the application.
By default, it will launch the GUI interface.
"""

import sys
import argparse
import importlib.util
import subprocess

def check_dependency(module_name):
    """Check if a Python module is installed"""
    return importlib.util.find_spec(module_name) is not None

def install_dependency(package_name):
    """Install a Python package using pip"""
    print(f"Installing {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    parser = argparse.ArgumentParser(description='Task Manager')
    parser.add_argument('--cli', action='store_true', help='Launch command-line interface instead of GUI')
    parser.add_argument('--simple-gui', action='store_true', help='Launch simple GUI using standard tkinter')
    parser.add_argument('--install-deps', action='store_true', help='Install missing dependencies automatically')
    parser.add_argument('--reset-settings', action='store_true', help='Reset all settings to defaults')
    args = parser.parse_args()

    if args.reset_settings:
        try:
            from task_manager.gui import DEFAULT_SETTINGS, save_settings
            save_settings(DEFAULT_SETTINGS)
            print("Settings reset to defaults.")
        except ImportError:
            print("Could not reset settings.")

    if args.cli:
        # Launch CLI version
        from task_manager.main import main as cli_main
        cli_main()
        return

    # Check for advanced GUI dependencies
    has_customtkinter = check_dependency('customtkinter')
    has_pillow = check_dependency('PIL')
    has_ttkthemes = check_dependency('ttkthemes')

    missing_deps = []
    if not has_customtkinter:
        missing_deps.append('customtkinter')
    if not has_pillow:
        missing_deps.append('Pillow')
    if not has_ttkthemes:
        missing_deps.append('ttkthemes')

    # If dependencies are missing and user wants to install them
    if missing_deps and args.install_deps:
        for dep in missing_deps:
            if install_dependency(dep):
                print(f"Successfully installed {dep}")
            else:
                print(f"Failed to install {dep}")

        # Recheck after installation
        has_customtkinter = check_dependency('customtkinter')
        has_pillow = check_dependency('PIL')
        has_ttkthemes = check_dependency('ttkthemes')

    # Use simple GUI if advanced dependencies are missing or simple GUI is requested
    if args.simple_gui or not all([has_customtkinter, has_pillow, has_ttkthemes]):
        if missing_deps:
            print(f"Missing dependencies for advanced GUI: {', '.join(missing_deps)}")
            print("Launching simple GUI instead. Use --install-deps to install required packages.")

        # Launch simple GUI version
        from task_manager.gui import launch_simple_gui
        launch_simple_gui()
    else:
        # Try to launch advanced GUI
        try:
            from task_manager.gui import launch_gui
            launch_gui()
        except ImportError as e:
            # Check if we need to fall back due to missing imports for interactive features
            print(f"Error loading advanced GUI: {e}")
            print("Falling back to simple GUI.")

            try:
                from task_manager.gui import launch_simple_gui
                launch_simple_gui()
            except ImportError:
                print("Error: Could not load GUI. Falling back to CLI mode.")
                from task_manager.main import main as cli_main
                cli_main()

if __name__ == "__main__":
    main()
