def main():
    import sys
    import argparse
    from task_manager.commands.add import add_task
    from task_manager.commands.list import list_tasks
    from task_manager.commands.complete import complete_task
    from task_manager.commands.delete import delete_task
    from task_manager.utils.settings import load_settings, toggle_interactive_mode

    # Show a welcome banner when starting the CLI
    print("\033[1;36m")
    print("=======================================")
    print("   Task Manager CLI - Version 1.0.0   ")
    print("=======================================")
    print("\033[0m")

    # Create argument parser with better help texts
    parser = argparse.ArgumentParser(
        description="Task Manager CLI - Manage your tasks from the command line",
        epilog="Run without arguments to enter interactive mode (if enabled)"
    )

    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Add task command
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("description", help="Task description", nargs="+")
    add_parser.add_argument("-p", "--priority", choices=["High", "Medium", "Low"],
                           default="Medium", help="Task priority (default: Medium)")
    add_parser.add_argument("-d", "--due", help="Due date in YYYY-MM-DD format")
    add_parser.add_argument("-c", "--category", help="Task category")

    # List tasks command
    list_parser = subparsers.add_parser("list", help="List all tasks")
    list_parser.add_argument("-s", "--status", choices=["all", "active", "completed"],
                            default="all", help="Filter by status")
    list_parser.add_argument("-p", "--priority", choices=["all", "High", "Medium", "Low"],
                            default="all", help="Filter by priority")

    # Complete task command
    complete_parser = subparsers.add_parser("complete", help="Mark a task as complete")
    complete_parser.add_argument("task_id", type=int, help="ID of the task to complete")

    # Delete task command
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("task_id", type=int, help="ID of the task to delete")

    # Interactive mode command
    subparsers.add_parser("interactive", help="Start interactive mode")

    # Toggle interactive mode command
    subparsers.add_parser("toggle-interactive", help="Toggle the default interactive mode setting")

    # Parse arguments
    if len(sys.argv) > 1:
        args = parser.parse_args()
    else:
        # If no arguments, check settings for interactive mode preference
        settings = load_settings()
        use_interactive = settings.get('cli', {}).get('interactive_mode', True)

        if use_interactive:
            from task_manager.cli_interactive import run_interactive_cli
            print("Starting Task Manager in interactive mode...")
            print("Tip: Use 'task-cli --help' to see all available commands")
            run_interactive_cli()
            return
        else:
            # For command mode, show a prompt for input
            command = input("\033[1;36m➤ task-cli\033[0m ")
            if command.strip():
                # Process the entered command
                sys.argv.extend(command.split())
                args = parser.parse_args()
            else:
                parser.print_help()
                return

    # Process commands
    if args.command == "add":
        description = " ".join(args.description)
        add_task(description, priority=args.priority, due_date=args.due, category=args.category)
        print(f"Task added: {description}")

    elif args.command == "list":
        list_tasks(status=args.status, priority=args.priority)

    elif args.command == "complete":
        try:
            complete_task(args.task_id)
            print(f"Task #{args.task_id} marked as complete")
        except Exception as e:
            print(f"Error: {str(e)}")

    elif args.command == "delete":
        try:
            delete_task(args.task_id)
            print(f"Task #{args.task_id} deleted")
        except Exception as e:
            print(f"Error: {str(e)}")

    elif args.command == "interactive":
        # Explicit request for interactive mode
        from task_manager.cli_interactive import run_interactive_cli
        print("Starting Task Manager in interactive mode...")
        run_interactive_cli()

    elif args.command == "toggle-interactive":
        new_mode = toggle_interactive_mode()
        print(f"Interactive mode {'enabled' if new_mode else 'disabled'}")
        print(f"Default mode is now: {'Interactive' if new_mode else 'Command-line'}")

    else:
        # Fallback to help
        parser.print_help()

if __name__ == "__main__":
    main()