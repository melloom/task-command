"""
Delete task command for Task Manager
"""

from task_manager.utils.storage import load_tasks, save_tasks

def delete_task(task_id):
    """Delete a task"""
    tasks = load_tasks()

    # Find the task with matching ID
    for i, task in enumerate(tasks):
        if task.id == task_id:
            # Remove the task
            del tasks[i]

            # Save the updated tasks
            save_tasks(tasks)
            return True

    # Task not found
    raise ValueError(f"Task with ID {task_id} not found")