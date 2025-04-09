"""
Task Manager GUI using standard tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime
import time
import threading  # Used elsewhere in the code
import platform
import os  # Used elsewhere in the code
from task_manager.utils.storage import load_tasks, save_tasks
from task_manager.utils.notifications import show_notification, start_reminder_service  # Used elsewhere
from task_manager.models.task import Task
import tkinter.colorchooser as colorchooser
from task_manager.utils.settings import load_settings, save_settings, DEFAULT_SETTINGS, get_color  # Used elsewhere
from task_manager.utils.import_export import import_from_json, import_from_csv, export_to_json, export_to_csv  # Used elsewhere
from task_manager.ai_interface import show_ai_assistant

# Import the split gui methods
from task_manager.gui_parts import (
    create_task_list, on_task_select, select_all_tasks, deselect_all_tasks,
    refresh_task_list, matches_filters, delete_task, get_selected_task,
    on_task_double_click, create_context_menu, show_context_menu, add_custom_category
)

# App constants
APP_NAME = "Task Manager"
VERSION = "1.0.0"
COPYRIGHT = "© 2023 Task Manager Team"

# Make these functions available for import at the module level
def launch_simple_gui():
    """Launch the simple GUI version of the Task Manager."""
    root = tk.Tk()
    app = SimpleTaskManagerGUI(root)
    root.mainloop()

def launch_gui():
    """Launch the GUI version of the Task Manager (redirects to simple GUI)."""
    launch_simple_gui()

# Tooltip class for showing tooltips on hover
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        # Create a toplevel window
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = ttk.Label(self.tooltip, text=self.text, background="#ffffe0",
                         relief="solid", borderwidth=1, padding=(5, 2))
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

# Function to get all unique categories from tasks
def get_all_categories():
    tasks = load_tasks()
    categories = set()
    for task in tasks:
        if hasattr(task, 'category') and task.category:
            categories.add(task.category)
    return list(categories) or ["Work", "Personal", "Shopping", "Health", "Finance"]

# Task Editor Dialog
class TaskEditor(tk.Toplevel):
    """Dialog for adding or editing tasks"""
    def __init__(self, parent, task, title="Edit Task"):
        super().__init__(parent)
        self.title(title)
        self.task = task
        self.result = None

        # Set dialog size and position
        self.geometry("550x500")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        # Apply a light theme background
        self.configure(bg="#f5f5f7")

        # Create the form
        self.create_widgets()

        # Center on parent
        self.geometry(f"+{parent.winfo_rootx() + 50}+{parent.winfo_rooty() + 50}")

        # Wait for window to be destroyed
        self.wait_window()

    def create_widgets(self):
        # Main container with padding
        container = ttk.Frame(self, padding="20")
        container.pack(fill=tk.BOTH, expand=True)

        # Create a header
        header_frame = ttk.Frame(container)
        header_frame.pack(fill=tk.X, pady=(0, 15))

        header_text = "Task Details" if "Edit" in self.title() else "Create New Task"
        header_label = ttk.Label(header_frame, text=header_text,
                               font=("Helvetica", 16, "bold"))
        header_label.pack(anchor="w")

        subheader = "Edit the task details below" if "Edit" in self.title() else "Fill in the details for your new task"
        subheader_label = ttk.Label(header_frame, text=subheader,
                                  font=("Helvetica", 10))
        subheader_label.pack(anchor="w")

        ttk.Separator(container).pack(fill=tk.X, pady=(0, 15))

        # Form content using a notebook with tabs
        notebook = ttk.Notebook(container)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Basic info tab
        basic_frame = ttk.Frame(notebook, padding=15)
        notebook.add(basic_frame, text="Basic Info")

        # Description field with improved styling
        ttk.Label(basic_frame, text="Description:", font=("Helvetica", 10, "bold")).grid(
            row=0, column=0, sticky="w", padx=5, pady=10)
        self.description_var = tk.StringVar(value=self.task.description)
        description_entry = ttk.Entry(basic_frame, textvariable=self.description_var, width=40)
        description_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=10)
        description_entry.focus_set()

        # Priority field with color indicators
        ttk.Label(basic_frame, text="Priority:", font=("Helvetica", 10, "bold")).grid(
            row=1, column=0, sticky="w", padx=5, pady=10)

        priority_frame = ttk.Frame(basic_frame)
        priority_frame.grid(row=1, column=1, sticky="ew", padx=5, pady=10)

        self.priority_var = tk.StringVar(value=getattr(self.task, 'priority', 'Medium'))

        # Create stylish radio buttons instead of combobox
        priorities = [("High", "red"), ("Medium", "blue"), ("Low", "green")]
        for i, (priority, color) in enumerate(priorities):
            rb = ttk.Radiobutton(priority_frame, text=priority, value=priority,
                               variable=self.priority_var)
            rb.pack(side=tk.LEFT, padx=(0 if i == 0 else 10, 0))

            # Add a colored indicator
            indicator = tk.Frame(priority_frame, width=10, height=10, bg=color)
            indicator.pack(side=tk.LEFT, padx=(5, 15 if i < len(priorities)-1 else 0))

        # Due date with improved date picker button
        ttk.Label(basic_frame, text="Due Date:", font=("Helvetica", 10, "bold")).grid(
            row=2, column=0, sticky="w", padx=5, pady=10)

        date_frame = ttk.Frame(basic_frame)
        date_frame.grid(row=2, column=1, sticky="ew", padx=5, pady=10)

        self.due_date_var = tk.StringVar(value=getattr(self.task, 'due_date', ''))
        due_date_entry = ttk.Entry(date_frame, textvariable=self.due_date_var, width=15)
        due_date_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Fixed calendar button with proper styling
        style = ttk.Style()
        style.configure("Calendar.TButton", foreground="black", background="white")
        calendar_btn = ttk.Button(date_frame, text="📅", width=3,
                                command=self.select_date, style="Calendar.TButton")
        calendar_btn.pack(side=tk.LEFT, padx=(5, 0))
        Tooltip(calendar_btn, "Select date from calendar")

        # Category field with custom input option
        ttk.Label(basic_frame, text="Category:", font=("Helvetica", 10, "bold")).grid(
            row=3, column=0, sticky="w", padx=5, pady=10)

        category_frame = ttk.Frame(basic_frame)
        category_frame.grid(row=3, column=1, sticky="ew", padx=5, pady=10)

        self.category_var = tk.StringVar(value=getattr(self.task, 'category', ''))

        # Create a combo box for predefined categories
        self.category_combo = ttk.Combobox(category_frame, textvariable=self.category_var,
                                         values=get_all_categories(), width=20)
        self.category_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Add a button to add custom category
        add_cat_btn = ttk.Button(category_frame, text="+", width=3,
                               command=self.add_custom_category)
        add_cat_btn.pack(side=tk.LEFT, padx=(5, 0))
        Tooltip(add_cat_btn, "Add custom category")

        # Completed status
        self.completed_var = tk.BooleanVar(value=getattr(self.task, 'completed', False))
        completed_check = ttk.Checkbutton(basic_frame, text="Mark as completed",
                                        variable=self.completed_var)
        completed_check.grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=10)

        # Make form fields resize with window
        basic_frame.columnconfigure(1, weight=1)

        # Details tab
        details_frame = ttk.Frame(notebook, padding=15)
        notebook.add(details_frame, text="Details")

        # Progress with improved visual bar
        ttk.Label(details_frame, text="Progress:", font=("Helvetica", 10, "bold")).grid(
            row=0, column=0, sticky="w", padx=5, pady=10)

        progress_frame = ttk.Frame(details_frame)
        progress_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=10)

        self.progress_var = tk.IntVar(value=getattr(self.task, 'progress', 0))

        progress_slider = ttk.Scale(progress_frame, from_=0, to=100, variable=self.progress_var,
                                  orient=tk.HORIZONTAL, length=200)
        progress_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Show percentage with dynamic color change
        progress_label = ttk.Label(progress_frame, textvariable=self.progress_var, width=4)
        progress_label.pack(side=tk.LEFT, padx=(5, 0))
        progress_label.after(100, lambda: self.update_progress_label(progress_label))

        # Notes section with better styling
        ttk.Label(details_frame, text="Notes:", font=("Helvetica", 10, "bold")).grid(
            row=1, column=0, sticky="nw", padx=5, pady=10)

        notes_frame = ttk.Frame(details_frame)
        notes_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=10)

        self.notes_text = tk.Text(notes_frame, width=40, height=10,
                                wrap=tk.WORD, bd=1, relief=tk.SOLID,
                                font=("Helvetica", 10))
        self.notes_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        if hasattr(self.task, 'notes') and self.task.notes:
            self.notes_text.insert("1.0", self.task.notes)

        notes_scroll = ttk.Scrollbar(notes_frame, orient="vertical", command=self.notes_text.yview)
        notes_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.notes_text.configure(yscrollcommand=notes_scroll.set)

        # Make details frame expand
        details_frame.columnconfigure(1, weight=1)
        details_frame.rowconfigure(1, weight=1)

        # Buttons with improved styling
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X)

        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.destroy, width=10)
        cancel_btn.pack(side=tk.RIGHT, padx=5)

        save_btn = ttk.Button(button_frame, text="Save", command=self.save_task, width=10)
        save_btn.pack(side=tk.RIGHT, padx=5)

        # Add a help button
        help_btn = ttk.Button(button_frame, text="Help", width=10,
                           command=lambda: messagebox.showinfo("Help",
                                                            "Fill in the task details and click Save when done.\n"
                                                            "All fields except Description are optional."))
        help_btn.pack(side=tk.LEFT, padx=5)

    def update_progress_label(self, label):
        """Update the progress label with color based on value"""
        progress = self.progress_var.get()
        if progress < 30:
            label.configure(foreground="red")
        elif progress < 70:
            label.configure(foreground="blue")
        else:
            label.configure(foreground="green")

        # Continue updating if the window still exists
        try:
            if self.winfo_exists():
                label.after(100, lambda: self.update_progress_label(label))
        except:
            pass  # Window was destroyed

    def select_date(self):
        # Show date picker
        date_dialog = DateTimeDialog(self, "Select Due Date")
        if date_dialog.result:
            self.due_date_var.set(date_dialog.result.strftime("%Y-%m-%d"))

    def add_custom_category(self):
        """Add a custom category"""
        new_category = simpledialog.askstring("New Category", "Enter a new category name:")
        if new_category and new_category.strip():
            current_values = list(self.category_combo['values'])
            if new_category not in current_values:
                new_values = current_values + [new_category]
                self.category_combo['values'] = new_values
                self.category_var.set(new_category)

    def save_task(self):
        # Validate input
        if not self.description_var.get().strip():
            messagebox.showerror("Error", "Description cannot be empty")
            return

        # Create result dictionary with updated values
        self.result = {
            'description': self.description_var.get().strip(),
            'priority': self.priority_var.get(),
            'due_date': self.due_date_var.get().strip() if self.due_date_var.get().strip() else None,
            'category': self.category_var.get().strip() if self.category_var.get().strip() else None,
            'progress': self.progress_var.get(),
            'completed': self.completed_var.get(),
            'notes': self.notes_text.get("1.0", tk.END).strip()
        }

        # Close dialog
        self.destroy()

# DateTime Picker Dialog
class DateTimeDialog(tk.Toplevel):
    """Dialog for selecting date and time"""
    def __init__(self, parent, title="Select Date and Time", default_datetime=None):
        super().__init__(parent)
        self.title(title)
        self.result = None

        # Set default datetime to now if not provided
        if default_datetime is None:
            default_datetime = datetime.datetime.now()

        # Set dialog properties
        self.geometry("300x200")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Create the form
        self.create_widgets(default_datetime)

        # Center on parent
        self.geometry(f"+{parent.winfo_rootx() + 50}+{parent.winfo_rooty() + 50}")

        # Wait for window to be destroyed
        self.wait_window()

    def create_widgets(self, default_datetime):
        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Date selection
        date_frame = ttk.LabelFrame(main_frame, text="Date")
        date_frame.pack(fill=tk.X, padx=5, pady=5)

        # Date variables
        self.year_var = tk.IntVar(value=default_datetime.year)
        self.month_var = tk.IntVar(value=default_datetime.month)
        self.day_var = tk.IntVar(value=default_datetime.day)

        # Date spinners
        ttk.Label(date_frame, text="Year:").grid(row=0, column=0, padx=5, pady=5)
        year_spinner = ttk.Spinbox(date_frame, from_=2000, to=2100, textvariable=self.year_var, width=6)
        year_spinner.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(date_frame, text="Month:").grid(row=0, column=2, padx=5, pady=5)
        month_spinner = ttk.Spinbox(date_frame, from_=1, to=12, textvariable=self.month_var, width=4)
        month_spinner.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(date_frame, text="Day:").grid(row=0, column=4, padx=5, pady=5)
        day_spinner = ttk.Spinbox(date_frame, from_=1, to=31, textvariable=self.day_var, width=4)
        day_spinner.grid(row=0, column=5, padx=5, pady=5)

        # Time selection
        time_frame = ttk.LabelFrame(main_frame, text="Time")
        time_frame.pack(fill=tk.X, padx=5, pady=5)

        # Time variables
        self.hour_var = tk.IntVar(value=default_datetime.hour)
        self.minute_var = tk.IntVar(value=default_datetime.minute)

        # Time spinners
        ttk.Label(time_frame, text="Hour:").grid(row=0, column=0, padx=5, pady=5)
        hour_spinner = ttk.Spinbox(time_frame, from_=0, to=23, textvariable=self.hour_var, width=4)
        hour_spinner.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(time_frame, text="Minute:").grid(row=0, column=2, padx=5, pady=5)
        minute_spinner = ttk.Spinbox(time_frame, from_=0, to=59, textvariable=self.minute_var, width=4)
        minute_spinner.grid(row=0, column=3, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)

        ok_btn = ttk.Button(button_frame, text="OK", command=self.on_ok)
        ok_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)

        # Add some shortcuts
        ttk.Button(button_frame, text="Now", command=self.set_now).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Today 9:00", command=self.set_today_morning).pack(side=tk.LEFT, padx=5)

    def set_now(self):
        now = datetime.datetime.now()
        self.year_var.set(now.year)
        self.month_var.set(now.month)
        self.day_var.set(now.day)
        self.hour_var.set(now.hour)
        self.minute_var.set(now.minute)

    def set_today_morning(self):
        now = datetime.datetime.now()
        self.year_var.set(now.year)
        self.month_var.set(now.month)
        self.day_var.set(now.day)
        self.hour_var.set(9)
        self.minute_var.set(0)

    def on_ok(self):
        try:
            # Create datetime object from selected values
            self.result = datetime.datetime(
                self.year_var.get(),
                self.month_var.get(),
                self.day_var.get(),
                self.hour_var.get(),
                self.minute_var.get()
            )
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Invalid Date", str(e))

class TemplateDialog(tk.Toplevel):
    """Dialog for filling in template values"""
    def __init__(self, parent, template_name, placeholders):
        super().__init__(parent)
        self.title(f"Create Task from Template: {template_name}")
        self.result = None
        self.placeholders = placeholders

        # Set dialog properties
        self.geometry("400x300")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        # Create the form
        self.create_widgets()

        # Center on parent
        self.geometry(f"+{parent.winfo_rootx() + 50}+{parent.winfo_rooty() + 50}")

        # Wait for window to be destroyed
        self.wait_window()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Instruction label
        ttk.Label(main_frame, text="Fill in the values for this template:").pack(anchor="w", pady=(0, 10))

        # Scrollable frame for placeholder inputs
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)

        input_frame = ttk.Frame(canvas)
        # This line is important - it reconfigures the canvas scrollregion when the frame changes size
        input_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=input_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create variables to store input values
        self.placeholder_vars = {}

        # Add due date input - special case since most templates need it
        ttk.Label(input_frame, text="Due Date:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        due_date_frame = ttk.Frame(input_frame)
        due_date_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        self.placeholder_vars["due_date"] = tk.StringVar()
        due_entry = ttk.Entry(due_date_frame, textvariable=self.placeholder_vars["due_date"])
        due_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        date_btn = ttk.Button(due_date_frame, text="...", width=3,
                           command=lambda: self.select_date("due_date"))
        date_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # Add inputs for each placeholder
        for i, placeholder in enumerate(sorted(self.placeholders)):
            row = i + 1  # Start after due date
            ttk.Label(input_frame, text=f"{placeholder.replace('_', ' ').title()}:").grid(
                row=row, column=0, sticky="w", padx=5, pady=5)

            self.placeholder_vars[placeholder] = tk.StringVar()
            ttk.Entry(input_frame, textvariable=self.placeholder_vars[placeholder]).grid(
                row=row, column=1, sticky="ew", padx=5, pady=5)

        # Make input fields expandable
        input_frame.columnconfigure(1, weight=1)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        create_btn = ttk.Button(button_frame, text="Create Task", command=self.on_create)
        create_btn.pack(side=tk.RIGHT, padx=5)

        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)

    def select_date(self, field_name):
        # Show date picker
        date_dialog = DateTimeDialog(self, "Select Date")
        if date_dialog.result:
            # Set the date in YYYY-MM-DD format
            self.placeholder_vars[field_name].set(date_dialog.result.strftime("%Y-%m-%d"))

    def on_create(self):
        # Collect values from all placeholder variables
        self.result = {}
        for key, var in self.placeholder_vars.items():
            self.result[key] = var.get()

        # Close dialog
        self.destroy()

class TemplateManagerDialog(tk.Toplevel):
    """Dialog for managing templates"""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Template Manager")

        # Set dialog properties
        self.geometry("600x400")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        # Create the form
        self.create_widgets()

        # Center on parent
        self.geometry(f"+{parent.winfo_rootx() + 50}+{parent.winfo_rooty() + 50}")

        # Wait for window to be destroyed
        self.wait_window()

    def create_widgets(self):
        # Main layout with two panes
        paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left pane - template list
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=1)

        # Template list with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(list_frame, text="Templates").pack(anchor="w", pady=(0, 5))

        list_scroll = ttk.Scrollbar(list_frame)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.template_list = tk.Listbox(list_frame, activestyle="none",
                                       selectmode=tk.SINGLE,
                                       yscrollcommand=list_scroll.set)
        self.template_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scroll.config(command=self.template_list.yview)

        # Buttons for the template list
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=5)

        new_btn = ttk.Button(button_frame, text="New", command=self.new_template)
        new_btn.pack(side=tk.LEFT, padx=(0, 5))

        delete_btn = ttk.Button(button_frame, text="Delete", command=self.delete_template)
        delete_btn.pack(side=tk.LEFT)

        # Right pane - template editor
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=2)

        # Editor area
        editor_frame = ttk.LabelFrame(right_frame, text="Template Editor")
        editor_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Template name
        name_frame = ttk.Frame(editor_frame)
        name_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(name_frame, text="Template Name:").pack(side=tk.LEFT)
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(name_frame, textvariable=self.name_var)
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Template JSON editor
        json_frame = ttk.Frame(editor_frame)
        json_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        ttk.Label(json_frame, text="Template JSON:").pack(anchor="w")

        json_scroll_y = ttk.Scrollbar(json_frame)
        json_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        json_scroll_x = ttk.Scrollbar(json_frame, orient=tk.HORIZONTAL)
        json_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.json_text = tk.Text(json_frame, wrap=tk.NONE, height=10,
                              xscrollcommand=json_scroll_x.set,
                              yscrollcommand=json_scroll_y.set)
        self.json_text.pack(fill=tk.BOTH, expand=True)

        json_scroll_y.config(command=self.json_text.yview)
        json_scroll_x.config(command=self.json_text.xview)

        # Hint for template formatting
        hint_text = """
# Template Format Example:
{
    "description": "Task: {task_name}",
    "priority": "High",
    "category": "{category}",
    "notes": "Created from template.\nDetails: {details}"
}
""".strip()
        ttk.Label(editor_frame, text=hint_text, justify=tk.LEFT,
                font=("Courier", 9)).pack(fill=tk.X, padx=10, pady=(0, 10))

        # Buttons for the editor
        save_frame = ttk.Frame(right_frame)
        save_frame.pack(fill=tk.X)

        save_btn = ttk.Button(save_frame, text="Save Template", command=self.save_template)
        save_btn.pack(side=tk.RIGHT)

        # Load the templates
        self.load_templates()

        # Bind selection event
        self.template_list.bind("<<ListboxSelect>>", self.on_template_select)

    def load_templates(self):
        """Load templates into the list"""
        from task_manager.utils.templates import load_templates

        # Clear the list
        self.template_list.delete(0, tk.END)

        # Load templates
        self.templates = load_templates()

        # Add templates to list
        for i, name in enumerate(sorted(self.templates.keys())):
            self.template_list.insert(i, name)

        # Select first item if available
        if self.template_list.size() > 0:
            self.template_list.selection_set(0)
            self.template_list.event_generate("<<ListboxSelect>>")

    def on_template_select(self, event):
        """Handle template selection"""
        try:
            # Get selected template
            selection = self.template_list.curselection()
            if not selection:
                return

            template_name = self.template_list.get(selection[0])

            # Update the editor
            self.name_var.set(template_name)

            # Format the JSON for display
            import json
            formatted_json = json.dumps(self.templates[template_name], indent=4)

            # Update the text widget
            self.json_text.delete(1.0, tk.END)
            self.json_text.insert(tk.END, formatted_json)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load template: {str(e)}")

    def new_template(self):
        """Create a new template"""
        # Clear the editor
        self.name_var.set("New Template")
        self.json_text.delete(1.0, tk.END)

        # Insert template example
        self.json_text.insert(tk.END, """{
    "description": "New task from template",
    "priority": "Medium",
    "category": "Work",
    "notes": "Created from template."
}""")

    def delete_template(self):
        """Delete the selected template"""
        # Get selected template
        selection = self.template_list.curselection()
        if not selection:
            messagebox.showinfo("Info", "Please select a template to delete")
            return

        template_name = self.template_list.get(selection[0])

        # Ask for confirmation
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the template '{template_name}'?"
        )

        if confirm:
            try:
                # Delete the template
                from task_manager.utils.templates import delete_template
                delete_template(template_name)

                # Reload the templates
                self.load_templates()

                messagebox.showinfo("Success", f"Template '{template_name}' deleted successfully")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete template: {str(e)}")

    def save_template(self):
        """Save the current template"""
        template_name = self.name_var.get().strip()

        if not template_name:
            messagebox.showerror("Error", "Template name cannot be empty")
            return

        # Get JSON content
        try:
            import json
            json_content = self.json_text.get(1.0, tk.END).strip()
            try:
                template_data = json.loads(json_content)
            except json.JSONDecodeError as e:
                line_col = f"line {e.lineno}, column {e.colno}"
                messagebox.showerror("JSON Error", f"Invalid JSON format at {line_col}: {e.msg}")
                return

            # Save the template
            try:
                from task_manager.utils.templates import save_template
                save_template(template_name, template_data)
            except ImportError:
                messagebox.showerror("Error", "Could not import template utilities. Check your installation.")
                return
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save template: {str(e)}")
                return

            # Reload the templates
            self.load_templates()

            # Select the saved template
            for i in range(self.template_list.size()):
                if self.template_list.get(i) == template_name:
                    self.template_list.selection_set(i)
                    self.template_list.see(i)
                    self.template_list.event_generate("<<ListboxSelect>>")
                    break

            messagebox.showinfo("Success", f"Template '{template_name}' saved successfully")

        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")

class SimpleTaskManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")
        self.root.geometry("900x600")
        self.root.minsize(600, 400)

        # Set application icon if available
        try:
            if platform.system() == "Windows":
                self.root.iconbitmap("task_manager/resources/icon.ico")
            else:
                logo = tk.PhotoImage(file="task_manager/resources/icon.png")
                self.root.iconphoto(True, logo)
        except:
            pass  # Icon files not found, continue without them

        # Configure a more modern theme
        if platform.system() == "Darwin":  # macOS
            self.root.configure(bg="#f5f5f7")  # Light background similar to macOS
        else:
            self.root.configure(bg="#f0f0f0")  # Light gray for other platforms

        # Configure styles for the platform
        self.setup_styles()

        # Initialize variables needed by UI components
        self.selected_count = tk.StringVar(value="No tasks selected")

        # Create main layout
        self.create_layout()

        # Initialize task list by loading existing tasks
        self.tasks = load_tasks()
        self.refresh_task_list()

        # Start reminder service
        self.reminder_thread = start_reminder_service()

        # Make the layout responsive to window resizing
        self.configure_responsive_layout()

        # Load settings
        self.settings = load_settings()

        # Setup auto-save
        self.setup_autosave()

        # Bind window closing event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    # Settings Dialog Class - Inner class for SimpleTaskManagerGUI
    class SettingsDialog(tk.Toplevel):
        """Dialog for application settings"""
        def __init__(self, parent, settings):
            super().__init__(parent)
            self.title("Settings")
            self.settings = settings
            self.result = None

            # Set dialog properties
            self.geometry("450x500")
            self.resizable(True, True)
            self.transient(parent)
            self.grab_set()

            # Create the form
            self.create_widgets()

            # Center on parent
            self.geometry(f"+{parent.winfo_rootx() + 50}+{parent.winfo_rooty() + 50}")

            # Wait for window to be destroyed
            self.wait_window()

        def create_widgets(self):
            # Main container with padding
            container = ttk.Frame(self, padding="20")
            container.pack(fill=tk.BOTH, expand=True)

            # Create a header
            header_frame = ttk.Frame(container)
            header_frame.pack(fill=tk.X, pady=(0, 15))

            header_label = ttk.Label(header_frame, text="Application Settings",
                                   font=("Helvetica", 16, "bold"))
            header_label.pack(anchor="w")

            ttk.Separator(container).pack(fill=tk.X, pady=(0, 15))

            # Settings notebook with tabs
            notebook = ttk.Notebook(container)
            notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

            # General settings tab
            general_frame = ttk.Frame(notebook, padding=15)
            notebook.add(general_frame, text="General")

            # Auto-save settings
            ttk.Label(general_frame, text="Auto-save Interval (seconds):",
                    font=("Helvetica", 10, "bold")).grid(
                row=0, column=0, sticky="w", padx=5, pady=10)

            self.auto_save_var = tk.IntVar(value=self.settings.get("auto_save_interval", 300))
            auto_save_spinner = ttk.Spinbox(general_frame, from_=60, to=3600,
                                          textvariable=self.auto_save_var, width=6)
            auto_save_spinner.grid(row=0, column=1, sticky="w", padx=5, pady=10)

            # Theme settings
            ttk.Label(general_frame, text="Theme:", font=("Helvetica", 10, "bold")).grid(
                row=1, column=0, sticky="w", padx=5, pady=10)

            self.theme_var = tk.StringVar(value=self.settings.get("theme", "default"))
            themes = ["default", "light", "dark", "system"]
            theme_combo = ttk.Combobox(general_frame, textvariable=self.theme_var,
                                     values=themes, width=15, state="readonly")
            theme_combo.grid(row=1, column=1, sticky="w", padx=5, pady=10)

            # Confirmation dialog settings
            self.confirm_delete_var = tk.BooleanVar(value=self.settings.get("confirm_delete", True))
            confirm_check = ttk.Checkbutton(general_frame, text="Confirm before deleting tasks",
                                          variable=self.confirm_delete_var)
            confirm_check.grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=10)

            # Show status bar setting
            self.show_status_var = tk.BooleanVar(value=self.settings.get("show_status_bar", True))
            status_check = ttk.Checkbutton(general_frame, text="Show status bar",
                                         variable=self.show_status_var)
            status_check.grid(row=3, column=0, columnspan=2, sticky="w", padx=5, pady=10)

            # Color settings tab
            colors_frame = ttk.Frame(notebook, padding=15)
            notebook.add(colors_frame, text="Colors")

            # Priority colors
            ttk.Label(colors_frame, text="Priority Colors:",
                    font=("Helvetica", 10, "bold")).grid(
                row=0, column=0, sticky="w", padx=5, pady=10, columnspan=2)

            # High priority color
            ttk.Label(colors_frame, text="High Priority:").grid(
                row=1, column=0, sticky="w", padx=20, pady=5)

            self.high_color_var = tk.StringVar(value=self.settings.get("high_priority_color", "#ff0000"))
            high_color_frame = ttk.Frame(colors_frame)
            high_color_frame.grid(row=1, column=1, sticky="w", padx=5, pady=5)

            high_color_preview = tk.Frame(high_color_frame, width=20, height=20,
                                       bg=self.high_color_var.get())
            high_color_preview.pack(side=tk.LEFT, padx=(0, 5))

            high_color_btn = ttk.Button(high_color_frame, text="Choose...",
                                      command=lambda: self.choose_color("high_priority_color", high_color_preview))
            high_color_btn.pack(side=tk.LEFT)

            # Medium priority color
            ttk.Label(colors_frame, text="Medium Priority:").grid(
                row=2, column=0, sticky="w", padx=20, pady=5)

            self.medium_color_var = tk.StringVar(value=self.settings.get("medium_priority_color", "#0000ff"))
            medium_color_frame = ttk.Frame(colors_frame)
            medium_color_frame.grid(row=2, column=1, sticky="w", padx=5, pady=5)

            medium_color_preview = tk.Frame(medium_color_frame, width=20, height=20,
                                         bg=self.medium_color_var.get())
            medium_color_preview.pack(side=tk.LEFT, padx=(0, 5))

            medium_color_btn = ttk.Button(medium_color_frame, text="Choose...",
                                        command=lambda: self.choose_color("medium_priority_color", medium_color_preview))
            medium_color_btn.pack(side=tk.LEFT)

            # Low priority color
            ttk.Label(colors_frame, text="Low Priority:").grid(
                row=3, column=0, sticky="w", padx=20, pady=5)

            self.low_color_var = tk.StringVar(value=self.settings.get("low_priority_color", "#008000"))
            low_color_frame = ttk.Frame(colors_frame)
            low_color_frame.grid(row=3, column=1, sticky="w", padx=5, pady=5)

            low_color_preview = tk.Frame(low_color_frame, width=20, height=20,
                                      bg=self.low_color_var.get())
            low_color_preview.pack(side=tk.LEFT, padx=(0, 5))

            low_color_btn = ttk.Button(low_color_frame, text="Choose...",
                                     command=lambda: self.choose_color("low_priority_color", low_color_preview))
            low_color_btn.pack(side=tk.LEFT)

            # Reset colors button
            reset_btn = ttk.Button(colors_frame, text="Reset to Default Colors",
                                 command=self.reset_colors)
            reset_btn.grid(row=4, column=0, columnspan=2, pady=20)

            # Buttons
            button_frame = ttk.Frame(container)
            button_frame.pack(fill=tk.X, pady=(10, 0))

            save_btn = ttk.Button(button_frame, text="Save", command=self.save_settings)
            save_btn.pack(side=tk.RIGHT, padx=5)

            cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.destroy)
            cancel_btn.pack(side=tk.RIGHT, padx=5)

        def choose_color(self, setting_key, preview_widget):
            """Open color chooser and update preview"""
            initial_color = getattr(self, f"{setting_key}_var").get()
            color = colorchooser.askcolor(initial_color, title=f"Choose {setting_key.replace('_', ' ').title()}")

            if color and color[1]:  # If a color was selected
                getattr(self, f"{setting_key}_var").set(color[1])
                preview_widget.configure(bg=color[1])

        def reset_colors(self):
            """Reset colors to default values"""
            default_colors = {
                "high_priority_color": "#ff0000",
                "medium_priority_color": "#0000ff",
                "low_priority_color": "#008000"
            }

            # Update color variables and previews
            for widget in self.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Notebook):
                            for tab in child.winfo_children():
                                if "Colors" in str(tab):
                                    for i, row in enumerate(tab.winfo_children()):
                                        if isinstance(row, ttk.Frame) and i > 0:
                                            for frame in row.winfo_children():
                                                if isinstance(frame, tk.Frame) and len(frame.winfo_children()) > 0:
                                                    preview = frame.winfo_children()[0]
                                                    if i == 1:
                                                        preview.configure(bg=default_colors["high_priority_color"])
                                                        self.high_color_var.set(default_colors["high_priority_color"])
                                                    elif i == 2:
                                                        preview.configure(bg=default_colors["medium_priority_color"])
                                                        self.medium_color_var.set(default_colors["medium_priority_color"])
                                                    elif i == 3:
                                                        preview.configure(bg=default_colors["low_priority_color"])
                                                        self.low_color_var.set(default_colors["low_priority_color"])

        def save_settings(self):
            """Save settings and close the dialog"""
            self.result = {
                "auto_save_interval": self.auto_save_var.get(),
                "theme": self.theme_var.get(),
                "confirm_delete": self.confirm_delete_var.get(),
                "show_status_bar": self.show_status_var.get(),
                "high_priority_color": self.high_color_var.get(),
                "medium_priority_color": self.medium_color_var.get(),
                "low_priority_color": self.low_color_var.get()
            }
            self.destroy()

    def setup_styles(self):
        # Configure ttk styles
        style = ttk.Style()

        # Use a modern theme if available
        try:
            if platform.system() == "Windows":
                style.theme_use("vista")
            elif platform.system() == "Darwin":  # macOS
                style.theme_use("aqua")
            else:
                style.theme_use("clam")
        except tk.TclError:
            try:
                style.theme_use("clam")  # Fallback theme
            except tk.TclError:
                pass  # Use default theme if nothing else works

        # Custom styles for a more modern look
        bg_color = "#f5f5f7" if platform.system() == "Darwin" else "#f0f0f0"

        # Improve heading contrast with darker colors
        style.configure("TLabel", foreground="#121212")  # Dark text color for all labels

        # Make heading text more visible
        style.configure("Header.TLabel",
                       font=('Helvetica', 18, 'bold'),
                       foreground="#000000")  # Pure black for headers

        # Make subheader text more visible
        style.configure("Subheader.TLabel",
                       font=('Helvetica', 12, 'bold'),
                       foreground="#222222")  # Very dark gray for subheaders

        # Configure Treeview with more modern styling
        style.configure("Treeview",
                        rowheight=30,  # Increased row height
                        font=('Helvetica', 10),
                        background=bg_color,
                        fieldbackground=bg_color)

        style.map('Treeview',
                  background=[('selected', '#4a6984')],  # Darker blue selection
                  foreground=[('selected', 'white')])    # White text when selected

        style.configure("Treeview.Heading",
                        font=('Helvetica', 10, 'bold'),
                        background="#d0d0d0",  # Darker header background (was #e0e0e0)
                        foreground="#000000",  # Black header text
                        relief="flat")

        # Make section headers stand out more
        style.configure("Bold.TLabelframe.Label",
                      font=('Helvetica', 10, 'bold'),
                      foreground="#000000")  # Black for section headers

        style.map("Treeview.Heading",
                  background=[('active', '#c0c0c0')])  # Darker when active

        def configure_responsive_layout(self):
            """Configure the main window for responsive layout"""
            # Make the root window's columns and rows expandable
            self.root.grid_columnconfigure(0, weight=1)
            self.root.grid_rowconfigure(0, weight=1)

            # Make the main frame expand with window
            self.main_frame.pack_propagate(False)

            # Ensure treeview expands with window
            for i in range(3):  # Add weight to all important columns
                self.main_frame.columnconfigure(i, weight=1)
                self.main_frame.rowconfigure(i, weight=1)

    def create_layout(self):
        # Create main frame with menu bar
        self.setup_menu()

        # Main content frame with improved styling
        self.main_frame = ttk.Frame(self.root, padding="10 10 10 10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create header frame with more spacing
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))

        # Header title with larger, bolder text and better contrast
        title_label = ttk.Label(
            header_frame,
            text="Task Manager",
            style="Header.TLabel"  # Use our custom header style
        )
        title_label.pack(side=tk.LEFT)

        # Add task button with improved styling
        add_btn = ttk.Button(
            header_frame,
            text="➕ Add Task",
            command=self.add_task,
            style="Primary.TButton"
        )
        add_btn.pack(side=tk.RIGHT, padx=(0, 5))
        Tooltip(add_btn, "Create a new task")

        # AI Assistant button
        ai_btn = ttk.Button(
            header_frame,
            text="🤖 AI Assistant",
            command=self.show_ai_assistant
        )
        ai_btn.pack(side=tk.RIGHT, padx=(0, 5))
        Tooltip(ai_btn, "Open AI Assistant")

        # Command prompt button
        cmd_btn = ttk.Button(
            header_frame,
            text="⌨️ Terminal",
            command=self.show_command_prompt
        )
        cmd_btn.pack(side=tk.RIGHT, padx=(0, 5))
        Tooltip(cmd_btn, "Open terminal interface")

        # Settings button
        settings_btn = ttk.Button(
            header_frame,
            text="⚙️ Settings",
            command=self.show_settings
        )
        settings_btn.pack(side=tk.RIGHT, padx=(0, 5))
        Tooltip(settings_btn, "Configure application settings")

        # Create the task list view
        self.create_task_list()

        # Add status bar
        self.status_bar = ttk.Label(self.main_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def search_focus(self):
        """Set focus to the search box"""
        for child in self.main_frame.winfo_children():
            if isinstance(child, ttk.Frame):
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, ttk.LabelFrame) and grandchild.winfo_children():
                        if "Search" in grandchild.cget("text"):
                            # Found the search frame, now find the entry widget
                            for item in grandchild.winfo_children()[0].winfo_children():
                                if isinstance(item, ttk.Entry):
                                    item.focus_set()
                                    return

    def save_tasks_manually(self):
        """Manually save tasks"""
        from task_manager.utils.storage import save_with_recovery

        if self.tasks:
            if save_with_recovery(self.tasks):
                self.last_save_time = time.time()
                self.status_bar.config(text="Tasks saved successfully")
            else:
                self.status_bar.config(text="Failed to save tasks")

    def show_help(self):
        """Show keyboard shortcuts and help"""
        help_text = """
Task Manager Keyboard Shortcuts:

Ctrl+N: Add new task
Ctrl+E: Edit selected task
Ctrl+D: Delete selected task
Ctrl+F: Focus search box
Ctrl+S: Save tasks
F5: Refresh task list
F1: Show this help

Context menu is available via right-click on any task.
        """
        messagebox.showinfo("Keyboard Shortcuts", help_text)

    def setup_menu(self):
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Task", command=self.add_task)

        # Add template submenu
        template_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="New from Template", menu=template_menu)
        self.update_template_menu(template_menu)

        file_menu.add_separator()
        file_menu.add_command(label="Import", command=self.import_tasks)
        file_menu.add_command(label="Export", command=self.export_tasks)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Edit Selected Task", command=self.edit_task)
        edit_menu.add_command(label="Delete Selected Task", command=self.delete_task)
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all_tasks)
        edit_menu.add_command(label="Deselect All", command=self.deselect_all_tasks)
        edit_menu.add_separator()
        edit_menu.add_command(label="Settings", command=self.show_settings)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh", command=self.refresh_task_list)
        view_menu.add_separator()
        view_menu.add_command(label="Manage Templates", command=self.manage_templates)

        # Tools menu (new)
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Command Shell", command=self.launch_command_shell)
        tools_menu.add_command(label="Interactive CLI", command=self.launch_interactive_cli)
        tools_menu.add_separator()
        tools_menu.add_command(label="AI Assistant", command=self.show_ai_assistant)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def update_template_menu(self, template_menu):
        """Update the template menu with available templates"""
        # Clear existing menu items
        template_menu.delete(0, 'end')

        # Load templates
        from task_manager.utils.templates import load_templates
        templates = load_templates()

        if not templates:
            template_menu.add_command(label="No templates available", state=tk.DISABLED)
            return

        # Add each template to the menu
        for template_name in sorted(templates.keys()):
            # Use default parameter to capture the current value of template_name
            template_menu.add_command(
                label=template_name,
                command=lambda name=template_name: self.create_from_template(name)
            )

    def create_from_template(self, template_name):
        """Create a new task from the selected template"""
        from task_manager.utils.templates import load_templates, create_task_from_template
        import re

        templates = load_templates()
        if template_name not in templates:
            messagebox.showerror("Error", f"Template '{template_name}' not found.")
            return

        template = templates[template_name]

        # Find all placeholders in the template
        placeholders = set()
        for key, value in template.items():
            if isinstance(value, str):
                # Find all placeholders like {variable_name}
                matches = re.findall(r'\{([^}]+)\}', value)
                placeholders.update(matches)

        # Create dialog to fill in template values
        dialog = TemplateDialog(self.root, template_name, list(placeholders))

        if dialog.result:
            try:
                # Create a task ID
                task_id = 1 if not self.tasks else max(t.id for t in self.tasks) + 1

                # Get task data from template with placeholders filled in
                task_data = create_task_from_template(template_name, dialog.result)

                # Create a new task with the correct ID
                new_task = Task(task_id=task_id, description=task_data.get('description', 'Task from template'))

                # Copy template data to task
                for key, value in task_data.items():
                    if key != 'task_id' and key != 'id':  # Skip ID fields - we already set it
                        setattr(new_task, key, value)

                # Add due date if provided
                if 'due_date' in dialog.result and dialog.result['due_date']:
                    new_task.due_date = dialog.result['due_date']

                # Add to task list
                self.tasks.append(new_task)

                # Save and refresh
                save_tasks(self.tasks)
                self.refresh_task_list()

                # Show success message
                self.status_bar.config(text=f"Added task from template: {new_task.description}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to create task from template: {str(e)}")
                import traceback
                traceback.print_exc()  # Print traceback for debugging

    def launch_interactive_cli(self):
        """Launch the interactive CLI in a new terminal window"""
        import subprocess
        import platform
        import os

        try:
            # Different commands for different platforms
            if platform.system() == "Windows":
                # Windows - use start cmd
                subprocess.Popen(['start', 'cmd', '/k', 'task-cli interactive'], shell=True)
            elif platform.system() == "Darwin":  # macOS
                # Check if we can use Terminal or iTerm
                terminal_app = 'Terminal'
                if os.path.exists('/Applications/iTerm.app'):
                    terminal_app = 'iTerm'

                applescript = f'''
                tell application "{terminal_app}"
                    activate
                    do script "task-cli interactive"
                end tell
                '''
                subprocess.Popen(['osascript', '-e', applescript])
            else:
                # Linux - try common terminals
                terminals = ['x-terminal-emulator', 'gnome-terminal', 'xterm', 'konsole']

                for term in terminals:
                    try:
                        subprocess.Popen([term, '-e', 'task-cli interactive'])
                        break
                    except FileNotFoundError:
                        continue
                else:
                    # If no terminal is found, show an error
                    messagebox.showerror("Error", "No suitable terminal found. Please install xterm or gnome-terminal.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch interactive CLI: {str(e)}")

            # As a fallback, show instructions for manual launch
            messagebox.showinfo("Manual Launch",
                              "To manually launch the interactive CLI:\n"
                              "1. Open a terminal or command prompt\n"
                              "2. Type 'task-cli interactive' and press Enter")

    def launch_command_shell(self):
        """Launch a command shell for the task manager"""
        # This would be implemented to create a custom command shell window
        messagebox.showinfo("Feature Coming Soon",
                          "The command shell feature will be available in a future update.")

    def manage_templates(self):
        """Open the template manager dialog"""
        TemplateManagerDialog(self.root)
        # Update the template menu after managing templates
        template_menu = self.root.nametowidget(self.root.winfo_children()[0]).winfo_children()[0]
        self.update_template_menu(template_menu)

    def show_ai_assistant(self):
        """Show the AI assistant dialog"""
        show_ai_assistant(self.root)

    def show_command_prompt(self):
        """Show the command prompt interface"""
        self.launch_interactive_cli()

    # Add the imported methods to the class
    create_task_list = create_task_list
    on_task_select = on_task_select
    select_all_tasks = select_all_tasks
    deselect_all_tasks = deselect_all_tasks
    refresh_task_list = refresh_task_list
    matches_filters = matches_filters
    delete_task = delete_task
    get_selected_task = get_selected_task
    on_task_double_click = on_task_double_click
    create_context_menu = create_context_menu
    show_context_menu = show_context_menu
    add_custom_category = add_custom_category

    def edit_task(self):
        """Edit the selected task"""
        # Get the selected task
        task = self.get_selected_task()
        if not task:
            messagebox.showinfo("Info", "Please select a task to edit")
            return

        # Show the task editor
        editor = TaskEditor(self.root, task, "Edit Task")

        if editor.result:
            # Update task properties
            for key, value in editor.result.items():
                setattr(task, key, value)

            # Save and refresh
            save_tasks(self.tasks)
            self.refresh_task_list()

            # Show success message
            self.status_bar.config(text=f"Updated task: {task.description}")

    def toggle_complete(self):
        """Toggle completion status of selected tasks"""
        selected_items = self.task_tree.selection()
        if not selected_items:
            messagebox.showinfo("Info", "Please select a task to toggle completion")
            return

        # Toggle completion for all selected tasks
        for item_id in selected_items:
            task_id = int(self.task_tree.item(item_id, "values")[0])
            task = next((t for t in self.tasks if t.id == task_id), None)

            if task:
                task.completed = not task.completed
                # If completed, set progress to 100%
                if task.completed:
                    task.progress = 100

        # Save and refresh
        save_tasks(self.tasks)
        self.refresh_task_list()

        # Show success message
        current_reminder = None
        if task.reminder_time:
            try:
                current_reminder = datetime.datetime.fromtimestamp(float(task.reminder_time))
            except (ValueError, TypeError):
                current_reminder = None

        # Show date/time dialog
        date_dialog = DateTimeDialog(self.root, "Set Reminder Time", current_reminder or datetime.datetime.now())

        if date_dialog.result:
            # Set the reminder time
            task.set_reminder(date_dialog.result)

            # Save and show success message
            save_tasks(self.tasks)
            messagebox.showinfo("Reminder Set",
                               f"Reminder set for {date_dialog.result.strftime('%Y-%m-%d %H:%M')}")

    def add_task(self):
        """Add a new task"""
        # Create an empty task for the editor
        new_task = Task(task_id=1, description="")

        # Show the task editor
        editor = TaskEditor(self.root, new_task, "Add Task")

        if editor.result:
            # Generate a new task ID
            task_id = 1
            if self.tasks:
                task_id = max(task.id for task in self.tasks) + 1

            # Create a new task with the result from the editor
            new_task = Task(task_id=task_id, description=editor.result['description'])

            # Set additional properties
            for key, value in editor.result.items():
                if key != 'description':  # Already set in constructor
                    setattr(new_task, key, value)

            # Add to task list
            self.tasks.append(new_task)

            # Save and refresh
            save_tasks(self.tasks)
            self.refresh_task_list()

            # Show success message
            self.status_bar.config(text=f"Added task: {new_task.description}")

    def import_tasks(self):
        """Import tasks from a JSON file."""
        from tkinter.filedialog import askopenfilename
        file_path = askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            try:
                imported_tasks = import_from_json(file_path)
                self.tasks.extend(imported_tasks)
                save_tasks(self.tasks)
                self.refresh_task_list()
                messagebox.showinfo("Success", f"Imported {len(imported_tasks)} tasks successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import tasks: {str(e)}")

    def export_tasks(self):
        """Export tasks to a JSON file."""
        from tkinter.filedialog import asksaveasfilename
        file_path = asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if file_path:
            try:
                export_to_json(self.tasks, file_path)
                messagebox.showinfo("Success", "Tasks exported successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export tasks: {str(e)}")

    def show_about(self):
        """Show the About dialog"""
        about_text = f"""
{APP_NAME} v{VERSION}
{COPYRIGHT}

Task Manager is a simple application for managing your tasks.
You can add, edit, delete, and organize tasks with ease.

For more information, visit our website or contact support.
"""
        messagebox.showinfo("About Task Manager", about_text)

    def setup_autosave(self):
        """Setup auto-save functionality"""
        self.last_save_time = time.time()
        self.auto_save_interval = self.settings.get("auto_save_interval", 300)  # Default: 5 minutes
        self.start_autosave_timer()

    def start_autosave_timer(self):
        """Start the auto-save timer"""
        self.auto_save_timer = threading.Timer(self.auto_save_interval, self.auto_save)
        self.auto_save_timer.start()

    def auto_save(self):
        """Automatically save tasks"""
        if self.tasks:
            from task_manager.utils.storage import save_with_recovery
            if save_with_recovery(self.tasks):
                self.last_save_time = time.time()
                self.status_bar.config(text="Tasks auto-saved successfully")
            else:
                self.status_bar.config(text="Failed to auto-save tasks")

        # Restart the timer
        self.start_autosave_timer()

    def on_closing(self):
        """Handle window closing event"""
        if self.auto_save_timer:
            self.auto_save_timer.cancel()

        # Save tasks before closing
        save_tasks(self.tasks)

        # Close the application
        self.root.destroy()

    def show_settings(self):
        """Show the settings dialog"""
        dialog = self.SettingsDialog(self.root, self.settings)
        if dialog.result:
            self.settings.update(dialog.result)
            save_settings(self.settings)
            self.apply_settings()

    def apply_settings(self):
        """Apply the updated settings to the application"""
        # Update auto-save interval if it was changed
        if self.auto_save_timer:
            self.auto_save_timer.cancel()
        self.auto_save_interval = self.settings.get("auto_save_interval", 300)
        self.start_autosave_timer()

        # Apply theme settings if needed
        theme = self.settings.get("theme", "default")
        if theme != "default":
            # Apply theme-specific settings
            try:
                if theme == "dark":
                    self.apply_dark_theme()
                elif theme == "light":
                    self.apply_light_theme()
                elif theme == "system":
                    self.apply_system_theme()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to apply theme: {str(e)}")

        # Apply status bar visibility
        show_status = self.settings.get("show_status_bar", True)
        if show_status:
            self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        else:
            self.status_bar.pack_forget()

        # Apply priority colors
        self.refresh_task_list()

        # Show confirmation
        self.status_bar.config(text="Settings applied successfully")

    def apply_dark_theme(self):
        """Apply dark theme to the application"""
        style = ttk.Style()
        style.configure(".", background="#2e2e2e", foreground="#e0e0e0")
        style.configure("Treeview", background="#3a3a3a", fieldbackground="#3a3a3a", foreground="#e0e0e0")
        style.map('Treeview', background=[('selected', '#505050')], foreground=[('selected', '#ffffff')])
        style.configure("TLabel", background="#2e2e2e", foreground="#e0e0e0")
        style.configure("TButton", background="#3a3a3a", foreground="#e0e0e0")
        style.configure("TFrame", background="#2e2e2e")
        self.root.configure(bg="#2e2e2e")
        self.main_frame.configure(background="#2e2e2e")

    def apply_light_theme(self):
        """Apply light theme to the application"""
        style = ttk.Style()
        style.configure(".", background="#f5f5f7", foreground="#121212")
        style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff", foreground="#121212")
        style.map('Treeview', background=[('selected', '#4a6984')], foreground=[('selected', '#ffffff')])
        style.configure("TLabel", background="#f5f5f7", foreground="#121212")
        style.configure("TButton", background="#e0e0e0", foreground="#121212")
        style.configure("TFrame", background="#f5f5f7")
        self.root.configure(bg="#f5f5f7")
        self.main_frame.configure(background="#f5f5f7")

    def apply_system_theme(self):
        """Apply system theme to the application"""
        # This would typically check the system preference and apply appropriate theme
        if platform.system() == "Darwin":  # macOS
            self.apply_light_theme()
        elif platform.system() == "Windows":
            # Try to detect Windows dark/light mode
            try:
                import winreg
                registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                if value == 0:
                    self.apply_dark_theme()
                else:
                    self.apply_light_theme()
            except:
                self.apply_light_theme()  # Default to light if detection fails
        else:
            self.apply_light_theme()  # Default to light for other platforms

# Run the application if this is the main module
if __name__ == "__main__":
    launch_simple_gui())