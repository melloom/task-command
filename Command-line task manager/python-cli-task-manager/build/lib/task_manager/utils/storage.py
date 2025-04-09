import json
import os
from task_manager.models.task import Task

storage_file_path = os.path.join(os.path.dirname(__file__), 'tasks.json')

def load_tasks():
    if not os.path.exists(storage_file_path):
        return []
    with open(storage_file_path, 'r') as file:
        tasks_data = json.load(file)
        return [Task(**task) for task in tasks_data]

def save_tasks(tasks):
    with open(storage_file_path, 'w') as file:
        json.dump([task.__dict__ for task in tasks], file, indent=2)