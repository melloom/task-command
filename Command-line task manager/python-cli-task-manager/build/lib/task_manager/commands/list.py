def list_tasks(tasks):
    if not tasks:
        print("No tasks available.")
        return

    print("Current Tasks:")
    for task in tasks:
        status = "✓" if task.completed else "✗"
        print(f"[{status}] {task.id}: {task.description}")

def main():
    from task_manager.utils.storage import load_tasks
    tasks = load_tasks()
    list_tasks(tasks)

if __name__ == "__main__":
    main()