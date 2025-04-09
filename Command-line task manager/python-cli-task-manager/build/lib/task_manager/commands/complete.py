def complete_task(task_id: int) -> None:
    from task_manager.utils.storage import load_tasks, save_tasks
    from task_manager.models.task import Task

    tasks = load_tasks()
    for task in tasks:
        if task.id == task_id:
            task.completed = True
            save_tasks(tasks)
            print(f"Task {task_id} marked as complete.")
            return
    print(f"Task {task_id} not found.")