"""
HomiCraft Editor Launch Script
Entry point for the HomiCraft visual software development engine.
Usage:
    python homi_editor.py [path_to_project]
    python homi_editor.py --run <path_to_project>
"""

import sys
import os
import traceback

# Ensure HomiCraft root is on python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from core.paths import resolve_resource_path
from editor.main_window import HomiCraftEditorWindow
from editor.project_manager import HomiCraftProjectManager


def handle_exception(exc_type, exc_value, exc_traceback):
    """Global crash handler that writes to log file and shows error message."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    err_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    crash_file = os.path.join(os.path.expanduser("~"), "HomiCraft_crash.log")
    try:
        with open(crash_file, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\nHomiCraft Crash Log\n{'='*60}\n{err_msg}\n")
    except Exception:
        pass

    try:
        if QApplication.instance():
            QMessageBox.critical(None, "HomiCraft Error", f"An unexpected error occurred:\n\n{err_msg}")
    except Exception:
        pass

    sys.__excepthook__(exc_type, exc_value, exc_traceback)


sys.excepthook = handle_exception


class HomiCraftAppController:
    """Coordinates lifecycle between Project Manager and Editor Window safely."""

    def __init__(self, initial_project: str | None = None):
        self.editor: HomiCraftEditorWindow | None = None
        self.pm: HomiCraftProjectManager | None = None

        if initial_project and os.path.isdir(initial_project):
            self.open_editor(initial_project)
        else:
            self.open_project_manager()

    def open_project_manager(self):
        old_editor = self.editor
        self.pm = HomiCraftProjectManager()
        self.pm.project_opened.connect(self.open_editor)
        self.pm.show()
        if old_editor:
            old_editor.hide()
            self.editor = None
            QTimer.singleShot(150, old_editor.deleteLater)

    def open_editor(self, project_path: str):
        old_pm = self.pm
        self.editor = HomiCraftEditorWindow(project_path)
        self.editor.project_manager_requested.connect(self.open_project_manager)
        self.editor.show()
        if old_pm:
            old_pm.hide()
            self.pm = None
            QTimer.singleShot(150, old_pm.deleteLater)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setQuitOnLastWindowClosed(True)

    # Set application icon
    icon_path = resolve_resource_path("icon.png")
    if not os.path.exists(icon_path):
        icon_path = resolve_resource_path("icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Support standalone runner mode: homi_editor.py --run <path>
    if len(sys.argv) > 1 and sys.argv[1] == "--run":
        if len(sys.argv) > 2 and os.path.isdir(sys.argv[2]):
            from core.runtime import HomiRuntimeWindow
            window = HomiRuntimeWindow(sys.argv[2])
            window.show()
            sys.exit(app.exec())
        else:
            print("Error: Missing valid project directory for --run")
            sys.exit(1)

    project_arg = sys.argv[1] if len(sys.argv) > 1 else None
    controller = HomiCraftAppController(project_arg)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
