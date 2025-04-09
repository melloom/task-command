def delete_task(task_id: int) -> None:
    from task_manager.utils.storage import load_tasks, save_tasks

    tasks = load_tasks()
    tasks = [task for task in tasks if task.id != task_id]

    save_tasks(tasks)