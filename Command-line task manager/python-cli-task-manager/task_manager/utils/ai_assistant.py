"""
AI Assistant module for Task Manager
Provides intelligent task analysis, suggestions, and automation using DeepSeek AI.
This module is currently disabled but maintained for future activation.
"""

import re
import datetime
from typing import List, Dict, Any, Optional, Tuple

from task_manager.models.task import Task
from task_manager.utils.storage import load_tasks, save_tasks

# Flag to easily enable/disable AI functionality
AI_ENABLED = False

def is_available() -> bool:
    """Check if AI assistant functionality is available."""
    return AI_ENABLED

# Create a global instance that other modules can import
assistant = None

class AIAssistant:
    def __init__(self):
        self.tasks = []
        self.available = AI_ENABLED

    def analyze_tasks(self) -> List[Dict[str, Any]]:
        """Analyze tasks and provide insights."""
        if not AI_ENABLED:
            return [{"status": "AI assistant is currently disabled"}]

        # Original implementation preserved for future use
        self.tasks = load_tasks()
        analysis = []

        for task in self.tasks:
            if isinstance(task, Task):
                # Use regex to extract important keywords
                keywords = re.findall(r'\b\w+\b', task.description)

                # Check due dates
                due_date = task.due_date
                now = datetime.datetime.now()
                days_left: Optional[int] = None

                if due_date:
                    days_left = (due_date - now).days

                analysis.append({
                    'id': task.id,
                    'urgency': 'high' if days_left and days_left < 2 else 'normal',
                    'keywords': keywords
                })

        return analysis

    def save_analysis_results(self, results: List[Tuple[int, str]]) -> bool:
        """Save analysis results."""
        if not AI_ENABLED:
            return False

        # Example of using save_tasks
        return save_tasks(self.tasks)

    def generate_response(self, user_input, tasks=None) -> str:
        """Generate a response to user input."""
        if not AI_ENABLED:
            return "AI Assistant is currently disabled. You can enable it in the future by setting AI_ENABLED to True in the ai_assistant.py file."

        # Placeholder for future AI response generation
        return "This is a placeholder response. Real AI functionality will be implemented in the future."

# Initialize the global assistant instance
assistant = AIAssistant()
