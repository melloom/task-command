# README.md

# Task Manager

A versatile task management application with both graphical and command-line interfaces.

## Features

- Simple and intuitive interface
- Task prioritization (High, Medium, Low)
- Task categorization
- Due date tracking and reminders
- Progress tracking
- Filtering and searching
- Auto-save functionality
- Customizable appearance
- Import/export capabilities
- Task templates
- Interactive CLI

## Installation

### Method 1: Direct Installation

```bash
# Install the package
pip install -e .
```

## Usage

### GUI Interface

```bash
# Launch the GUI
task-manager
# or
task-gui
```

### Command Line Interface

```bash
# Launch the CLI menu
task-cli

# Or use command-line arguments:
task-cli add "New task description"
task-cli list
task-cli complete 1
task-cli delete 1
```

### From Python Code

```python
# Launch GUI
from task_manager import launch_gui
launch_gui()

# Use CLI functions
from task_manager.commands.add import add_task
from task_manager.commands.list import list_tasks
from task_manager.commands.complete import complete_task
from task_manager.commands.delete import delete_task

add_task("New task")
list_tasks()
complete_task(1)
delete_task(1)
```

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only the standard library)

## License

MIT