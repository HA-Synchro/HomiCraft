"""
HomiCraft FileSystem Dock
Provides an interactive project directory browser where developers can create,
rename, delete, drag & drop, and organize Python scripts, UI scenes, and project assets.
"""

import os
import sys
import shutil
import subprocess
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QFileSystemModel,
    QMenu, QInputDialog, QMessageBox, QPushButton, QLabel, QHeaderView,
    QAbstractItemView
)
from PySide6.QtCore import Qt, Signal, QModelIndex, QDir
from PySide6.QtGui import QAction, QIcon, QKeySequence


class FileSystemDock(QWidget):
    open_file_requested = Signal(str)      # Emits absolute file path on double click
    script_created = Signal(str)           # Emits absolute file path of newly created script
    file_renamed = Signal(str, str)        # Emits (old_path, new_path)
    file_deleted = Signal(str)             # Emits deleted path

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_dir: Optional[str] = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Header with quick action buttons
        header_layout = QHBoxLayout()
        self.lbl_title = QLabel("📁 FileSystem (res://)")
        self.lbl_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #4ecdc4; padding: 2px;")
        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch()

        btn_new_script = QPushButton("🐍 + Script")
        btn_new_script.setToolTip("Create a new Python script")
        btn_new_script.setStyleSheet("padding: 3px 6px; background-color: #2e4a46; color: #4ecdc4; font-weight: bold; font-size: 11px;")
        btn_new_script.clicked.connect(self._create_new_script)
        header_layout.addWidget(btn_new_script)

        btn_new_folder = QPushButton("📁 + Folder")
        btn_new_folder.setToolTip("Create a new directory")
        btn_new_folder.setStyleSheet("padding: 3px 6px; font-size: 11px;")
        btn_new_folder.clicked.connect(self._create_new_folder)
        header_layout.addWidget(btn_new_folder)

        layout.addLayout(header_layout)

        # File System Model & Tree View
        self.model = QFileSystemModel(self)
        self.model.setReadOnly(False)
        self.model.setFilter(QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot)

        self.tree = QTreeView(self)
        self.tree.setModel(self.model)
        self.tree.setAnimated(True)
        self.tree.setSortingEnabled(True)
        self.tree.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._open_context_menu)
        self.tree.doubleClicked.connect(self._on_item_double_clicked)

        # ENABLE DRAGGING (drag .py files from FileSystem)
        self.tree.setDragEnabled(True)
        self.tree.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)

        # Hide extra columns for a clean view
        self.tree.setHeaderHidden(False)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in range(1, 4):
            self.tree.setColumnHidden(col, True)

        self.tree.setStyleSheet("""
            QTreeView {
                background-color: #1e1e24;
                color: #e0e0e0;
                border: 1px solid #333340;
                border-radius: 4px;
                font-family: 'Segoe UI', Consolas;
                font-size: 12px;
            }
            QTreeView::item:hover {
                background-color: #2a2a36;
            }
            QTreeView::item:selected {
                background-color: #2e4a46;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #262630;
                color: #b0bec5;
                padding: 4px;
                border: none;
                font-weight: bold;
            }
        """)

        layout.addWidget(self.tree)

    def set_project_dir(self, project_dir: str) -> None:
        self.project_dir = os.path.abspath(project_dir)
        self.lbl_title.setText("📁 FileSystem (res://)")
        self.model.setRootPath(self.project_dir)
        root_idx = self.model.index(self.project_dir)
        self.tree.setRootIndex(root_idx)

    def _get_selected_dir(self) -> str:
        indexes = self.tree.selectedIndexes()
        if indexes:
            path = self.model.filePath(indexes[0])
            if os.path.isdir(path):
                return path
            return os.path.dirname(path)
        return self.project_dir or ""

    def _get_selected_path(self) -> Optional[str]:
        indexes = self.tree.selectedIndexes()
        if indexes:
            return self.model.filePath(indexes[0])
        return None

    def _on_item_double_clicked(self, index: QModelIndex) -> None:
        file_path = self.model.filePath(index)
        if os.path.isfile(file_path):
            self.open_file_requested.emit(file_path)

    def _create_new_script(self) -> None:
        target_dir = self._get_selected_dir()
        if not target_dir:
            return

        name, ok = QInputDialog.getText(
            self, "New Python Script", "Enter script name (e.g. inventory.py):"
        )
        if not ok or not name.strip():
            return

        name = name.strip()
        if not name.endswith(".py"):
            name += ".py"

        file_path = os.path.join(target_dir, name)
        if os.path.exists(file_path):
            QMessageBox.warning(self, "File Exists", f"A file named '{name}' already exists.")
            return

        base_name = os.path.splitext(name)[0]
        template = f'"""\n{base_name}.py — HomiCraft Script\n"""\n\ndef _ready(app):\n    pass\n'

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(template)
            self.script_created.emit(file_path)
            self.open_file_requested.emit(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create script: {e}")

    def _create_new_folder(self) -> None:
        target_dir = self._get_selected_dir()
        if not target_dir:
            return

        name, ok = QInputDialog.getText(self, "New Folder", "Enter folder name:")
        if not ok or not name.strip():
            return

        folder_path = os.path.join(target_dir, name.strip())
        try:
            os.makedirs(folder_path, exist_ok=False)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create folder: {e}")

    def _create_new_file(self) -> None:
        target_dir = self._get_selected_dir()
        if not target_dir:
            return

        name, ok = QInputDialog.getText(self, "New File", "Enter file name (e.g. config.json):")
        if not ok or not name.strip():
            return

        file_path = os.path.join(target_dir, name.strip())
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                pass
            self.open_file_requested.emit(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create file: {e}")

    def _rename_selected(self) -> None:
        path = self._get_selected_path()
        if not path or path == self.project_dir:
            return

        old_name = os.path.basename(path)
        new_name, ok = QInputDialog.getText(self, "Rename", f"Rename '{old_name}' to:", text=old_name)
        if not ok or not new_name.strip() or new_name.strip() == old_name:
            return

        new_path = os.path.join(os.path.dirname(path), new_name.strip())
        try:
            os.rename(path, new_path)
            self.file_renamed.emit(path, new_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to rename: {e}")

    def _delete_selected(self) -> None:
        path = self._get_selected_path()
        if not path or path == self.project_dir:
            return

        fname = os.path.basename(path)
        reply = QMessageBox.question(
            self,
            "Delete Confirmation",
            f"Are you sure you want to permanently delete '{fname}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                self.file_deleted.emit(path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete: {e}")

    def _show_in_explorer(self) -> None:
        path = self._get_selected_path() or self.project_dir
        if not path:
            return
        if os.name == 'nt':
            if os.path.isfile(path):
                subprocess.Popen(f'explorer /select,"{os.path.abspath(path)}"')
            else:
                os.startfile(os.path.abspath(path))

    def _open_context_menu(self, pos) -> None:
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #202028;
                color: #e0e0e0;
                border: 1px solid #333340;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #2e4a46;
                color: #ffffff;
            }
        """)

        action_new_script = menu.addAction("🐍 New Python Script...")
        action_new_script.triggered.connect(self._create_new_script)

        action_new_folder = menu.addAction("📁 New Folder...")
        action_new_folder.triggered.connect(self._create_new_folder)

        action_new_file = menu.addAction("📄 New File...")
        action_new_file.triggered.connect(self._create_new_file)

        menu.addSeparator()

        selected_path = self._get_selected_path()
        if selected_path and selected_path != self.project_dir:
            action_rename = menu.addAction("✏️ Rename (F2)")
            action_rename.triggered.connect(self._rename_selected)

            action_delete = menu.addAction("🗑️ Delete")
            action_delete.triggered.connect(self._delete_selected)

            menu.addSeparator()

        action_explorer = menu.addAction("📂 Show in Explorer")
        action_explorer.triggered.connect(self._show_in_explorer)

        menu.exec(self.tree.viewport().mapToGlobal(pos))
