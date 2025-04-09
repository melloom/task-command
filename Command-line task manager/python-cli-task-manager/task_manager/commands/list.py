"""
List tasks command for Task Manager
"""

from task_manager.utils.storage import load_tasks
import datetime
import os
import sys

def list_tasks(status="all", priority="all", due=None, category=None, sort_by=None):
    """List tasks with optional filtering and sorting"""
    tasks = load_tasks()

    # Filter by status
    if status == "active":
        tasks = [t for t in tasks if not t.completed]
    elif status == "completed":
        tasks = [t for t in tasks if t.completed]

    # Filter by priority
    if priority != "all":
        tasks = [t for t in tasks if getattr(t, 'priority', 'Medium') == priority]

    # Filter by due date
    if due == "today":
        today = datetime.date.today()
        tasks = [t for t in tasks if t.due_date and
                datetime.datetime.strptime(t.due_date, "%Y-%m-%d").date() == today]
    elif due == "week":
        today = datetime.date.today()
        end_date = today + datetime.timedelta(days=7)
        tasks = [t for t in tasks if t.due_date and
                today <= datetime.datetime.strptime(t.due_date, "%Y-%m-%d").date() <= end_date]
    elif due == "overdue":
        today = datetime.date.today()
        tasks = [t for t in tasks if t.due_date and
                datetime.datetime.strptime(t.due_date, "%Y-%m-%d").date() < today]

    # Filter by category
    if category:
        tasks = [t for t in tasks if hasattr(t, 'category') and t.category == category]

    # Sort tasks
    if sort_by == "priority":
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        tasks.sort(key=lambda t: priority_order.get(getattr(t, 'priority', 'Medium'), 1))
    elif sort_by == "due":
        # Sort by due date, with None values at the end
        tasks.sort(key=lambda t: datetime.datetime.strptime(t.due_date, "%Y-%m-%d").date() if t.due_date else datetime.date.max)
    else:
        # Default sort by ID
        tasks.sort(key=lambda t: t.id)

    if not tasks:
        print("No tasks found.")
        return

    # Try to import tabulate for nicer output
    try:
        from tabulate import tabulate
        use_tabulate = True
    except ImportError:
        use_tabulate = False

    # Check if color output is possible
    use_colors = sys.stdout.isatty() and os.name != 'nt'

    # Prepare data for display
    headers = ["ID", "Description", "Priority", "Due Date", "Status", "Progress", "Category"]
    rows = []

    for task in tasks:
        status_text = "✓" if task.completed else " "
        due_date = getattr(task, 'due_date', '') or ''
        priority_text = getattr(task, 'priority', 'Medium')
        category = getattr(task, 'category', '') or ''
        progress = f"{getattr(task, 'progress', 0)}%"

        if use_colors:
            # ANSI color codes
            reset = "\033[0m"

            if task.completed:
                color = "\033[90m"  # Gray for completed tasks
            elif priority_text == "High":
                color = "\033[91m"  # Red for high priority
            elif priority_text == "Medium":
                color = "\033[94m"  # Blue for medium priority
            elif priority_text == "Low":
                color = "\033[92m"  # Green for low priority
            else:
                color = ""

            description = f"{color}{task.description}{reset}"
            status_text = f"{color}{status_text}{reset}"
            priority_text = f"{color}{priority_text}{reset}"
        else:
            description = task.description

        # Check if task is overdue
        if due_date and not task.completed:
            try:
                due_date_obj = datetime.datetime.strptime(due_date, "%Y-%m-%d").date()
                if due_date_obj < datetime.date.today():
                    if use_colors:
                        due_date = f"\033[91m{due_date} (OVERDUE)\033[0m"
                    else:
                        due_date = f"{due_date} (OVERDUE)"
            except ValueError:
                pass

        row = [
            task.id,
            description,
            priority_text,
            due_date,
            status_text,
            progress,
            category
        ]
        rows.append(row)

    # Display table
    if use_tabulate:
        print(tabulate(rows, headers=headers, tablefmt="pretty"))
    else:
        # Simple table format for systems without tabulate
        # Print headers
        header_str = " | ".join(headers)
        print(header_str)
        print("-" * len(header_str))

        # Print rows
        for row in rows:
            print(" | ".join(str(cell) for cell in row))

    # Print summary
    total = len(tasks)
    completed = sum(1 for t in tasks if t.completed)
    active = total - completed

    print(f"\nTotal: {total} tasks | Active: {active} | Completed: {completed}")

    return tasks

def main():
    list_tasks()

if __name__ == "__main__":
    main()