# Installation Instructions

## Basic Installation

```bash
# Navigate to the project directory
cd "/Users/melvinperalta/Desktop/Command-line task manager/python-cli-task-manager"

# Install required dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Running the Application

After installation, you can run:

```bash
# Run directly with Python
python main.py

# Or use the entry points
task-manager  # GUI version
task-cli      # CLI version
```

## Troubleshooting

If you encounter issues with the advanced GUI:

1. Make sure all dependencies are installed:
   ```bash
   pip install customtkinter Pillow ttkthemes
   ```

2. If you still have issues, try the fallback GUI:
   ```bash
   python main.py --simple-gui
   ```

3. Or use the command-line interface:
   ```bash
   python main.py --cli
   ```
