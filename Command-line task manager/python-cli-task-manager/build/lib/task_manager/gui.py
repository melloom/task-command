import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, colorchooser
from tkinter import font as tkfont
from task_manager.utils.storage import load_tasks, save_tasks
from task_manager.models.task import Task
import datetime

class EnhancedTaskDialog(simpledialog.Dialog):
    def __init__(self, parent, title, task=None):
        self.task = task
        self.result = None
        super().__init__(parent, title)

    def body(self, master):
        # Description
        tk.Label(master, text="Description:").grid(row=0, column=0, sticky="w", pady=5)
        self.description_entry = tk.Entry(master, width=40)
        if self.task:
            self.description_entry.insert(0, self.task.description)
        self.description_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Priority
        tk.Label(master, text="Priority:").grid(row=1, column=0, sticky="w", pady=5)
        self.priority_var = tk.StringVar(value="Medium" if not self.task else self.task.priority)
        priorities = ["Low", "Medium", "High"]
        self.priority_combo = ttk.Combobox(master, textvariable=self.priority_var, values=priorities, state="readonly", width=10)
        self.priority_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Due Date
        tk.Label(master, text="Due Date:").grid(row=2, column=0, sticky="w", pady=5)
        self.due_date_frame = tk.Frame(master)
        self.due_date_frame.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        current_date = datetime.datetime.now()
        self.day_var = tk.StringVar(value=str(current_date.day))
        self.month_var = tk.StringVar(value=str(current_date.month))
        self.year_var = tk.StringVar(value=str(current_date.year))

        if self.task and self.task.due_date:
            try:
                due_date = datetime.datetime.strptime(self.task.due_date, "%Y-%m-%d")
                self.day_var.set(str(due_date.day))
                self.month_var.set(str(due_date.month))
                self.year_var.set(str(due_date.year))
            except:
                pass

        self.day_entry = ttk.Combobox(self.due_date_frame, textvariable=self.day_var, values=[str(i) for i in range(1, 32)], width=3)
        self.month_entry = ttk.Combobox(self.due_date_frame, textvariable=self.month_var, values=[str(i) for i in range(1, 13)], width=3)
        self.year_entry = ttk.Combobox(self.due_date_frame, textvariable=self.year_var, values=[str(current_date.year + i) for i in range(-1, 6)], width=6)

        self.day_entry.pack(side=tk.LEFT, padx=2)
        tk.Label(self.due_date_frame, text="/").pack(side=tk.LEFT)
        self.month_entry.pack(side=tk.LEFT, padx=2)
        tk.Label(self.due_date_frame, text="/").pack(side=tk.LEFT)
        self.year_entry.pack(side=tk.LEFT, padx=2)

        self.has_due_date_var = tk.BooleanVar(value=bool(self.task and self.task.due_date))
        self.has_due_date_cb = tk.Checkbutton(self.due_date_frame, text="Enable", variable=self.has_due_date_var)
        self.has_due_date_cb.pack(side=tk.LEFT, padx=10)

        # Tags
        tk.Label(master, text="Tags:").grid(row=3, column=0, sticky="w", pady=5)
        self.tags_entry = tk.Entry(master, width=40)
        if self.task and self.task.tags:
            self.tags_entry.insert(0, ", ".join(self.task.tags))
        self.tags_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # Notes
        tk.Label(master, text="Notes:").grid(row=4, column=0, sticky="nw", pady=5)
        self.notes_text = tk.Text(master, width=40, height=5)
        if self.task and self.task.notes:
            self.notes_text.insert("1.0", self.task.notes)
        self.notes_text.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        # Category
        tk.Label(master, text="Category:").grid(row=5, column=0, sticky="w", pady=5)
        self.category_entry = tk.Entry(master, width=20)
        if self.task and hasattr(self.task, 'category') and self.task.category:
            self.category_entry.insert(0, self.task.category)
        self.category_entry.grid(row=5, column=1, padx=5, pady=5, sticky="w")

        # Color picker
        tk.Label(master, text="Color:").grid(row=6, column=0, sticky="w", pady=5)
        self.color_frame = tk.Frame(master)
        self.color_frame.grid(row=6, column=1, sticky="w", padx=5, pady=5)

        self.task_color = "#4287f5" if not self.task or not hasattr(self.task, 'color') else self.task.color
        self.color_btn = tk.Button(self.color_frame, bg=self.task_color, width=3, height=1, command=self.choose_color)
        self.color_btn.pack(side=tk.LEFT, padx=5)

        return self.description_entry  # Initial focus

    def choose_color(self):
        color = colorchooser.askcolor(initialcolor=self.task_color)
        if color[1]:
            self.task_color = color[1]
            self.color_btn.config(bg=self.task_color)

    def validate(self):
        if not self.description_entry.get().strip():
            messagebox.showerror("Error", "Description cannot be empty")
            return False
        return True

    def apply(self):
        description = self.description_entry.get().strip()
        priority = self.priority_var.get()

        due_date = None
        if self.has_due_date_var.get():
            try:
                day = int(self.day_var.get())
                month = int(self.month_var.get())
                year = int(self.year_var.get())
                due_date = f"{year}-{month:02d}-{day:02d}"
            except:
                messagebox.showwarning("Warning", "Invalid date format. Due date will not be set.")

        tags = [tag.strip() for tag in self.tags_entry.get().split(",") if tag.strip()]
        notes = self.notes_text.get("1.0", tk.END).strip()
        category = self.category_entry.get().strip()

        self.result = {
            "description": description,
            "priority": priority,
            "due_date": due_date,
            "tags": tags,
            "notes": notes,
            "category": category,
            "color": self.task_color
        }

class TaskManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager Pro")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Set theme and fonts
        self.style = ttk.Style()
        self.style.theme_use('clam')  # 'clam', 'alt', 'default', 'classic'

        self.title_font = tkfont.Font(family="Helvetica", size=14, weight="bold")
        self.header_font = tkfont.Font(family="Helvetica", size=12, weight="bold")
        self.normal_font = tkfont.Font(family="Helvetica", size=10)

        # Custom colors
        self.bg_color = "#f5f5f5"
        self.accent_color = "#4287f5"
        self.light_accent = "#e6f0ff"

        # Configure styles
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TButton", font=self.normal_font, padding=6)
        self.style.configure("TLabel", font=self.normal_font, background=self.bg_color)
        self.style.configure("Header.TLabel", font=self.header_font, background=self.bg_color)
        self.style.configure("Title.TLabel", font=self.title_font, background=self.bg_color, foreground=self.accent_color)

        self.root.configure(bg=self.bg_color)

        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10 10 10 10", style="TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Title and menu
        self.title_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.title_frame.pack(fill=tk.X, pady=(0, 10))

        self.title_label = ttk.Label(self.title_frame, text="Task Manager Pro", style="Title.TLabel")
        self.title_label.pack(side=tk.LEFT, padx=5)

        # Filter options
        self.filter_frame = ttk.Frame(self.title_frame, style="TFrame")
        self.filter_frame.pack(side=tk.RIGHT, padx=5)

        ttk.Label(self.filter_frame, text="Filter:", style="TLabel").pack(side=tk.LEFT, padx=5)

        self.filter_var = tk.StringVar(value="All")
        self.filter_combo = ttk.Combobox(self.filter_frame, textvariable=self.filter_var,
                                         values=["All", "Active", "Completed", "High Priority", "Due Soon"],
                                         width=12, state="readonly")
        self.filter_combo.pack(side=tk.LEFT, padx=5)
        self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_tasks())

        # Search
        self.search_frame = ttk.Frame(self.title_frame, style="TFrame")
        self.search_frame.pack(side=tk.RIGHT, padx=5)

        ttk.Label(self.search_frame, text="Search:", style="TLabel").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.refresh_tasks())
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var, width=15)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        # Create task list with Treeview instead of Listbox
        self.tree_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Create scrollbar
        self.tree_scroll = ttk.Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure treeview
        self.task_tree = ttk.Treeview(self.tree_frame, columns=("ID", "Description", "Priority", "Due Date", "Category", "Tags"),
                                     show="headings", yscrollcommand=self.tree_scroll.set)

        # Configure scrollbar
        self.tree_scroll.config(command=self.task_tree.yview)

        # Configure columns
        self.task_tree.column("ID", width=50, anchor=tk.CENTER)
        self.task_tree.column("Description", width=250, anchor=tk.W)
        self.task_tree.column("Priority", width=80, anchor=tk.CENTER)
        self.task_tree.column("Due Date", width=100, anchor=tk.CENTER)
        self.task_tree.column("Category", width=100, anchor=tk.W)
        self.task_tree.column("Tags", width=150, anchor=tk.W)

        # Configure headers
        self.task_tree.heading("ID", text="ID")
        self.task_tree.heading("Description", text="Description")
        self.task_tree.heading("Priority", text="Priority")
        self.task_tree.heading("Due Date", text="Due Date")
        self.task_tree.heading("Category", text="Category")
        self.task_tree.heading("Tags", text="Tags")

        self.task_tree.pack(fill=tk.BOTH, expand=True)

        # Create detail panel
        self.detail_frame = ttk.Frame(self.main_frame, style="TFrame", padding="5 5 5 5")
        self.detail_frame.pack(fill=tk.X, pady=5)

        self.detail_label = ttk.Label(self.detail_frame, text="Select a task to view details", style="Header.TLabel")
        self.detail_label.pack(anchor=tk.W, pady=5)

        self.notes_text = tk.Text(self.detail_frame, height=3, width=50, wrap=tk.WORD, state=tk.DISABLED)
        self.notes_text.pack(fill=tk.X, pady=5)

        # Create buttons frame
        self.button_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.button_frame.pack(fill=tk.X, pady=10)

        # Add task button
        self.add_button = ttk.Button(self.button_frame, text="Add Task", command=self.add_task)
        self.add_button.pack(side=tk.LEFT, padx=5)

        # Edit task button
        self.edit_button = ttk.Button(self.button_frame, text="Edit Task", command=self.edit_task)
        self.edit_button.pack(side=tk.LEFT, padx=5)

        # Complete task button
        self.complete_button = ttk.Button(self.button_frame, text="Mark Complete", command=self.complete_task)
        self.complete_button.pack(side=tk.LEFT, padx=5)

        # Delete task button
        self.delete_button = ttk.Button(self.button_frame, text="Delete Task", command=self.delete_task)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        # Statistics frame
        self.stats_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.stats_frame.pack(fill=tk.X, pady=5)

        self.stats_label = ttk.Label(self.stats_frame, text="", style="TLabel")
        self.stats_label.pack(side=tk.LEFT, padx=5)

        # Event handlers
        self.task_tree.bind("<ButtonRelease-1>", self.on_task_select)

        # Load tasks
        self.tasks = []
        self.refresh_tasks()

    def update_stats(self):
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task.completed)
        active = total - completed
        high_priority = sum(1 for task in self.tasks if hasattr(task, 'priority') and task.priority == "High" and not task.completed)

        stats_text = f"Total: {total} tasks | Active: {active} | Completed: {completed} | High Priority: {high_priority}"
        self.stats_label.config(text=stats_text)

    def on_task_select(self, event):
        selected_items = self.task_tree.selection()
        if not selected_items:
            return

        item_id = selected_items[0]
        task_id = int(self.task_tree.item(item_id, "values")[0])

        task = next((t for t in self.tasks if t.id == task_id), None)
        if not task:
            return

        # Update details panel
        self.detail_label.config(text=f"Task #{task.id}: {task.description}")

        self.notes_text.config(state=tk.NORMAL)
        self.notes_text.delete(1.0, tk.END)
        if hasattr(task, 'notes') and task.notes:
            self.notes_text.insert(tk.END, task.notes)
        else:
            self.notes_text.insert(tk.END, "No notes available.")
        self.notes_text.config(state=tk.DISABLED)

    def refresh_tasks(self):
        # Clear current tree
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)

        # Load tasks
        self.tasks = load_tasks()

        if not self.tasks:
            self.update_stats()
            return

        # Apply filter
        filter_type = self.filter_var.get()
        search_text = self.search_var.get().lower()

        filtered_tasks = self.tasks

        if filter_type == "Active":
            filtered_tasks = [t for t in filtered_tasks if not t.completed]
        elif filter_type == "Completed":
            filtered_tasks = [t for t in filtered_tasks if t.completed]
        elif filter_type == "High Priority":
            filtered_tasks = [t for t in filtered_tasks if hasattr(t, 'priority') and t.priority == "High"]
        elif filter_type == "Due Soon":
            today = datetime.datetime.now().date()
            one_week_later = today + datetime.timedelta(days=7)

            def is_due_soon(task):
                if not hasattr(task, 'due_date') or not task.due_date:
                    return False
                try:
                    due_date = datetime.datetime.strptime(task.due_date, "%Y-%m-%d").date()
                    return today <= due_date <= one_week_later
                except:
                    return False

            filtered_tasks = [t for t in filtered_tasks if is_due_soon(t)]

        # Apply search
        if search_text:
            filtered_tasks = [t for t in filtered_tasks if
                              search_text in t.description.lower() or
                              (hasattr(t, 'notes') and t.notes and search_text in t.notes.lower()) or
                              (hasattr(t, 'category') and t.category and search_text in t.category.lower()) or
                              (hasattr(t, 'tags') and any(search_text in tag.lower() for tag in t.tags))]

        # Update tree
        for task in filtered_tasks:
            # Prepare values
            task_id = task.id
            description = task.description
            priority = task.priority if hasattr(task, 'priority') else "Medium"
            due_date = task.due_date if hasattr(task, 'due_date') else ""
            category = task.category if hasattr(task, 'category') else ""
            tags = ", ".join(task.tags) if hasattr(task, 'tags') and task.tags else ""

            # Insert into tree
            item_id = self.task_tree.insert("", tk.END, values=(task_id, description, priority, due_date, category, tags))

            # Set tag based on completion status
            if task.completed:
                self.task_tree.item(item_id, tags=("completed",))
            elif hasattr(task, 'priority') and task.priority == "High":
                self.task_tree.item(item_id, tags=("high_priority",))

            # Set custom color if available
            if hasattr(task, 'color') and task.color:
                self.task_tree.tag_configure(f"color_{task_id}", background=task.color)
                self.task_tree.item(item_id, tags=(f"color_{task_id}",))

        # Configure tags
        self.task_tree.tag_configure("completed", foreground="green")
        self.task_tree.tag_configure("high_priority", foreground="red")

        # Update statistics
        self.update_stats()

    def add_task(self):
        dialog = EnhancedTaskDialog(self.root, "Add New Task")
        if dialog.result:
            task_id = 1 if not self.tasks else max(task.id for task in self.tasks) + 1

            # Create task with enhanced properties
            new_task = Task(
                task_id,
                dialog.result["description"],
                False
            )

            # Add extended attributes
            new_task.priority = dialog.result["priority"]
            new_task.due_date = dialog.result["due_date"]
            new_task.tags = dialog.result["tags"]
            new_task.notes = dialog.result["notes"]
            new_task.category = dialog.result["category"]
            new_task.color = dialog.result["color"]

            self.tasks.append(new_task)
            save_tasks(self.tasks)
            self.refresh_tasks()
            messagebox.showinfo("Success", f"Task '{dialog.result['description']}' added successfully")

    def edit_task(self):
        selected_items = self.task_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a task to edit")
            return

        item_id = selected_items[0]
        task_id = int(self.task_tree.item(item_id, "values")[0])

        task = next((t for t in self.tasks if t.id == task_id), None)
        if not task:
            return

        dialog = EnhancedTaskDialog(self.root, "Edit Task", task)
        if dialog.result:
            # Update task properties
            task.description = dialog.result["description"]
            task.priority = dialog.result["priority"]
            task.due_date = dialog.result["due_date"]
            task.tags = dialog.result["tags"]
            task.notes = dialog.result["notes"]
            task.category = dialog.result["category"]
            task.color = dialog.result["color"]

            save_tasks(self.tasks)
            self.refresh_tasks()
            messagebox.showinfo("Success", f"Task {task_id} updated successfully")

    def complete_task(self):
        selected_items = self.task_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a task to mark as complete")
            return

        item_id = selected_items[0]
        task_id = int(self.task_tree.item(item_id, "values")[0])

        task = next((t for t in self.tasks if t.id == task_id), None)
        if not task:
            return

        task.completed = True
        save_tasks(self.tasks)
        self.refresh_tasks()
        messagebox.showinfo("Success", f"Task {task_id} marked as complete")

    def delete_task(self):
        selected_items = self.task_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a task to delete")
            return

        item_id = selected_items[0]
        task_id = int(self.task_tree.item(item_id, "values")[0])

        task = next((t for t in self.tasks if t.id == task_id), None)
        if not task:
            return

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete task #{task_id}?"):
            self.tasks.remove(task)
            save_tasks(self.tasks)
            self.refresh_tasks()
            messagebox.showinfo("Success", f"Task {task_id} deleted successfully")

def launch_gui():
    root = tk.Tk()
    app = TaskManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    launch_gui()