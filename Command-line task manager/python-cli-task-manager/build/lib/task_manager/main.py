def main():
    import sys
    from task_manager.commands.add import add_task
    from task_manager.commands.list import list_tasks
    from task_manager.commands.complete import complete_task
    from task_manager.commands.delete import delete_task

    if len(sys.argv) < 2:
        print("Usage: python main.py [command] [options]")
        return

    command = sys.argv[1]

    if command == "add":
        description = " ".join(sys.argv[2:])
        add_task(description)
    elif command == "list":
        list_tasks()
    elif command == "complete":
        task_id = sys.argv[2]
        complete_task(task_id)
    elif command == "delete":
        task_id = sys.argv[2]
        delete_task(task_id)
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()