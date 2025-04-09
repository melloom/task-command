#!/usr/bin/env python
"""
Task Manager Command Shell
Provides a persistent command-line interface for Task Manager
"""

import os
import sys
import shlex
import subprocess

def show_prompt():
    """Show a colorful command prompt"""
    return "\033[1;36mtask> \033[0m"

def process_command(command):
    """Process a single command by forwarding to task-cli"""
    if not command.strip():
        return True

    # Handle built-in commands
    if command.strip() == "exit" or command.strip() == "quit":
        print("Exiting Task Manager.")
        return False
    elif command.strip() == "help":
        print("\nTask Manager Commands:")
        print("  add \"Task description\" [--priority=High|Medium|Low] [--due=YYYY-MM-DD]")
        print("  list [--status=all|active|completed] [--priority=all|High|Medium|Low]")
        print("  complete <task_id>    - Mark a task as complete")
        print("  delete <task_id>      - Delete a task")
        print("  interactive           - Enter interactive mode")
        print("  toggle-interactive    - Toggle interactive mode setting")
        print("  exit, quit            - Exit the shell")
        print("  help                  - Show this help")
        return True
    elif command.strip() == "clear" or command.strip() == "cls":
        os.system('cls' if os.name == 'nt' else 'clear')
        return True

    # Forward to task-cli
    try:
        args = shlex.split(command)
        subprocess.run([sys.executable, "-m", "task_manager.main"] + args)
    except Exception as e:
        print(f"Error: {e}")

    return True

def main():
    """Run the command shell"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\033[1;36m")
    print("=======================================")
    print("   Task Manager Command Shell v1.0.0   ")
    print("=======================================")
    print("\033[0m")
    print("Type 'help' for available commands or 'exit' to quit.")

    running = True
    while running:
        try:
            command = input(show_prompt())
            running = process_command(command)
        except KeyboardInterrupt:
            print("\nUse 'exit' or 'quit' to exit.")
        except EOFError:
            print("\nExiting Task Manager.")
            running = False

if __name__ == "__main__":
    main()
