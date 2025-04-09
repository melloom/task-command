"""
Interactive CLI for Task Manager
"""
import os
import sys
import time
import datetime
from task_manager.models.task import Task
from task_manager.utils.storage import load_tasks, save_tasks
from task_manager.commands.add import add_task
from task_manager.commands.list import list_tasks
from task_manager.commands.complete import complete_task
from task_manager.commands.delete import delete_task

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Print a formatted header"""
    width = 60
    print("=" * width)
    print(f"{title:^{width}}")
    print("=" * width)
    print()

def print_menu(options):
    """Print menu options"""
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    print("0. Exit")
    print()

def print_footer():
    """Print helpful shortcuts at the bottom of the screen"""
    print("\n" + "-" * 60)
    print("Commands: 0=Exit | q=Quit | ?=Help")

def show_welcome_screen():
    """Display a welcome screen with basic instructions"""
    clear_screen()
    width = 60
    print("=" * width)
    print(f"{'Welcome to Task Manager CLI':^{width}}")
    print("=" * width)
    print("\nNavigate using the menu numbers or 'q' to exit any screen.")
    print("\nQuick Tips:")
    print("- Use arrow keys or numbers to select options")
    print("- Enter '0' to go back or exit")
    print("- Press Ctrl+C at any time to exit the application")
    print("\nVersion: 1.0.0")
    print("\nPress Enter to continue...")
    input()

def show_help():
    """Show help information"""
    clear_screen()
    print_header("Task Manager Help")

    print("NAVIGATION:")
    print("  - Enter the number of an option to select it")
    print("  - Enter '0' to go back or exit a screen")
    print("  - Enter 'q' to quit immediately from any prompt")
    print("  - Press Ctrl+C to exit the application at any time")

    print("\nMAIN MENU OPTIONS:")
    print("  1. View All Tasks - List all tasks and select one to view/edit")
    print("  2. Add New Task - Create a new task with description, priority, etc.")
    print("  3. Filter Tasks - Show tasks filtered by various criteria")
    print("  4. Sort Tasks - Sort the task list by different properties")
    print("  5. Use Template - Create a task from a pre-defined template")

    print("\nTASK MANAGEMENT:")
    print("  - Mark tasks as complete to track your progress")
    print("  - Set due dates to prioritize your work")
    print("  - Categorize tasks for better organization")
    print("  - Track progress percentage for ongoing tasks")

    print("\nPress Enter to return...")
    input()

def get_input(prompt, valid_range=None):
    """Get user input with validation and help support"""
    while True:
        try:
            # Add a visible CLI prompt for better UX
            formatted_prompt = f"\033[1;36m➤\033[0m {prompt}"
            choice = input(formatted_prompt)

            # Special commands
            if choice.lower() == 'q':
                clear_screen()
                print("Exiting Task Manager...\nYour tasks have been saved.")
                import sys
                sys.exit(0)
            elif choice.lower() == '?':
                show_help()
                return -1  # Special value to indicate help was shown

            # Normal number input
            if not choice.strip():
                continue  # Empty input, ask again

            choice = int(choice)
            if valid_range is None or choice in valid_range:
                return choice

            print(f"Please enter a number between {min(valid_range)} and {max(valid_range)}, or 0 to exit.")
            print("Type '?' for help.")

        except ValueError:
            print("Please enter a valid number. Type '?' for help.")

def format_task(task, index=None):
    """Format a task for display"""
    # Use index if provided, otherwise use task.id
    task_id = index if index is not None else task.id
    status = "[✓]" if task.completed else "[ ]"

    # Format due date
    due_date = ""
    if hasattr(task, 'due_date') and task.due_date:
        try:
            date_obj = datetime.datetime.strptime(task.due_date, "%Y-%m-%d").date()
            today = datetime.date.today()

            if date_obj < today:
                due_date = f"\033[91m(Overdue: {task.due_date})\033[0m"  # Red for overdue
            elif date_obj == today:
                due_date = f"\033[93m(Due Today)\033[0m"  # Yellow for today
            else:
                due_date = f"(Due: {task.due_date})"
        except ValueError:
            due_date = f"(Due: {task.due_date})"

    # Format priority
    priority_colors = {
        "High": "\033[91m",    # Red
        "Medium": "\033[94m",  # Blue
        "Low": "\033[92m"      # Green
    }
    priority = getattr(task, 'priority', 'Medium')
    priority_str = f"{priority_colors.get(priority, '')}{priority}\033[0m"

    # Format category
    category = f"[{task.category}]" if hasattr(task, 'category') and task.category else ""

    # Basic task info
    line = f"{task_id:3d}. {status} {task.description}"

    # Add details
    details = " ".join(filter(None, [
        priority_str,
        due_date,
        category
    ]))

    if details:
        line += f" - {details}"

    return line

def show_tasks(tasks, title="All Tasks"):
    """Display a list of tasks"""
    clear_screen()
    print_header(title)

    filtered_tasks = tasks

    if not filtered_tasks:
        print("No tasks found.")
        print()
        return filtered_tasks

    # Display tasks
    for i, task in enumerate(filtered_tasks, 1):
        print(format_task(task, i))

    print()
    return filtered_tasks

def task_details(task):
    """Show detailed view of a task"""
    clear_screen()
    print_header(f"Task #{task.id} Details")

    print(f"Description: {task.description}")
    print(f"Status: {'Completed' if task.completed else 'Active'}")
    print(f"Priority: {getattr(task, 'priority', 'Medium')}")

    if hasattr(task, 'due_date') and task.due_date:
        print(f"Due Date: {task.due_date}")

    if hasattr(task, 'category') and task.category:
        print(f"Category: {task.category}")

    if hasattr(task, 'progress'):
        print(f"Progress: {task.progress}%")

    if hasattr(task, 'notes') and task.notes:
        print("\nNotes:")
        print(task.notes)

    print("\nOptions:")
    print("1. Edit Task")
    print("2. Toggle Completion")
    print("3. Delete Task")
    print("0. Back to List")
    print()

def add_task_interactive():
    """Interactive dialog to add a new task"""
    clear_screen()
    print_header("Add New Task")

    # Get task details
    description = input("Description: ")
    if not description.strip():
        print("Task must have a description. Operation cancelled.")
        time.sleep(1.5)
        return

    priority_options = ["High", "Medium", "Low"]
    print("\nPriority:")
    for i, option in enumerate(priority_options, 1):
        print(f"{i}. {option}")
    priority_choice = get_input("Select priority (1-3) [default=2]: ", range(1, 4))
    if priority_choice == 0:
        return
    priority = priority_options[priority_choice - 1]

    due_date = input("\nDue Date (YYYY-MM-DD) [optional]: ")
    if due_date:
        try:
            datetime.datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Using no due date.")
            due_date = None
    else:
        due_date = None

    category = input("\nCategory [optional]: ")
    if not category.strip():
        category = None

    notes = input("\nNotes [optional]: ")
    if not notes.strip():
        notes = None

    # Create and save the task
    tasks = load_tasks()

    # Generate new task ID
    if tasks:
        task_id = max(task.id for task in tasks) + 1
    else:
        task_id = 1

    new_task = Task(task_id=task_id, description=description)
    new_task.priority = priority
    new_task.due_date = due_date
    new_task.category = category
    new_task.notes = notes
    new_task.progress = 0

    tasks.append(new_task)
    save_tasks(tasks)

    print("\nTask added successfully!")
    time.sleep(1.5)

def edit_task_interactive(task):
    """Interactive dialog to edit a task"""
    clear_screen()
    print_header(f"Edit Task #{task.id}")

    # Edit description
    print(f"Current description: {task.description}")
    new_description = input("New description (leave empty to keep current): ")
    if new_description.strip():
        task.description = new_description

    # Edit priority
    priority_options = ["High", "Medium", "Low"]
    current_priority = getattr(task, 'priority', 'Medium')
    print(f"\nCurrent priority: {current_priority}")
    print("New priority:")
    for i, option in enumerate(priority_options, 1):
        print(f"{i}. {option}")
    priority_choice = get_input("Select priority (1-3) [leave empty to keep current]: ", range(1, 4))
    if priority_choice != 0:
        task.priority = priority_options[priority_choice - 1]

    # Edit due date
    current_due_date = getattr(task, 'due_date', None)
    print(f"\nCurrent due date: {current_due_date or 'None'}")
    new_due_date = input("New due date (YYYY-MM-DD) [leave empty to keep current, 'none' to remove]: ")
    if new_due_date.lower() == 'none':
        task.due_date = None
    elif new_due_date.strip():
        try:
            datetime.datetime.strptime(new_due_date, "%Y-%m-%d")
            task.due_date = new_due_date
        except ValueError:
            print("Invalid date format. Keeping current due date.")

    # Edit category
    current_category = getattr(task, 'category', None)
    print(f"\nCurrent category: {current_category or 'None'}")
    new_category = input("New category [leave empty to keep current, 'none' to remove]: ")
    if new_category.lower() == 'none':
        task.category = None
    elif new_category.strip():
        task.category = new_category

    # Edit notes
    current_notes = getattr(task, 'notes', None)
    print(f"\nCurrent notes: {current_notes or 'None'}")
    print("New notes [leave empty to keep current, 'none' to remove]:")
    new_notes = input("> ")
    if new_notes.lower() == 'none':
        task.notes = None
    elif new_notes.strip():
        task.notes = new_notes

    # Edit progress
    current_progress = getattr(task, 'progress', 0)
    print(f"\nCurrent progress: {current_progress}%")
    new_progress = input("New progress (0-100) [leave empty to keep current]: ")
    if new_progress.strip():
        try:
            progress_value = int(new_progress)
            if 0 <= progress_value <= 100:
                task.progress = progress_value
            else:
                print("Progress must be between 0 and 100. Keeping current progress.")
        except ValueError:
            print("Invalid progress value. Keeping current progress.")

    # Save changes
    tasks = load_tasks()
    for i, t in enumerate(tasks):
        if t.id == task.id:
            tasks[i] = task
            break

    save_tasks(tasks)
    print("\nTask updated successfully!")
    time.sleep(1.5)

def filter_menu():
    """Show task filtering options"""
    clear_screen()
    print_header("Filter Tasks")

    options = [
        "All Tasks",
        "Active Tasks",
        "Completed Tasks",
        "High Priority",
        "Medium Priority",
        "Low Priority",
        "Overdue Tasks",
        "Due Today",
        "Due This Week",
        "Search by Keyword"
    ]

    print_menu(options)
    choice = get_input("Select filter option: ", range(0, len(options) + 1))

    tasks = load_tasks()
    today = datetime.date.today()
    end_of_week = today + datetime.timedelta(days=7)

    if choice == 1:  # All Tasks
        return show_tasks(tasks, "All Tasks")
    elif choice == 2:  # Active Tasks
        filtered = [t for t in tasks if not t.completed]
        return show_tasks(filtered, "Active Tasks")
    elif choice == 3:  # Completed Tasks
        filtered = [t for t in tasks if t.completed]
        return show_tasks(filtered, "Completed Tasks")
    elif choice == 4:  # High Priority
        filtered = [t for t in tasks if getattr(t, 'priority', 'Medium') == 'High']
        return show_tasks(filtered, "High Priority Tasks")
    elif choice == 5:  # Medium Priority
        filtered = [t for t in tasks if getattr(t, 'priority', 'Medium') == 'Medium']
        return show_tasks(filtered, "Medium Priority Tasks")
    elif choice == 6:  # Low Priority
        filtered = [t for t in tasks if getattr(t, 'priority', 'Medium') == 'Low']
        return show_tasks(filtered, "Low Priority Tasks")
    elif choice == 7:  # Overdue Tasks
        filtered = []
        for task in tasks:
            if hasattr(task, 'due_date') and task.due_date and not task.completed:
                try:
                    due_date = datetime.datetime.strptime(task.due_date, "%Y-%m-%d").date()
                    if due_date < today:
                        filtered.append(task)
                except ValueError:
                    continue
        return show_tasks(filtered, "Overdue Tasks")
    elif choice == 8:  # Due Today
        filtered = []
        for task in tasks:
            if hasattr(task, 'due_date') and task.due_date and not task.completed:
                try:
                    due_date = datetime.datetime.strptime(task.due_date, "%Y-%m-%d").date()
                    if due_date == today:
                        filtered.append(task)
                except ValueError:
                    continue
        return show_tasks(filtered, "Tasks Due Today")
    elif choice == 9:  # Due This Week
        filtered = []
        for task in tasks:
            if hasattr(task, 'due_date') and task.due_date and not task.completed:
                try:
                    due_date = datetime.datetime.strptime(task.due_date, "%Y-%m-%d").date()
                    if today <= due_date <= end_of_week:
                        filtered.append(task)
                except ValueError:
                    continue
        return show_tasks(filtered, "Tasks Due This Week")
    elif choice == 10:  # Search by Keyword
        keyword = input("Enter search term: ").lower()
        if keyword:
            filtered = [t for t in tasks if keyword in t.description.lower() or
                         (hasattr(t, 'notes') and t.notes and keyword in t.notes.lower()) or
                         (hasattr(t, 'category') and t.category and keyword in t.category.lower())]
            return show_tasks(filtered, f"Search Results for '{keyword}'")

    return tasks

def main_menu():
    """Display main menu and process user choices"""
    while True:
        clear_screen()
        print_header("Task Manager - Main Menu")

        options = [
            "View All Tasks",
            "Add New Task",
            "Filter Tasks",
            "Sort Tasks",
            "Use Template"
        ]

        print_menu(options)
        print_footer()

        choice = get_input("Select an option: ", range(0, len(options) + 1))

        if choice == 0:
            break
        elif choice == 1:  # View All Tasks
            tasks = show_tasks(load_tasks())
            if tasks:
                task_choice = get_input("Select a task number to view details (0 to go back): ",
                                      range(0, len(tasks) + 1))
                if task_choice > 0:
                    task_menu(tasks[task_choice - 1])
        elif choice == 2:  # Add New Task
            add_task_interactive()
        elif choice == 3:  # Filter Tasks
            filtered_tasks = filter_menu()
            if filtered_tasks:
                task_choice = get_input("Select a task number to view details (0 to go back): ",
                                      range(0, len(filtered_tasks) + 1))
                if task_choice > 0:
                    task_menu(filtered_tasks[task_choice - 1])
        elif choice == 4:  # Sort Tasks
            sort_menu()
        elif choice == 5:  # Use Template
            use_template()
        elif choice == -1 or choice == '?':  # Hidden help option
            show_help()

def use_template():
    """Create a task from a template"""
    clear_screen()
    print_header("Create Task from Template")

    # Load templates
    from task_manager.utils.templates import load_templates
    templates = load_templates()

    if not templates:
        print("No templates available.")
        input("\nPress Enter to continue...")
        return

    # Show available templates
    print("Available Templates:")
    template_names = list(templates.keys())
    for i, name in enumerate(template_names, 1):
        print(f"{i}. {name}")
    print()

    # Get template choice
    template_choice = get_input("Select a template (0 to cancel): ", range(0, len(template_names) + 1))
    if template_choice == 0:
        return

    template_name = template_names[template_choice - 1]
    template = templates[template_name]

    # Find variables in template
    import re
    variables = set()
    for value in template.values():
        if isinstance(value, str):
            matches = re.findall(r'\{([^}]+)\}', value)
            variables.update(matches)

    # Get variable values
    variable_values = {}
    if variables:
        print(f"\nEnter values for template '{template_name}':")
        for var in variables:
            value = input(f"{var.replace('_', ' ').title()}: ")
            variable_values[var] = value

    # Get due date
    print("\nDue date (optional):")
    due_date = input("Due Date (YYYY-MM-DD) [leave empty for none]: ")
    if due_date:
        try:
            import datetime
            datetime.datetime.strptime(due_date, "%Y-%m-%d")
            variable_values['due_date'] = due_date
        except ValueError:
            print("Invalid date format. No due date will be set.")

    # Create task from template
    try:
        from task_manager.utils.templates import create_task_from_template
        from task_manager.models.task import Task
        from task_manager.utils.storage import load_tasks, save_tasks

        # Get task data from template
        task_data = create_task_from_template(template_name, variable_values)

        # Create a task ID
        tasks = load_tasks()
        task_id = 1 if not tasks else max(t.id for t in tasks) + 1

        # Create a new task
        new_task = Task(task_id=task_id)

        # Copy template data to task
        for key, value in task_data.items():
            setattr(new_task, key, value)

        # Add due date if provided
        if 'due_date' in variable_values:
            new_task.due_date = variable_values['due_date']

        # Add to task list
        tasks.append(new_task)

        # Save tasks
        save_tasks(tasks)

        print(f"\nTask created successfully from template '{template_name}'.")
    except Exception as e:
        print(f"\nError creating task: {str(e)}")

    input("\nPress Enter to continue...")

def task_menu(task):
    """Display task details and actions"""
    while True:
        task_details(task)
        choice = get_input("Select an option: ", range(0, 4))

        if choice == 0:
            break
        elif choice == 1:  # Edit Task
            edit_task_interactive(task)
            # Reload the task in case it was modified
            tasks = load_tasks()
            for t in tasks:
                if t.id == task.id:
                    task = t
                    break
        elif choice == 2:  # Toggle Completion
            task.completed = not task.completed
            if task.completed:
                task.progress = 100

            tasks = load_tasks()
            for i, t in enumerate(tasks):
                if t.id == task.id:
                    tasks[i] = task
                    break

            save_tasks(tasks)
            print("Task status updated.")
            time.sleep(1)
        elif choice == 3:  # Delete Task
            confirm = input("Are you sure you want to delete this task? (y/n): ")
            if confirm.lower() == 'y':
                tasks = load_tasks()
                tasks = [t for t in tasks if t.id != task.id]
                save_tasks(tasks)
                print("Task deleted.")
                time.sleep(1)
                return  # Exit task menu after deletion

def sort_menu():
    """Display and process sort options"""
    clear_screen()
    print_header("Sort Tasks")

    options = [
        "By ID",
        "By Description",
        "By Priority",
        "By Due Date",
        "By Progress"
    ]

    print_menu(options)
    choice = get_input("Select sort option: ", range(0, len(options) + 1))

    if choice == 0:
        return

    tasks = load_tasks()

    if choice == 1:  # By ID
        tasks.sort(key=lambda t: t.id)
        show_tasks(tasks, "Tasks Sorted by ID")
    elif choice == 2:  # By Description
        tasks.sort(key=lambda t: t.description.lower())
        show_tasks(tasks, "Tasks Sorted by Description")
    elif choice == 3:  # By Priority
        priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
        tasks.sort(key=lambda t: priority_order.get(getattr(t, 'priority', 'Medium'), 1))
        show_tasks(tasks, "Tasks Sorted by Priority")
    elif choice == 4:  # By Due Date
        # Define a key function that handles tasks without due dates
        def due_date_key(task):
            if not hasattr(task, 'due_date') or not task.due_date:
                return datetime.datetime.max  # Tasks without due dates come last
            try:
                return datetime.datetime.strptime(task.due_date, "%Y-%m-%d")
            except ValueError:
                return datetime.datetime.max

        tasks.sort(key=due_date_key)
        show_tasks(tasks, "Tasks Sorted by Due Date")
    elif choice == 5:  # By Progress
        tasks.sort(key=lambda t: getattr(t, 'progress', 0))
        show_tasks(tasks, "Tasks Sorted by Progress")

    if tasks:
        task_choice = get_input("Select a task number to view details (0 to go back): ", range(0, len(tasks) + 1))
        if task_choice > 0:
            task_menu(tasks[task_choice - 1])

def run_interactive_cli():
    """Entry point for the interactive CLI"""
    try:
        # Show welcome screen on first run
        show_welcome_screen()

        # Start the main menu loop
        main_menu()

    except KeyboardInterrupt:
        clear_screen()
        print("\nExiting Task Manager...\nYour tasks have been saved.")

    print("Goodbye!")

if __name__ == "__main__":
    run_interactive_cli()
