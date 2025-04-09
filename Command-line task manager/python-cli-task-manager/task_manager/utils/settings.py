"""
Settings module for Task Manager
"""

import json
import os
from task_manager.utils.storage import get_storage_directory

# Default settings
DEFAULT_SETTINGS = {
    'colors': {
        'high_priority': '#FF4444',  # Red
        'medium_priority': '#4444FF',  # Blue
        'low_priority': '#44AA44',    # Green
        'completed': '#888888',       # Gray
        'default': '#000000'          # Black
    },
    'autosave': {
        'enabled': True,
        'interval': 120,  # in seconds (2 minutes)
        'on_exit': True
    },
    'notifications': {
        'enabled': True,
        'sound': True,
        'advance_warning': 15  # minutes
    },
    'ui': {
        'theme': 'system',  # system, light, dark
        'font_family': 'Helvetica',
        'font_size': 10,
        'compact_view': False,
        'show_status_bar': True
    },
    'cli': {
        'interactive_mode': True,  # Default to interactive mode
        'show_colors': True,       # Use color output when available
        'compact_view': False      # Use detailed output by default
    }
}

def get_settings_file_path():
    """Get the path to the settings file"""
    storage_dir = get_storage_directory()
    return os.path.join(storage_dir, "settings.json")

def load_settings():
    """Load settings from file, using defaults for missing values"""
    try:
        settings_path = get_settings_file_path()

        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                saved_settings = json.load(f)

            # Merge with defaults, keeping saved values
            settings = DEFAULT_SETTINGS.copy()

            # Deep merge - handle nested dictionaries
            for key, value in saved_settings.items():
                if key in settings and isinstance(settings[key], dict) and isinstance(value, dict):
                    settings[key].update(value)
                else:
                    settings[key] = value

            return settings
        else:
            # Create the default settings file if it doesn't exist
            save_settings(DEFAULT_SETTINGS)
            return DEFAULT_SETTINGS.copy()

    except Exception as e:
        print(f"Error loading settings: {e}")
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """Save settings to file"""
    try:
        settings_path = get_settings_file_path()

        # Ensure directory exists
        os.makedirs(os.path.dirname(settings_path), exist_ok=True)

        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False

def get_color(priority, settings=None):
    """Get color for a priority level"""
    if settings is None:
        settings = load_settings()

    color_key = f'{priority.lower()}_priority'
    return settings['colors'].get(color_key, DEFAULT_SETTINGS['colors'].get(color_key, '#000000'))

def toggle_interactive_mode():
    """Toggle interactive mode setting and return new state"""
    settings = load_settings()

    # Make sure the CLI settings section exists
    if 'cli' not in settings:
        settings['cli'] = DEFAULT_SETTINGS['cli'].copy()

    # Toggle the value
    current_mode = settings['cli'].get('interactive_mode', True)
    settings['cli']['interactive_mode'] = not current_mode

    # Save the updated settings
    save_settings(settings)

    # Return the new mode
    return settings['cli']['interactive_mode']