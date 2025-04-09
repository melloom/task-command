"""
AI Assistant Interface for Task Manager
Provides the GUI interface for interacting with the AI assistant
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import time
from typing import List, Dict, Any, Optional

# Import the AI assistant - now with explicit handling for disabled state
from task_manager.utils.ai_assistant import assistant, is_available

from task_manager.utils.storage import load_tasks, save_tasks
from task_manager.models.task import Task

def show_ai_assistant(parent=None):
    """Show the AI assistant dialog with disabled state message"""
    dialog = AIAssistantDialog(parent)
    return dialog

class AIAssistantDialog(tk.Toplevel):
    """Dialog for AI Assistant interface"""

    def __init__(self, parent, task_manager=None):
        super().__init__(parent)
        self.title("AI Assistant")
        self.geometry("700x500")
        self.minsize(500, 400)
        self.transient(parent)
        self.grab_set()

        self.task_manager = task_manager
        self.tasks = load_tasks()

        # Configure the dialog
        self.create_widgets()

        # Center on parent
        self.geometry(f"+{parent.winfo_rootx() + 50}+{parent.winfo_rooty() + 50}")

        # Set up message queue for thread safety
        self.message_queue = queue.Queue()
        self.after(100, self.check_queue)

        # Welcome message
        if is_available():
            self.add_assistant_message("Hello! I'm your AI assistant. How can I help you manage your tasks today?")
        else:
            self.add_assistant_message("AI Assistant is currently disabled. This feature will be available in a future update.")
            self.add_assistant_message("You can still use this interface to view how the AI assistant will work.")
            self.input_entry.config(state=tk.DISABLED)  # Disable input when AI is disabled

    def create_widgets(self):
        """Create the dialog widgets"""
        # Main container with padding
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(
            main_frame,
            width=80,
            height=20,
            wrap=tk.WORD,
            font=("Helvetica", 10),
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Input area
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        self.input_entry = ttk.Entry(input_frame, font=("Helvetica", 10))
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.input_entry.bind("<Return>", self.send_message)

        send_button = ttk.Button(input_frame, text="Send", command=self.send_message)
        send_button.pack(side=tk.RIGHT)

        # Bottom button area
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(
            button_frame,
            text="Close",
            command=self.destroy
        ).pack(side=tk.RIGHT)

    def add_user_message(self, message):
        """Add a user message to the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "You: ", "user_tag")
        self.chat_display.insert(tk.END, message + "\n\n", "user_message")
        self.chat_display.tag_configure("user_tag", foreground="blue", font=("Helvetica", 10, "bold"))
        self.chat_display.tag_configure("user_message", font=("Helvetica", 10))
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def add_assistant_message(self, message):
        """Add an assistant message to the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "Assistant: ", "assistant_tag")
        self.chat_display.insert(tk.END, message + "\n\n", "assistant_message")
        self.chat_display.tag_configure("assistant_tag", foreground="green", font=("Helvetica", 10, "bold"))
        self.chat_display.tag_configure("assistant_message", font=("Helvetica", 10))
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def send_message(self, event=None):
        """Send a message to the AI assistant"""
        # If AI is disabled, don't process messages
        if not is_available():
            self.add_assistant_message("Sorry, the AI assistant is currently disabled.")
            return

        message = self.input_entry.get().strip()
        if not message:
            return

        # Clear input
        self.input_entry.delete(0, tk.END)

        # Add user message to chat
        self.add_user_message(message)

        # Get response from assistant
        response = assistant.generate_response(message, self.tasks)
        self.add_assistant_message(response)

    def check_queue(self):
        """Check for messages in the queue and process them"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                self.add_assistant_message(message)
                self.message_queue.task_done()
        except queue.Empty:
            pass

        # Schedule the next check
        self.after(100, self.check_queue)
