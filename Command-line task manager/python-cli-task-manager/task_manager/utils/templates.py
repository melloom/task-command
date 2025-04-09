"""
Task templates functionality for Task Manager
"""

import os
import json
import re
from task_manager.utils.storage import get_storage_directory
from task_manager.models.task import Task

def get_templates_directory():
    """Get the directory where templates are stored"""
    storage_dir = get_storage_directory()
    templates_dir = os.path.join(storage_dir, "templates")

    # Ensure templates directory exists
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir, exist_ok=True)

    return templates_dir

def get_template_file_path(template_name):
    """Get file path for a specific template"""
    templates_dir = get_templates_directory()
    safe_name = re.sub(r'[^\w\-\.]', '_', template_name)
    return os.path.join(templates_dir, f"{safe_name}.json")

def load_templates():
    """Load all available templates"""
    templates = {}
    templates_dir = get_templates_directory()

    if not os.path.exists(templates_dir):
        return templates

    for filename in os.listdir(templates_dir):
        if filename.endswith('.json'):
            try:
                template_path = os.path.join(templates_dir, filename)
                template_name = os.path.splitext(filename)[0]

                with open(template_path, 'r') as f:
                    template_data = json.load(f)

                    # Convert underscores back to spaces for display
                    display_name = template_name.replace('_', ' ')
                    templates[display_name] = template_data
            except Exception as e:
                print(f"Error loading template {filename}: {e}")

    return templates

def save_template(template_name, template_data):
    """Save a template to a file"""
    template_path = get_template_file_path(template_name)

    with open(template_path, 'w') as f:
        json.dump(template_data, f, indent=2)

def delete_template(template_name):
    """Delete a template file"""
    template_path = get_template_file_path(template_name)

    if os.path.exists(template_path):
        os.remove(template_path)
    else:
        raise FileNotFoundError(f"Template '{template_name}' not found")

def create_task_from_template(template_name, placeholder_values):
    """Create a task from a template, filling in placeholders"""
    templates = load_templates()

    if template_name not in templates:
        raise ValueError(f"Template '{template_name}' not found")

    template = templates[template_name]
    task_data = {}

    # Fill in placeholders in all string fields
    for key, value in template.items():
        if isinstance(value, str):
            # Replace all {placeholder} with values
            for placeholder, replacement in placeholder_values.items():
                pattern = r'\{' + re.escape(placeholder) + r'\}'
                value = re.sub(pattern, replacement, value)

            task_data[key] = value
        else:
            # Non-string values are copied directly
            task_data[key] = value

    return task_data
