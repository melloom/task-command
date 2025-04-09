"""
Storage utilities for Task Manager
"""

import os
import json
import pickle
import shutil
from datetime import datetime
import platform

def get_storage_directory():
    """Get platform-specific storage directory for task manager data"""
    system = platform.system()
    home_dir = os.path.expanduser("~")

    if system == "Windows":
        return os.path.join(os.getenv("APPDATA"), "TaskManager")
    elif system == "Darwin":  # macOS
        return os.path.join(home_dir, "Library", "Application Support", "TaskManager")
    else:  # Linux and others
        return os.path.join(home_dir, ".taskmanager")

def get_tasks_file_path():
    """Get path to the tasks data file"""
    storage_dir = get_storage_directory()
    return os.path.join(storage_dir, "tasks.pickle")

def save_tasks(tasks):
    """Save tasks to pickle file"""
    tasks_path = get_tasks_file_path()

    # Ensure directory exists
    os.makedirs(os.path.dirname(tasks_path), exist_ok=True)

    with open(tasks_path, 'wb') as f:
        pickle.dump(tasks, f)

    return True

def save_with_recovery(tasks):
    """Save tasks with backup recovery"""
    tasks_path = get_tasks_file_path()
    backup_path = tasks_path + ".bak"

    # Ensure directory exists
    os.makedirs(os.path.dirname(tasks_path), exist_ok=True)

    # If tasks file exists, create a backup
    if os.path.exists(tasks_path):
        try:
            shutil.copy2(tasks_path, backup_path)
        except Exception as e:
            print(f"Warning: Failed to create backup: {e}")

    # Save the new data
    try:
        with open(tasks_path, 'wb') as f:
            pickle.dump(tasks, f)
        return True
    except Exception as e:
        print(f"Error saving tasks: {e}")

        # Try to restore from backup
        if os.path.exists(backup_path):
            try:
                shutil.copy2(backup_path, tasks_path)
                print("Restored from backup")
            except Exception as restore_error:
                print(f"Failed to restore from backup: {restore_error}")

        return False

def load_tasks():
    """Load tasks from pickle file, return empty list if file doesn't exist"""
    tasks_path = get_tasks_file_path()

    if not os.path.exists(tasks_path):
        return []

    try:
        with open(tasks_path, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        print(f"Error loading tasks: {e}")

        # Try to load from backup
        backup_path = tasks_path + ".bak"
        if os.path.exists(backup_path):
            try:
                with open(backup_path, 'rb') as f:
                    tasks = pickle.load(f)
                print("Loaded from backup")
                return tasks
            except Exception as backup_error:
                print(f"Failed to load from backup: {backup_error}")

        return []