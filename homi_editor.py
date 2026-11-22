"""
HomiCraft Editor Launch Script
Entry point for the HomiCraft visual software development engine.
Usage:
    python homi_editor.py [path_to_project]
"""

import sys
import os

# Ensure HomiCraft root is on python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from editor.main_window import HomiCraftEditorWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    project_arg = sys.argv[1] if len(sys.argv) > 1 else None
    window = HomiCraftEditorWindow(project_arg)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
