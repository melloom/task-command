import sys
import logging
import atexit

def main():
    """Main entry point for the task shell."""
    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("Welcome to the Task Shell!")

    # Start notification service
    from task_manager.utils.notifications import start_reminder_service, stop_reminder_service
    reminder_thread = start_reminder_service()

    # Register a function to stop the reminder service when the application exits
    atexit.register(stop_reminder_service)

    # Check if GUI mode is requested
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        try:
            from task_manager.gui import launch_simple_gui
            print("Starting GUI...")
            launch_simple_gui()
            return
        except ImportError as e:
            print(f"Error launching GUI: {e}")
            print("Falling back to command-line mode.")

    # Continue with command-line interface
    # ...existing code...

