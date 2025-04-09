"""
Add task command for Task Manager
"""

from task_manager.utils.storage import load_tasks, save_tasks
from task_manager.models.task import Task

def add_task(description, priority=None, due_date=None, category=None):
    """Add a new task to the task list"""
    # Load existing tasks
    tasks = load_tasks()

    # Create task ID (max ID + 1 or 1 if no tasks)
    task_id = 1 if not tasks else max(task.id for task in tasks) + 1

    # Create new task
    task = Task(task_id=task_id, description=description)

    # Set optional properties
    if priority:
        task.priority = priority

    if due_date:
        task.due_date = due_date

    if category:
        task.category = category

    # Add to task list
    tasks.append(task)

    # Save tasks
    save_tasks(tasks)

    return task