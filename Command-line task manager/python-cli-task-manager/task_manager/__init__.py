# FILE: __init__.py

"""Task Manager - A simple command-line and GUI task management tool

This package provides a simple task management system with both
command line and graphical user interfaces. It supports task reminders
and is compatible with Windows, macOS, and Linux.
"""

from task_manager.gui import launch_simple_gui as launch_gui

__version__ = '1.0.0'  # Update this when making new releases
__author__ = 'Your Name'  # Replace with your actual name

# Define public API
__all__ = ['launch_gui']