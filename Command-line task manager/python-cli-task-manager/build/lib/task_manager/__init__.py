# FILE: __init__.py

"""Task Manager Package

This package provides a simple task management system with both
command line and graphical user interfaces.
"""

from task_manager.gui import launch_gui

__version__ = '0.1.0'
__all__ = ['launch_gui']