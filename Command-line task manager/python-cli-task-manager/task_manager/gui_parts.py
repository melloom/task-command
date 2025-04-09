"""
Additional methods for the SimpleTaskManagerGUI class
This file contains methods that are imported by the main GUI module
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from task_manager.utils.storage import save_tasks

def create_task_list(self):
    """Create the task list treeview"""
    # Create main task list with scrollbars
    task_frame = ttk.Frame(self.main_frame)
    task_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

    # Create treeview with scrollbars
    self.task_tree = ttk.Treeview(task_frame)

    # Add vertical scrollbar
    vsb = ttk.Scrollbar(task_frame, orient="vertical", command=self.task_tree.yview)
    vsb.pack(side=tk.RIGHT, fill=tk.Y)

    # Add horizontal scrollbar
    hsb = ttk.Scrollbar(task_frame, orient="horizontal", command=self.task_tree.xview)
    hsb.pack(side=tk.BOTTOM, fill=tk.X)

    # Configure treeview to use scrollbars
    self.task_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Define columns
    self.task_tree["columns"] = ("id", "description", "priority", "due_date", "status", "progress", "category")

    # Format columns
    self.task_tree.column("#0", width=0, stretch=tk.NO)  # Hide the default column
    self.task_tree.column("id", width=50, minwidth=50)
    self.task_tree.column("description", width=300, minwidth=200)
    self.task_tree.column("priority", width=80, minwidth=80)

    # Define column headings
    self.task_tree.heading("#0", text="", anchor=tk.W)
    self.task_tree.heading("id", text="ID", anchor=tk.W)
    self.task_tree.heading("description", text="Description", anchor=tk.W)
    self.task_tree.heading("priority", text="Priority", anchor=tk.W)
    self.task_tree.heading("due_date", text="Due Date", anchor=tk.W)
    self.task_tree.heading("status", text="Status", anchor=tk.W)
    self.task_tree.heading("progress", text="Progress", anchor=tk.W)
    self.task_tree.heading("category", text="Category", anchor=tk.W)

    # Configure alternating row colors
    self.task_tree.tag_configure('odd_row', background='#f0f0f0')
    self.task_tree.tag_configure('even_row', background='#ffffff')

    # Bind selection event
    self.task_tree.bind("<<TreeviewSelect>>", self.on_task_select)

    # Bind double-click event
    self.task_tree.bind("<Double-1>", self.on_task_double_click)

    # Create context menu
    self.create_context_menu()

def on_task_select(self, _=None):
    """Handle task selection event with improved multi-selection support"""
    selected_items = self.task_tree.selection()
    selected_count = len(selected_items)

    # Update selection count label
    if selected_count == 0:
        self.selected_count.set("No tasks selected")
    elif selected_count == 1:
        item_id = selected_items[0]
        task_id = self.task_tree.item(item_id, "values")[0]
        self.selected_count.set(f"Task #{task_id} selected")
    else:
        self.selected_count.set(f"{selected_count} tasks selected")

    # Enable/disable action buttons based on selection
    if selected_count > 0:
        self.complete_btn.config(state=tk.NORMAL)
        self.delete_btn.config(state=tk.NORMAL)
        # Only enable edit button for single selection
        self.edit_btn.config(state=tk.NORMAL if selected_count == 1 else tk.DISABLED)
    else:
        self.complete_btn.config(state=tk.DISABLED)
        self.edit_btn.config(state=tk.DISABLED)
        self.delete_btn.config(state=tk.DISABLED)

def select_all_tasks(self, event=None):
    """Select all tasks with visual feedback"""
    # First deselect all (to ensure clean state)
    self.task_tree.selection_remove(self.task_tree.selection())

    # Then select all items
    for item in self.task_tree.get_children():
        self.task_tree.selection_add(item)

    # Ensure at least one item is visible
    if self.task_tree.get_children():
        self.task_tree.see(self.task_tree.get_children()[0])

    # Update selection status
    self.on_task_select()

    # Show brief confirmation in status bar
    old_text = self.status_bar.cget("text")
    self.status_bar.config(text="Selected all tasks")

    # Restore previous status after a delay
    self.root.after(1500, lambda: self.status_bar.config(text=old_text))

    return "break"  # Prevent default behavior for Ctrl+A

def deselect_all_tasks(self):
    """Deselect all tasks with visual feedback"""
    self.task_tree.selection_remove(self.task_tree.selection())

    # Update selection status
    self.on_task_select()

    # Show brief confirmation
    old_text = self.status_bar.cget("text")
    self.status_bar.config(text="Deselected all tasks")

    # Restore previous status
    self.root.after(1500, lambda: self.status_bar.config(text=old_text))

def refresh_task_list(self):
    # Clear current items
    for item in self.task_tree.get_children():
        self.task_tree.delete(item)

    # Sort by ID
    filtered_tasks = [t for t in self.tasks if self.matches_filters(t)]
    filtered_tasks.sort(key=lambda t: t.id)

    # Add tasks to the tree with alternating row colors
    for i, task in enumerate(filtered_tasks):
        status = "Completed" if task.completed else "Active"
        due_date = task.due_date if task.due_date else ""
        priority = task.priority if hasattr(task, 'priority') else "Medium"
        progress = f"{task.progress}%" if hasattr(task, 'progress') else "0%"
        category = task.category if hasattr(task, 'category') and task.category else ""

        # Insert the item
        item_id = self.task_tree.insert(
            "",
            tk.END,
            values=(task.id, task.description, priority, due_date, status, progress, category),
            tags=('even_row' if i % 2 == 0 else 'odd_row',)  # Alternate row colors
        )

        # Add additional tags for priority and status
        if task.completed:
            self.task_tree.item(item_id, tags=self.task_tree.item(item_id, "tags") + ("completed",))
        elif priority == "High":
            self.task_tree.item(item_id, tags=self.task_tree.item(item_id, "tags") + ("high",))
        elif priority == "Medium":
            self.task_tree.item(item_id, tags=self.task_tree.item(item_id, "tags") + ("medium",))
        elif priority == "Low":
            self.task_tree.item(item_id, tags=self.task_tree.item(item_id, "tags") + ("low",))

    # Configure tag colors with improved visibility
    self.task_tree.tag_configure("completed", foreground="#888888")
    self.task_tree.tag_configure("high", foreground="#d9534f")  # Bootstrap danger red
    self.task_tree.tag_configure("medium", foreground="#0275d8")  # Bootstrap primary blue
    self.task_tree.tag_configure("low", foreground="#5cb85c")  # Bootstrap success green

    # Update status bar
    total = len(self.tasks)
    completed = sum(1 for t in self.tasks if t.completed)
    active = total - completed
    filtered = len(filtered_tasks)

    self.status_bar.config(
        text=f"Total: {total} tasks | Active: {active} | Completed: {completed} | Showing: {filtered}"
    )

    # Reset selection status
    self.selected_count.set("No tasks selected")

    # Disable action buttons initially
    self.complete_btn.config(state=tk.DISABLED)
    self.edit_btn.config(state=tk.DISABLED)
    self.delete_btn.config(state=tk.DISABLED)

def matches_filters(self, task):
    # Status filter
    status_filter = self.status_var.get()
    if status_filter == "Active" and task.completed:
        return False
    elif status_filter == "Completed" and not task.completed:
        return False

    # Priority filter
    priority_filter = self.priority_var.get()
    if priority_filter != "All" and task.priority != priority_filter:
        return False

    # Due date filter
    due_filter = self.due_var.get()
    if due_filter != "All":
        today = datetime.date.today()

        # Helper function to safely parse date strings
        def safe_parse_date(date_string):
            try:
                return datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                return None

        task_date = safe_parse_date(task.due_date)

        if due_filter == "Today" and (not task_date or task_date != today):
            return False
        elif due_filter == "This Week":
            end_date = today + datetime.timedelta(days=7)
            if not task_date or not (today <= task_date <= end_date):
                return False
        elif due_filter == "Overdue":
            if not task_date or task_date >= today:
                return False
        elif due_filter == "No Due Date" and task.due_date:
            return False

    # Search text filter
    search_text = self.search_var.get().lower()
    if search_text:
        if (search_text not in task.description.lower() and
            (not hasattr(task, 'category') or not task.category or
             search_text not in task.category.lower()) and
            (not hasattr(task, 'notes') or not task.notes or
             search_text not in task.notes.lower())):
            return False

    return True

def delete_task(self):
    selected_items = self.task_tree.selection()
    if not selected_items:
        messagebox.showinfo("Info", "Please select a task to delete")
        return

    # Confirm deletion
    task_count = len(selected_items)
    if task_count == 1:
        item_id = selected_items[0]
        task_id = int(self.task_tree.item(item_id, "values")[0])
        task = next((t for t in self.tasks if t.id == task_id), None)

        if not task:
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete task #{task.id}?\n\n{task.description}"
        )
    else:
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete {task_count} tasks?"
        )

    if confirm:
        # Collect tasks to delete
        tasks_to_delete = []
        for item_id in selected_items:
            task_id = int(self.task_tree.item(item_id, "values")[0])
            task = next((t for t in self.tasks if t.id == task_id), None)
            if task:
                tasks_to_delete.append(task)

        # Delete the tasks
        for task in tasks_to_delete:
            self.tasks.remove(task)

        # Save and refresh
        save_tasks(self.tasks)
        self.refresh_task_list()

        # Show success message
        if tasks_to_delete:
            self.status_bar.config(text=f"Deleted {len(tasks_to_delete)} task(s)")

def get_selected_task(self):
    """Get the currently selected task"""
    selected_item = self.task_tree.selection()
    if not selected_item:
        return None

    # Get task ID from the selected item
    item_id = selected_item[0]
    task_id = int(self.task_tree.item(item_id, "values")[0])

    # Find task with that ID
    for task in self.tasks:
        if task.id == task_id:
            return task

    return None  # Return None if task not found

def on_task_double_click(self, _):
    """Handle double-clicking on a task"""
    self.edit_task()
    return None

def create_context_menu(self):
    """Create right-click context menu for tasks"""
    self.context_menu = tk.Menu(self.root, tearoff=0)
    self.context_menu.add_command(label="Edit Task", command=self.edit_task)
    self.context_menu.add_command(label="Toggle Completion", command=self.toggle_complete)
    self.context_menu.add_separator()
    self.context_menu.add_command(label="Delete Task", command=self.delete_task)
    self.context_menu.add_separator()
    self.context_menu.add_command(label="Set Reminder", command=self.set_reminder)

    # Bind right-click to show context menu
    self.task_tree.bind("<Button-3>", self.show_context_menu)

def show_context_menu(self, event):
    """Show the context menu on right-click"""
    # Select the item under cursor
    item = self.task_tree.identify_row(event.y)
    if item:
        self.task_tree.selection_set(item)
        self.context_menu.post(event.x_root, event.y_root)

# Rest of the methods from gui 2...
def add_custom_category(self):
    """Add a custom category to an existing task"""
    new_category = messagebox.askstring("New Category", "Enter a new category name:")
    if new_category and new_category.strip():
        # This is for the main application - not the TaskEditor
        task = self.get_selected_task()
        if task:
            task.category = new_category
            save_tasks(self.tasks)
            self.refresh_task_list()
            self.status_bar.config(text=f"Added category '{new_category}' to task")
