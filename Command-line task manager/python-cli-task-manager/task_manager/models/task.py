import datetime
import time

class Task:
    def __init__(self, task_id: int, description: str, completed: bool = False, created_at=None):
        self.id = task_id
        self.description = description
        self.completed = completed
        self.created_at = created_at or datetime.datetime.now().strftime("%Y-%m-%d")

        # Additional properties used by the GUI
        self.priority = "Medium"
        self.due_date = None
        self.category = None
        self.progress = 0
        self.notes = ""
        self.reminder_time = None

    def mark_complete(self):
        self.completed = True
        self.progress = 100

    def set_reminder(self, reminder_datetime):
        """Set a reminder time for this task"""
        if isinstance(reminder_datetime, datetime.datetime):
            self.reminder_time = reminder_datetime.timestamp()
        else:
            self.reminder_time = float(reminder_datetime)

    def __repr__(self):
        return f"Task(id={self.id}, description='{self.description}', completed={self.completed})"