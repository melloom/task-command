import datetime

class Task:
    def __init__(self, task_id: int, description: str, completed: bool = False, created_at=None):
        self.id = task_id
        self.description = description
        self.completed = completed
        self.created_at = created_at or datetime.datetime.now().strftime("%Y-%m-%d")
        self.reminder_time = None
        self.reminder_notified = False

    def mark_complete(self):
        self.completed = True

    def set_reminder(self, reminder_datetime):
        """Set a reminder time for this task.

        Args:
            reminder_datetime: A datetime object for when to send the reminder
        """
        if isinstance(reminder_datetime, datetime.datetime):
            # Convert to unix timestamp for storage
            self.reminder_time = reminder_datetime.timestamp()
            self.reminder_notified = False
            return True
        else:
            raise TypeError("reminder_datetime must be a datetime object")

    def clear_reminder(self):
        """Clear the reminder for this task"""
        self.reminder_time = None
        self.reminder_notified = False

    def get_reminder_datetime(self):
        """Get the reminder time as a datetime object, or None if not set"""
        if self.reminder_time is None:
            return None

        try:
            return datetime.datetime.fromtimestamp(float(self.reminder_time))
        except (ValueError, TypeError):
            return None

    def __repr__(self):
        return f"Task(id={self.id}, description='{self.description}', completed={self.completed}, created_at='{self.created_at}')"