"""
Import and export utilities for Task Manager
"""

import json
import csv
import os
from task_manager.models.task import Task

def export_to_json(tasks, file_path):
    """Export tasks to a JSON file"""
    # Convert tasks to dictionaries
    task_dicts = []
    for task in tasks:
        task_dict = task.__dict__.copy()
        task_dicts.append(task_dict)

    with open(file_path, 'w') as f:
        json.dump(task_dicts, f, indent=2)

def import_from_json(file_path):
    """Import tasks from a JSON file"""
    with open(file_path, 'r') as f:
        task_dicts = json.load(f)

    tasks = []
    for task_dict in task_dicts:
        # Create Task object
        task_id = task_dict.pop('id')
        description = task_dict.pop('description')
        completed = task_dict.pop('completed', False)
        created_at = task_dict.pop('created_at', None)

        task = Task(task_id=task_id, description=description,
                   completed=completed, created_at=created_at)

        # Set all remaining attributes
        for key, value in task_dict.items():
            setattr(task, key, value)

        tasks.append(task)

    return tasks

def export_to_csv(tasks, file_path):
    """Export tasks to a CSV file"""
    # Define CSV headers
    headers = ['id', 'description', 'completed', 'priority',
              'due_date', 'category', 'progress', 'created_at']

    with open(file_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()

        for task in tasks:
            # Extract needed attributes from the task
            row = {
                'id': task.id,
                'description': task.description,
                'completed': task.completed,
                'priority': getattr(task, 'priority', 'Medium'),
                'due_date': getattr(task, 'due_date', ''),
                'category': getattr(task, 'category', ''),
                'progress': getattr(task, 'progress', 0),
                'created_at': getattr(task, 'created_at', '')
            }
            writer.writerow(row)

def import_from_csv(file_path):
    """Import tasks from a CSV file"""
    tasks = []

    with open(file_path, 'r', newline='') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Create task object
            task = Task(
                task_id=int(row['id']),
                description=row['description'],
                completed=row['completed'].lower() in ['true', 'yes', '1'],
                created_at=row['created_at']
            )

            # Set additional attributes
            if 'priority' in row and row['priority']:
                task.priority = row['priority']

            if 'due_date' in row and row['due_date']:
                task.due_date = row['due_date']

            if 'category' in row and row['category']:
                task.category = row['category']

            if 'progress' in row and row['progress']:
                try:
                    task.progress = int(row['progress'])
                except ValueError:
                    task.progress = 0

            tasks.append(task)

    return tasks
