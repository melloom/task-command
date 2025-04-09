from setuptools import setup, find_packages

setup(
    name="task-manager",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "Pillow",  # Optional for advanced GUI
        "ttkthemes",  # Optional for advanced GUI themes
    ],
    entry_points={
        "console_scripts": [
            "task-cli=task_manager.main:main",
            "task=task_manager.main:main",  # Shorter alias
            "task-gui=main:main",
            "taskmanager=main:main",  # Alternative name
            "task-shell=task_manager.task_shell:main",  # New interactive shell
        ],
    },
    author="Task Manager Team",
    author_email="example@example.com",
    description="A versatile task management application with GUI and CLI interfaces",
    keywords="task, todo, productivity, gui, cli",
    python_requires=">=3.6",
)