def add_task(description: str) -> None:
    from task_manager.models.task import Task
    from task_manager.utils.storage import load_tasks, save_tasks

    tasks = load_tasks()
    task_id = len(tasks) + 1
    new_task = Task(task_id, description, False)
    tasks.append(new_task)
    save_tasks(tasks)