"""
Cross-platform notification system for Task Manager

This module provides a unified notification interface across different platforms:
- Windows: Uses win10toast, Windows API via PowerShell, or MessageBox fallback
- macOS: Uses pync (terminal-notifier) or AppleScript
- Linux: Uses D-Bus, notify-send, or zenity

The module also includes a background service to check for task reminders.
"""

import time
import threading
import platform
import subprocess
import logging
from functools import lru_cache
from task_manager.utils.storage import load_tasks, save_tasks
from task_manager.utils.settings import load_settings

# Configure logging
logger = logging.getLogger(__name__)

# Global settings for notifications
NOTIFICATION_SETTINGS = {
    'enabled': True,
    'sound': True,
    'console_fallback': True,
    'notify_completed': False
}

# Platform detection (only do this once)
@lru_cache(maxsize=1)
def get_platform():
    """Get the current platform"""
    return platform.system()

class NotificationManager:
    """Manages notifications across different platforms"""

    def __init__(self):
        self.platform = get_platform()
        self._notification_libs = {}

    def _import_platform_lib(self, lib_name):
        """Import a platform-specific notification library"""
        # Return cached library if we've already tried to import it
        if lib_name in self._notification_libs:
            return self._notification_libs[lib_name]

        # Don't try to import libraries for other platforms
        # Don't try to import libraries for other platforms
        if (lib_name == 'win10toast' and self.platform != "Windows") or \
           (lib_name == 'pync' and self.platform != "Darwin") or \
           (lib_name == 'dbus' and self.platform in ("Windows", "Darwin")):
            self._notification_libs[lib_name] = None
            return None

        # Try to import the library
        try:
            lib = __import__(lib_name)
            self._notification_libs[lib_name] = lib
            return lib
        except ImportError:
            self._notification_libs[lib_name] = None
            logger.debug(f"Notification library {lib_name} not available")
            return None
        except Exception as e:
            logger.error(f"Error importing {lib_name}: {e}")
            self._notification_libs[lib_name] = None
            return None
    def show_notification(self, title, message, timeout=5):
        """
        Show a notification using the best available method for the platform

        Args:
            title: Notification title
            message: Notification message
            timeout: Notification timeout in seconds

        Returns:
            bool: True if notification was shown, False otherwise
        """
        # Check if notifications are enabled
        settings = load_settings()
        if not settings.get('notifications', {}).get('enabled', True):
            logger.debug("Notifications are disabled in settings")
            return False

        # Make sound if enabled
        if settings.get('notifications', {}).get('sound', True):
            self._play_notification_sound()

        # Try platform-specific notifications
        try:
            if self.platform == "Windows":
                return self._show_windows_notification(title, message, timeout)
            elif self.platform == "Darwin":  # macOS
                return self._show_macos_notification(title, message)
            else:  # Linux and others
                return self._show_linux_notification(title, message, timeout)
        except Exception as e:
            logger.error(f"Error showing notification: {e}")

        # Fallback to console if enabled
        if settings.get('notifications', {}).get('console_fallback', True):
            self._show_console_notification(title, message)
            return True

        return False

    def _show_windows_notification(self, title, message, timeout=5):
        """Show notification on Windows"""
        # Try win10toast
        toaster = self._import_platform_lib('win10toast')
        if toaster:
            try:
                toaster.show_toast(title, message, duration=timeout, threaded=True)
                return True
            except Exception as e:
                logger.error(f"Error using win10toast: {e}")

        # Try Windows 10 PowerShell method
        try:
            # Escape quotes in title and message
            title = title.replace('"', '`"')
            message = message.replace('"', '`"')

            powershell_cmd = [
                'powershell',
                '-Command',
                f'''
                [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
                [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType=WindowsRuntime] | Out-Null
                $template = [Windows.UI.Notifications.ToastTemplateType]::ToastText02
                $xml = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent($template)
                $text = $xml.GetElementsByTagName('text')
                $text[0].AppendChild($xml.CreateTextNode('{title}'))
                $text[1].AppendChild($xml.CreateTextNode('{message}'))
                $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
                [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Task Manager').Show($toast)
                '''
            ]
            # Use CREATE_NO_WINDOW flag if on Windows to hide the PowerShell window
            kwargs = {'creationflags': subprocess.CREATE_NO_WINDOW} if self.platform == 'Windows' else {}
            subprocess.run(powershell_cmd, capture_output=True, **kwargs)
            return True
        except Exception as e:
            logger.error(f"Error using PowerShell notification: {e}")

        # Last resort - try Windows MessageBox via ctypes
        try:
            import ctypes
            MB_ICONINFORMATION = 0x00000040
            return ctypes.windll.user32.MessageBoxW(0, message, title, MB_ICONINFORMATION) != 0
        except Exception as e:
            logger.error(f"Error using MessageBox: {e}")

        return False

    def _show_macos_notification(self, title, message):
        """Show notification on macOS"""
        # Try pync
        pync_lib = self._import_platform_lib('pync')
        if pync_lib:
            try:
                pync_lib.notify(message, title=title, sound="default")
                return True
            except Exception as e:
                logger.error(f"Error using pync: {e}")

        # Fallback to AppleScript
        try:
            # Escape quotes in title and message
            title = title.replace('"', '\\"')
            message = message.replace('"', '\\"')

            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(['osascript', '-e', script], capture_output=True)
            return True
        except Exception as e:
            logger.error(f"Error using AppleScript: {e}")

        return False

    def _show_linux_notification(self, title, message, timeout=5):
        """Show notification on Linux"""
        # Try dbus
        dbus_lib = self._import_platform_lib('dbus')
        if dbus_lib:
            try:
                session_bus = dbus_lib.SessionBus()
                obj = session_bus.get_object(
                    'org.freedesktop.Notifications',
                    '/org/freedesktop/Notifications'
                )
                interface = dbus_lib.Interface(
                    obj,
                    'org.freedesktop.Notifications'
                )
                interface.Notify(
                    "Task Manager",     # app_name
                    0,                  # replaces_id
                    "",                 # app_icon
                    title,              # summary
                    message,            # body
                    [],                 # actions
                    {},                 # hints
                    timeout * 1000      # timeout in ms
                )
                return True
            except Exception as e:
                logger.error(f"Error using D-Bus notification: {e}")

        # Try notify-send
        try:
            subprocess.run(['notify-send', title, message], check=True, capture_output=True)
            return True
        except Exception:
            pass

        # Try zenity
        try:
            subprocess.run(
                ['zenity', '--notification', '--text', f"{title}: {message}"],
                check=True, capture_output=True
            )
            return True
        except Exception:
            pass

        return False

    def _show_console_notification(self, title, message):
        """Show a notification in the console as a fallback"""
        print(f"\n[NOTIFICATION] {title}: {message}")

    def _play_notification_sound(self):
        """Play a notification sound if available on the platform"""
        try:
            if self.platform == "Windows":
                import winsound
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            elif self.platform == "Darwin":  # macOS
                subprocess.run(['afplay', '/System/Library/Sounds/Ping.aiff'],
                              capture_output=True, timeout=1)
            else:  # Linux
                subprocess.run(['paplay', '/usr/share/sounds/freedesktop/stereo/message.oga'],
                              capture_output=True, timeout=1)
        except Exception:
            # Silently fail if we can't play a sound
            pass

# Global notification manager instance
notification_manager = NotificationManager()

def show_notification(title, message, timeout=5):
    """Show a notification using the appropriate method for the platform"""
    return notification_manager.show_notification(title, message, timeout)

def test_notification():
    """Test the notification system"""
    return show_notification(
        "Task Manager Test",
        "If you can see this notification, the system is working correctly!",
        timeout=5
    )

# Add this function to fix the reminder handling
def set_task_reminder(task, reminder_datetime):
    """Set a reminder for a task and save the task list

    Args:
        task: The task object to set a reminder for
        reminder_datetime: A datetime object specifying when to send the reminder

    Returns:
        bool: True if the reminder was set successfully
    """
    try:
        if not hasattr(task, 'set_reminder'):
            logger.error(f"Task {task.id} doesn't have set_reminder method")
            return False

        # Set the reminder
        task.set_reminder(reminder_datetime)

        # Save the updated task list
        tasks = load_tasks()
        for i, t in enumerate(tasks):
            if t.id == task.id:
                tasks[i] = task
                break

        save_tasks(tasks)

        logger.info(f"Reminder set for task {task.id} at {reminder_datetime.strftime('%Y-%m-%d %H:%M')}")
        return True

    except Exception as e:
        logger.error(f"Error setting reminder: {e}")
        return False

class ReminderService:
    """Background service to check for task reminders"""

    def __init__(self):
        self.running = False
        self.thread = None

    def start(self):
        """Start the reminder service in a background thread"""
        if self.running:
            logger.warning("Reminder service already running")
            return self.thread

        self.running = True
        self.thread = threading.Thread(target=self._service_loop, daemon=True)
        self.thread.start()
        logger.info("Reminder service started")
        return self.thread

    def stop(self):
        """Stop the reminder service"""
        self.running = False
        logger.info("Reminder service stopped")

    def _service_loop(self):
        """Main service loop that checks for reminders"""
        while self.running:
            try:
                self.check_reminders()
            except Exception as e:
                logger.error(f"Error in reminder service: {e}")

            # Sleep for a minute before checking again
            time.sleep(60)

    # Fix this method to handle task objects correctly
    def check_reminders(self):
        """Check tasks for due reminders"""
        try:
            tasks = load_tasks()
            current_time = time.time()
            updated = False

            for task in tasks:
                # Skip tasks that don't need reminders or aren't properly configured
                if not hasattr(task, 'reminder_time') or task.reminder_time is None:
                    continue

                # Skip completed tasks (unless notifications for completed tasks are enabled)
                if task.completed and not NOTIFICATION_SETTINGS.get('notify_completed', False):
                    continue

                # Skip already notified reminders
                if hasattr(task, 'reminder_notified') and task.reminder_notified:
                    continue

                # Convert reminder_time to float if it's a string or handle invalid types
                try:
                    reminder_time = float(task.reminder_time)
                except (ValueError, TypeError):
                    logger.warning(f"Invalid reminder_time for task {task.id}")
                    continue

                # If reminder time has passed
                if current_time >= reminder_time:
                    # Format due date info if available
                    due_info = ""
                    if hasattr(task, 'due_date') and task.due_date:
                        due_info = f" (Due: {task.due_date})"

                    # Format priority if available and not Medium
                    priority_str = ""
                    if hasattr(task, 'priority') and task.priority != "Medium":
                        priority_str = f"[{task.priority}] "

                    notification_title = f"Task Reminder {priority_str}"
                    notification_message = f"Task #{task.id}: {task.description}{due_info}"

                    # Show the notification
                    notification_success = show_notification(notification_title, notification_message)

                    # Mark as notified if notification was shown or if we can't show notifications
                    # (to avoid repeated failed attempts)
                    task.reminder_notified = True
                    updated = True

                    if notification_success:
                        logger.info(f"Reminder notification sent for task #{task.id}")
                    else:
                        logger.warning(f"Failed to send notification for task #{task.id}")

            # Save tasks if any were updated
            if updated:
                save_tasks(tasks)
                return True

        except Exception as e:
            logger.error(f"Error checking reminders: {e}")

        return False

# Global reminder service instance
reminder_service = ReminderService()

def start_reminder_service():
    """Start the reminder service"""
    return reminder_service.start()

def stop_reminder_service():
    """Stop the reminder service"""
    reminder_service.stop()

def check_reminders():
    """Manually check for due reminders"""
    return reminder_service.check_reminders()

def reset_notifications():
    """Reset notification flags for all tasks (for debugging)"""
    tasks = load_tasks()
    updated = False

    for task in tasks:
        if hasattr(task, 'reminder_notified') and task.reminder_notified:
            task.reminder_notified = False
            updated = True

    if updated:
        save_tasks(tasks)
        logger.info("All notification flags have been reset")
        return True
    else:
        logger.info("No notification flags needed to be reset")
        return False