"""
HomiCraft App Runner
Entry-point CLI to launch any HomiCraft project.
Usage:
    python runner.py <path_to_project_folder>
"""

import sys
import os

# Add HomiCraft root directory to python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from core.runtime import HomiRuntimeWindow


def main():
    if len(sys.argv) < 2:
        print("Usage: python runner.py <path_to_project_folder>")
        print("Example: python runner.py examples/counter_app")
        sys.exit(1)

    project_dir = sys.argv[1]
    if not os.path.isdir(project_dir):
        print(f"Error: Directory '{project_dir}' not found.")
        sys.exit(1)

    app = QApplication(sys.argv)
    
    # Modern dark theme for runtime
    app.setStyle("Fusion")

    window = HomiRuntimeWindow(project_dir)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
