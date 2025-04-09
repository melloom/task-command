"""
Complete task command for Task Manager
"""

from task_manager.utils.storage import load_tasks, save_tasks

def complete_task(task_id):
    """Mark a task as complete"""
    tasks = load_tasks()

    # Find the task with matching ID
    for task in tasks:
        if task.id == task_id:
            # Mark as complete and set progress to 100%
            task.completed = True
            if hasattr(task, 'progress'):
                task.progress = 100

            # Save the updated tasks
            save_tasks(tasks)
            return True

    # Task not found
    raise ValueError(f"Task with ID {task_id} not found")