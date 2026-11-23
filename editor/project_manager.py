"""
HomiCraft Project Manager
Godot-style Project Hub to create, browse, import, edit, run, and manage HomiCraft projects.
Styled with official Catppuccin palettes and rounded-corner UI components.
"""

import os
import sys
import json
import shutil
from typing import List, Dict, Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QListWidget, QListWidgetItem, QFileDialog, QMessageBox,
    QDialog, QFormLayout, QComboBox, QFrame, QAbstractItemView, QApplication,
    QInputDialog
)
from PySide6.QtCore import Qt, Signal, QSettings, QSize
from PySide6.QtGui import QIcon, QFont, QKeySequence

from core.schema import (
    ProjectConfig, WidgetNode, save_project_config, load_project_config,
    save_scene
)
from core.paths import resolve_resource_path
from editor.theme import build_catppuccin_stylesheet, CATPPUCCIN_PALETTES


class ProjectCardWidget(QWidget):
    """Visual card for each project in the list (Godot style)."""

    def __init__(self, name: str, path: str, version: str = "1.0.0", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        # Top line: Project title and version
        top_row = QHBoxLayout()
        self.lbl_title = QLabel(f"⚡ {name}")
        self.lbl_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #cba6f7;")
        top_row.addWidget(self.lbl_title)

        lbl_version = QLabel(f"v{version}")
        lbl_version.setStyleSheet("font-size: 11px; color: #a6adc8; background: #313244; padding: 2px 6px; border-radius: 4px;")
        top_row.addWidget(lbl_version)
        top_row.addStretch()

        if not os.path.exists(path):
            lbl_missing = QLabel("⚠️ Folder Missing")
            lbl_missing.setStyleSheet("font-size: 11px; color: #f38ba8; font-weight: bold; background: rgba(243, 139, 168, 0.15); padding: 2px 6px; border-radius: 4px;")
            top_row.addWidget(lbl_missing)

        layout.addLayout(top_row)

        # Bottom line: Directory path
        self.lbl_path = QLabel(path)
        self.lbl_path.setStyleSheet("font-size: 11px; color: #9399b2; font-family: Consolas;")
        layout.addWidget(self.lbl_path)


class NewProjectDialog(QDialog):
    """Dialog to create a new HomiCraft project with templates."""

    def __init__(self, default_parent_dir: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New HomiCraft Project")
        self.resize(560, 340)
        self.created_project_path: Optional[str] = None

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 18, 20, 18)

        header = QLabel("✨ Create New Project")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #cba6f7; padding-bottom: 2px;")
        layout.addWidget(header)

        form = QFormLayout()
        form.setSpacing(10)

        # Project Name
        self.inp_name = QLineEdit("My New App")
        self.inp_name.textChanged.connect(self._update_full_path)
        form.addRow("Project Name:", self.inp_name)

        # Project Location
        path_row = QHBoxLayout()
        self.default_parent = default_parent_dir
        self.inp_parent_dir = QLineEdit(default_parent_dir)
        self.inp_parent_dir.textChanged.connect(self._update_full_path)
        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self._browse_dir)
        path_row.addWidget(self.inp_parent_dir)
        path_row.addWidget(btn_browse)
        form.addRow("Location:", path_row)

        # Target Full Path Display
        self.lbl_full_path = QLabel("")
        self.lbl_full_path.setStyleSheet("font-size: 11px; color: #a6e3a1; font-family: Consolas;")
        form.addRow("Target Folder:", self.lbl_full_path)

        # Starter Template
        self.combo_template = QComboBox()
        self.combo_template.addItems([
            "Empty Project (Clean Slate)",
            "Counter & Controls Demo (Sample Widgets & Scripts)"
        ])
        form.addRow("Starter Template:", self.combo_template)

        layout.addLayout(form)
        self._update_full_path()

        layout.addStretch()

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)

        self.btn_create = QPushButton("🚀 Create & Edit")
        self.btn_create.setObjectName("btn_run")
        self.btn_create.setStyleSheet("padding: 8px 18px; font-weight: bold; border-radius: 8px;")
        self.btn_create.clicked.connect(self._create_project)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(self.btn_create)
        layout.addLayout(btn_layout)

    def _browse_dir(self):
        chosen = QFileDialog.getExistingDirectory(self, "Select Projects Parent Directory", self.inp_parent_dir.text())
        if chosen:
            self.inp_parent_dir.setText(chosen)

    def _update_full_path(self):
        name_clean = self.inp_name.text().strip().replace(" ", "_").lower() or "my_app"
        parent = self.inp_parent_dir.text().strip()
        full = os.path.join(parent, name_clean)
        self.lbl_full_path.setText(full)

    def _create_project(self):
        name = self.inp_name.text().strip() or "Untitled Project"
        target_dir = self.lbl_full_path.text().strip()

        if not target_dir:
            QMessageBox.warning(self, "Invalid Path", "Please specify a valid destination folder.")
            return

        if os.path.exists(target_dir) and os.listdir(target_dir):
            reply = QMessageBox.question(
                self,
                "Folder Not Empty",
                f"The directory '{target_dir}' already exists and contains files.\nDo you still want to create the project here?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        os.makedirs(target_dir, exist_ok=True)
        is_demo = (self.combo_template.currentIndex() == 1)

        if is_demo:
            # Copy sample files from counter_app
            sample_dir = resolve_resource_path("examples", "counter_app")
            if os.path.exists(sample_dir):
                for item in os.listdir(sample_dir):
                    if item in ("dist", "__pycache__"):
                        continue
                    src_file = os.path.join(sample_dir, item)
                    dst_file = os.path.join(target_dir, item)
                    if os.path.isfile(src_file):
                        shutil.copy2(src_file, dst_file)
                # Overwrite project.json with the user's project name
                config_path = os.path.join(target_dir, "project.json")
                if os.path.exists(config_path):
                    try:
                        cfg = load_project_config(config_path)
                        cfg.name = name
                        cfg.window_title = name
                        save_project_config(config_path, cfg)
                    except Exception:
                        pass
            else:
                self._create_empty_project(target_dir, name)
        else:
            self._create_empty_project(target_dir, name)

        self.created_project_path = target_dir
        self.accept()

    def _create_empty_project(self, target_dir: str, name: str):
        # 1. project.json
        config = ProjectConfig(
            name=name,
            version="1.0.0",
            entry_scene="main.ui.json",
            window_title=name,
            window_width=800,
            window_height=600,
            window_resizable=True
        )
        save_project_config(os.path.join(target_dir, "project.json"), config)

        # 2. main.ui.json
        root = WidgetNode(
            id="root_window",
            type="Window",
            x=0,
            y=0,
            width=800,
            height=600,
            properties={"title": name, "bg_color": "#1e1e2e"},
            signals={},
            children=[]
        )
        save_scene(os.path.join(target_dir, "main.ui.json"), root)

        # 3. main.py
        py_content = (
            f'"""\n'
            f'{name} — Main Controller Script\n'
            f'Generated by HomiCraft Engine\n'
            f'"""\n\n'
            f'def _ready(app):\n'
            f'    """Called when the scene tree has loaded and is ready."""\n'
            f'    print("{name} loaded successfully!")\n'
        )
        with open(os.path.join(target_dir, "main.py"), "w", encoding="utf-8") as f:
            f.write(py_content)


class HomiCraftProjectManager(QMainWindow):
    project_opened = Signal(str)  # Emits project_dir when user clicks Edit/Open

    def __init__(self):
        super().__init__()
        self.setWindowTitle("HomiCraft — Project Manager")
        self.resize(1020, 640)

        # Theme setting
        settings = QSettings("HomiCraft", "Theme")
        self.current_flavor = settings.value("flavor", "Mocha")

        self.projects: List[Dict[str, str]] = []
        self._load_projects_list()

        self._init_ui()
        self.apply_theme(self.current_flavor)

    def _init_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 18, 20, 18)
        main_layout.setSpacing(14)

        # Header bar
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        lbl_app = QLabel("⚡ HomiCraft Engine")
        lbl_app.setStyleSheet("font-size: 22px; font-weight: 800; color: #cba6f7;")
        title_box.addWidget(lbl_app)

        lbl_sub = QLabel("Select a project to edit, run, or create a new one.")
        lbl_sub.setStyleSheet("font-size: 12px; color: #a6adc8;")
        title_box.addWidget(lbl_sub)
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        # Theme Selector in Project Manager header
        lbl_theme = QLabel("🎨 Theme:")
        lbl_theme.setStyleSheet("font-weight: bold; margin-right: 4px;")
        header_layout.addWidget(lbl_theme)

        self.combo_theme = QComboBox(self)
        self.combo_theme.addItems([
            "🌿 Mocha (Dark)",
            "☕ Macchiato (Medium)",
            "🍨 Frappé (Soft)",
            "🥛 Latte (Light)"
        ])
        flavor_to_idx = {"Mocha": 0, "Macchiato": 1, "Frappé": 2, "Latte": 3}
        self.combo_theme.setCurrentIndex(flavor_to_idx.get(self.current_flavor, 0))
        self.combo_theme.currentIndexChanged.connect(self._on_theme_changed)
        header_layout.addWidget(self.combo_theme)

        main_layout.addLayout(header_layout)

        # Search bar
        search_layout = QHBoxLayout()
        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("🔍 Filter Projects...")
        self.inp_search.textChanged.connect(self._filter_projects)
        search_layout.addWidget(self.inp_search)
        main_layout.addLayout(search_layout)

        # Body: Left = Projects List, Right = Action Buttons (Godot style)
        body_layout = QHBoxLayout()
        body_layout.setSpacing(16)

        # Project List View
        self.project_list = QListWidget(self)
        self.project_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.project_list.setStyleSheet("""
            QListWidget {
                border-radius: 10px;
                padding: 6px;
            }
            QListWidget::item {
                border-radius: 8px;
                margin-bottom: 4px;
            }
        """)
        self.project_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.project_list.itemSelectionChanged.connect(self._on_selection_changed)
        body_layout.addWidget(self.project_list, stretch=1)

        # Right Action Column
        actions_box = QVBoxLayout()
        actions_box.setSpacing(8)

        self.btn_edit = QPushButton("✏️ Edit Project")
        self.btn_edit.setObjectName("btn_run")
        self.btn_edit.setStyleSheet("padding: 10px 20px; font-size: 13px; font-weight: bold; border-radius: 8px;")
        self.btn_edit.clicked.connect(self._open_selected_project)
        actions_box.addWidget(self.btn_edit)

        self.btn_run = QPushButton("▶ Run Standalone")
        self.btn_run.setStyleSheet("padding: 8px 18px; font-size: 12px; border-radius: 8px;")
        self.btn_run.clicked.connect(self._run_selected_project)
        actions_box.addWidget(self.btn_run)

        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        actions_box.addWidget(line1)

        btn_new = QPushButton("➕ New Project...")
        btn_new.setStyleSheet("padding: 8px 18px; font-size: 12px; border-radius: 8px;")
        btn_new.clicked.connect(self._open_new_project_dialog)
        actions_box.addWidget(btn_new)

        btn_import = QPushButton("📂 Import / Scan...")
        btn_import.setStyleSheet("padding: 8px 18px; font-size: 12px; border-radius: 8px;")
        btn_import.clicked.connect(self._import_project)
        actions_box.addWidget(btn_import)

        self.btn_rename = QPushButton("📝 Rename Project...")
        self.btn_rename.setStyleSheet("padding: 8px 18px; font-size: 12px; border-radius: 8px;")
        self.btn_rename.clicked.connect(self._rename_selected_project)
        actions_box.addWidget(self.btn_rename)

        self.btn_reveal = QPushButton("🔍 Show in Explorer")
        self.btn_reveal.setStyleSheet("padding: 8px 18px; font-size: 12px; border-radius: 8px;")
        self.btn_reveal.clicked.connect(self._reveal_in_explorer)
        actions_box.addWidget(self.btn_reveal)

        actions_box.addStretch()

        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        actions_box.addWidget(line2)

        self.btn_remove = QPushButton("🗑️ Remove from List")
        self.btn_remove.setStyleSheet("padding: 8px 18px; font-size: 12px; border-radius: 8px; background-color: #45475a; color: #cdd6f4;")
        self.btn_remove.clicked.connect(self._remove_selected_project)
        actions_box.addWidget(self.btn_remove)

        self.btn_delete = QPushButton("💥 Delete Project Files...")
        self.btn_delete.setStyleSheet("padding: 8px 18px; font-size: 12px; border-radius: 8px; background-color: #ba2d42; color: #ffffff; font-weight: bold;")
        self.btn_delete.clicked.connect(self._delete_project_files)
        actions_box.addWidget(self.btn_delete)

        body_layout.addLayout(actions_box)
        main_layout.addLayout(body_layout)

        self._populate_list()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._open_selected_project()
        else:
            super().keyPressEvent(event)

    def _on_theme_changed(self, index: int):
        flavors = ["Mocha", "Macchiato", "Frappé", "Latte"]
        if 0 <= index < len(flavors):
            self.apply_theme(flavors[index])

    def apply_theme(self, flavor: str):
        self.current_flavor = flavor
        qss = build_catppuccin_stylesheet(flavor)
        self.setStyleSheet(qss)
        settings = QSettings("HomiCraft", "Theme")
        settings.setValue("flavor", flavor)

    def _load_projects_list(self):
        settings = QSettings("HomiCraft", "ProjectManager")
        raw = settings.value("recent_projects", "[]")
        try:
            loaded = json.loads(raw)
        except Exception:
            loaded = []

        # Filter out stale temp paths (e.g., from PyInstaller _MEI extraction folders)
        self.projects = []
        for p in loaded:
            pth = p.get("path", "")
            if pth and "_MEI" not in pth and os.path.exists(pth):
                self.projects.append(p)

        # Ensure a permanent demo project exists in user Documents/HomiCraftProjects
        user_projects_dir = os.path.join(os.path.expanduser("~/Documents"), "HomiCraftProjects")
        permanent_demo = os.path.join(user_projects_dir, "CounterDemo")

        # If running from source, use the source repo's examples/counter_app directly
        source_demo = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "examples", "counter_app"))
        if os.path.exists(source_demo) and not getattr(sys, "frozen", False):
            target_demo = source_demo
        else:
            if not os.path.exists(permanent_demo):
                bundled_demo = resolve_resource_path("examples", "counter_app")
                if os.path.exists(bundled_demo):
                    os.makedirs(user_projects_dir, exist_ok=True)
                    shutil.copytree(bundled_demo, permanent_demo, dirs_exist_ok=True)
            target_demo = permanent_demo if os.path.exists(permanent_demo) else resolve_resource_path("examples", "counter_app")

        if os.path.exists(target_demo):
            if not any(p.get("path") == target_demo for p in self.projects):
                self.projects.insert(0, {
                    "name": "Counter & Controls Demo",
                    "path": target_demo,
                    "version": "1.0.0"
                })

    def _save_projects_list(self):
        settings = QSettings("HomiCraft", "ProjectManager")
        settings.setValue("recent_projects", json.dumps(self.projects))

    def _populate_list(self, filter_text: str = ""):
        self.project_list.clear()
        filter_lower = filter_text.strip().lower()

        for p in self.projects:
            name = p.get("name", "Untitled")
            path = p.get("path", "")
            version = p.get("version", "1.0.0")

            if filter_lower and filter_lower not in name.lower() and filter_lower not in path.lower():
                continue

            item = QListWidgetItem(self.project_list)
            item.setSizeHint(QSize(0, 68))
            card = ProjectCardWidget(name, path, version)
            self.project_list.addItem(item)
            self.project_list.setItemWidget(item, card)
            item.setData(Qt.ItemDataRole.UserRole, p)

        if self.project_list.count() > 0:
            self.project_list.setCurrentRow(0)
            self._update_buttons(True)
        else:
            self._update_buttons(False)

    def _filter_projects(self, text: str):
        self._populate_list(text)

    def _on_selection_changed(self):
        has_sel = len(self.project_list.selectedItems()) > 0
        self._update_buttons(has_sel)

    def _update_buttons(self, enabled: bool):
        self.btn_edit.setEnabled(enabled)
        self.btn_run.setEnabled(enabled)
        self.btn_rename.setEnabled(enabled)
        self.btn_reveal.setEnabled(enabled)
        self.btn_remove.setEnabled(enabled)
        self.btn_delete.setEnabled(enabled)

    def _get_selected_project(self) -> Optional[Dict[str, str]]:
        items = self.project_list.selectedItems()
        if items:
            return items[0].data(Qt.ItemDataRole.UserRole)
        return None

    def _on_item_double_clicked(self, item: QListWidgetItem):
        self._open_selected_project()

    def _open_selected_project(self):
        p = self._get_selected_project()
        if not p:
            return
        path = p.get("path")
        if not path or not os.path.isdir(path):
            QMessageBox.critical(self, "Project Missing", f"The directory '{path}' no longer exists on disk.")
            return

        self.project_opened.emit(path)

    def _run_selected_project(self):
        p = self._get_selected_project()
        if not p:
            return
        path = p.get("path")
        if not path or not os.path.isdir(path):
            QMessageBox.critical(self, "Project Missing", f"The directory '{path}' no longer exists on disk.")
            return

        import subprocess
        if getattr(sys, "frozen", False):
            subprocess.Popen([sys.executable, "--run", path])
        else:
            runner_script = resolve_resource_path("runner.py")
            subprocess.Popen([sys.executable, runner_script, path])

    def _reveal_in_explorer(self):
        p = self._get_selected_project()
        if not p:
            return
        path = p.get("path")
        if path and os.path.isdir(path):
            os.startfile(path)

    def _open_new_project_dialog(self):
        user_docs = os.path.expanduser("~/Documents")
        default_parent = os.path.join(user_docs, "HomiCraftProjects")
        os.makedirs(default_parent, exist_ok=True)

        dlg = NewProjectDialog(default_parent, parent=self)
        if dlg.exec():
            new_path = dlg.created_project_path
            name = dlg.inp_name.text().strip() or "Untitled"
            if new_path:
                self.projects = [p for p in self.projects if p.get("path") != new_path]
                self.projects.insert(0, {
                    "name": name,
                    "path": new_path,
                    "version": "1.0.0"
                })
                self._save_projects_list()
                self._populate_list()
                self.project_opened.emit(new_path)

    def _import_project(self):
        chosen = QFileDialog.getExistingDirectory(self, "Select Existing HomiCraft Project Folder")
        if not chosen:
            return

        proj_path = os.path.abspath(chosen)
        cfg_file = os.path.join(proj_path, "project.json")
        name = os.path.basename(proj_path)
        version = "1.0.0"
        if os.path.exists(cfg_file):
            try:
                with open(cfg_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    name = data.get("name", name)
                    version = data.get("version", version)
            except Exception:
                pass

        self.projects = [p for p in self.projects if p.get("path") != proj_path]
        self.projects.insert(0, {
            "name": name,
            "path": proj_path,
            "version": version
        })
        self._save_projects_list()
        self._populate_list()
        QMessageBox.information(self, "Import Successful", f"Project '{name}' was added to your project list!")

    def _rename_selected_project(self):
        p = self._get_selected_project()
        if not p:
            return
        old_name = p.get("name", "Untitled")
        new_name, ok = QInputDialog.getText(
            self,
            "Rename Project",
            "Enter new project name:",
            QLineEdit.EchoMode.Normal,
            old_name
        )
        if ok and new_name.strip() and new_name.strip() != old_name:
            new_name = new_name.strip()
            p["name"] = new_name
            proj_path = p.get("path")
            if proj_path and os.path.isdir(proj_path):
                cfg_path = os.path.join(proj_path, "project.json")
                if os.path.exists(cfg_path):
                    try:
                        cfg = load_project_config(cfg_path)
                        cfg.name = new_name
                        cfg.window_title = new_name
                        save_project_config(cfg_path, cfg)
                    except Exception:
                        pass
            self._save_projects_list()
            self._populate_list()

    def _remove_selected_project(self):
        p = self._get_selected_project()
        if not p:
            return

        name = p.get("name", "Project")
        reply = QMessageBox.question(
            self,
            "Remove From List",
            f"Remove '{name}' from the Project Manager list?\n\n(This will NOT delete any files on disk)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.projects = [item for item in self.projects if item.get("path") != p.get("path")]
            self._save_projects_list()
            self._populate_list()

    def _delete_project_files(self):
        p = self._get_selected_project()
        if not p:
            return
        name = p.get("name", "Project")
        path = p.get("path", "")

        reply = QMessageBox.warning(
            self,
            "⚠️ Delete Project Permanently",
            f"Are you sure you want to permanently delete the project '{name}' and all its files from disk?\n\nPath: {path}\n\nWARNING: THIS ACTION CANNOT BE UNDONE!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if path and os.path.isdir(path):
                try:
                    shutil.rmtree(path, ignore_errors=True)
                except Exception as e:
                    QMessageBox.critical(self, "Deletion Error", f"Failed to delete directory: {e}")
                    return
            self.projects = [item for item in self.projects if item.get("path") != path]
            self._save_projects_list()
            self._populate_list()
            QMessageBox.information(self, "Project Deleted", f"Project '{name}' was permanently deleted from disk.")
