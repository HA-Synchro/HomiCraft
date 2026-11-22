"""
HomiCraft IDE Main Window
The central visual development environment integrating Canvas, Hierarchy,
Inspector, Script Editor, App Runner, and Standalone Exporter.
"""

import os
import sys
import copy
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QDockWidget, QTabWidget, QVBoxLayout,
    QHBoxLayout, QToolBar, QPushButton, QLabel, QFileDialog,
    QPlainTextEdit, QScrollArea, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt, QProcess, QKeyCombination
from PySide6.QtGui import QAction, QIcon, QKeySequence

from core.schema import (
    ProjectConfig, WidgetNode, save_project_config, load_project_config,
    save_scene, load_scene
)
from core.registry import WIDGET_REGISTRY
from editor.canvas import DesignCanvas
from editor.palette import WidgetPalette
from editor.hierarchy import HierarchyDock
from editor.inspector import InspectorDock
from editor.code_editor import ScriptEditorTab
from editor.export_dialog import ExportDialog


class HomiCraftEditorWindow(QMainWindow):
    def __init__(self, project_dir: Optional[str] = None):
        super().__init__()
        self.setWindowTitle("HomiCraft — Software Engine")
        self.resize(1340, 840)

        self.project_dir: Optional[str] = None
        self.project_config: ProjectConfig = ProjectConfig()
        self.root_node: WidgetNode = WidgetNode(id="root_window", type="Window")

        # Background runner process (F5)
        self.runner_process: Optional[QProcess] = None

        self._init_ui()

        # Load initial project or default demo
        if project_dir and os.path.isdir(project_dir):
            self.load_project(project_dir)
        else:
            default_demo = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "examples", "counter_app"))
            if os.path.exists(default_demo):
                self.load_project(default_demo)
            else:
                self.new_default_project()

    def _init_ui(self) -> None:
        self.setStyleSheet("""
            QMainWindow {
                background-color: #16161c;
                color: #e0e0e0;
            }
            QToolBar {
                background-color: #202028;
                border-bottom: 1px solid #333340;
                spacing: 8px;
                padding: 4px;
            }
            QDockWidget {
                background-color: #1e1e24;
                color: #e0e0e0;
                font-weight: bold;
            }
            QDockWidget::title {
                background-color: #262630;
                padding: 6px;
                border-radius: 4px;
            }
            QTabWidget::pane {
                border: 1px solid #333340;
                background-color: #18181f;
            }
            QTabBar::tab {
                background: #25252e;
                color: #b0bec5;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background: #37474f;
                color: #4ecdc4;
                font-weight: bold;
            }
            QPushButton {
                background-color: #2e2e38;
                color: #ffffff;
                border: 1px solid #404050;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #3e3e4a;
            }
        """)

        # 1. Central Tab Widget (Visual Canvas + Script Editor)
        self.center_tabs = QTabWidget(self)
        self.setCentralWidget(self.center_tabs)

        # Tab 0: Visual Canvas wrapped in scroll area
        self.canvas_scroll = QScrollArea(self)
        self.canvas_scroll.setWidgetResizable(True)
        self.canvas_scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.canvas_scroll.setStyleSheet("background-color: #121217; border: none;")

        self.canvas = DesignCanvas(self)
        self.canvas_scroll.setWidget(self.canvas)
        self.center_tabs.addTab(self.canvas_scroll, "🎨 Visual Canvas")

        # Tab 1: Script Editor
        self.script_tab = ScriptEditorTab(self)
        self.center_tabs.addTab(self.script_tab, "🐍 Script Editor (main.py)")

        # 2. Docks
        self._setup_docks()

        # 3. Toolbar
        self._setup_toolbar()

        # 4. Wire signals between components
        self._connect_signals()

    def _setup_toolbar(self) -> None:
        toolbar = QToolBar("Main Toolbar", self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Open Project
        btn_open = QPushButton("📁 Open")
        btn_open.clicked.connect(self._on_open_project_clicked)
        toolbar.addWidget(btn_open)

        # Save Project (Ctrl+S)
        btn_save = QPushButton("💾 Save (Ctrl+S)")
        btn_save.clicked.connect(self.save_current_project)
        btn_save.setShortcut(QKeySequence("Ctrl+S"))
        toolbar.addWidget(btn_save)

        toolbar.addSeparator()

        # Duplicate (Ctrl+D)
        btn_dup = QPushButton("📋 Duplicate (Ctrl+D)")
        btn_dup.clicked.connect(self._on_duplicate_clicked)
        btn_dup.setShortcut(QKeySequence("Ctrl+D"))
        toolbar.addWidget(btn_dup)

        # Center Alignment Quick Buttons
        btn_center_h = QPushButton("↔ Center H")
        btn_center_h.clicked.connect(self._align_center_horizontal)
        toolbar.addWidget(btn_center_h)

        btn_center_v = QPushButton("↕ Center V")
        btn_center_v.clicked.connect(self._align_center_vertical)
        toolbar.addWidget(btn_center_v)

        toolbar.addSeparator()

        # Run Button (F5)
        self.btn_run = QPushButton("▶ Run (F5)")
        self.btn_run.setStyleSheet("""
            QPushButton {
                background-color: #2e7d32;
                color: white;
                font-weight: bold;
                padding: 6px 14px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #388e3c; }
        """)
        self.btn_run.clicked.connect(self.run_project)
        self.btn_run.setShortcut(QKeySequence("F5"))
        toolbar.addWidget(self.btn_run)

        # Stop Button
        self.btn_stop = QPushButton("⏹ Stop")
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background-color: #c62828;
                color: white;
                font-weight: bold;
                padding: 6px 14px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #d32f2f; }
        """)
        self.btn_stop.clicked.connect(self.stop_project)
        self.btn_stop.setEnabled(False)
        toolbar.addWidget(self.btn_stop)

        toolbar.addSeparator()

        # Export Standalone .EXE
        btn_export = QPushButton("📦 Export .EXE")
        btn_export.setStyleSheet("""
            QPushButton {
                background-color: #0288d1;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #039be5; }
        """)
        btn_export.clicked.connect(self._on_export_clicked)
        toolbar.addWidget(btn_export)

        toolbar.addSeparator()

        # Grid Toggle
        chk_grid = QCheckBox("Grid Snap (10px)")
        chk_grid.setChecked(True)
        chk_grid.toggled.connect(lambda state: setattr(self.canvas, "grid_enabled", state) or self.canvas.overlay.update())
        toolbar.addWidget(chk_grid)

    def _setup_docks(self) -> None:
        # Left Dock: Palette & Hierarchy
        self.dock_left = QDockWidget("Project & Hierarchy", self)
        self.dock_left.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        left_tabs = QTabWidget()
        
        self.palette = WidgetPalette(self)
        self.hierarchy = HierarchyDock(self)
        left_tabs.addTab(self.palette, "Widgets")
        left_tabs.addTab(self.hierarchy, "Hierarchy")
        self.dock_left.setWidget(left_tabs)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_left)

        # Right Dock: Inspector
        self.dock_right = QDockWidget("Property Inspector", self)
        self.dock_right.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.inspector = InspectorDock(self)
        self.dock_right.setWidget(self.inspector)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_right)

        # Bottom Dock: Output Console
        self.dock_bottom = QDockWidget("Output & Debug Console", self)
        self.dock_bottom.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self.console = QPlainTextEdit(self)
        self.console.setReadOnly(True)
        self.console.setStyleSheet("background-color: #121217; color: #a4b0be; font-family: Consolas; font-size: 11px;")
        self.dock_bottom.setWidget(self.console)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dock_bottom)

    def _connect_signals(self) -> None:
        # Palette spawns widget
        self.palette.widget_spawn_requested.connect(self._spawn_widget)

        # Canvas selection, modification, delete, duplicate, double-click
        self.canvas.node_selected.connect(self._on_canvas_node_selected)
        self.canvas.node_modified.connect(self._on_canvas_node_modified)
        self.canvas.node_delete_requested.connect(self._delete_node_by_id)
        self.canvas.node_duplicate_requested.connect(self._duplicate_node_by_id)
        self.canvas.node_double_clicked.connect(self._on_canvas_double_clicked)

        # Hierarchy selection & deletion
        self.hierarchy.node_selected.connect(self.canvas.select_node_by_id)
        self.hierarchy.node_delete_requested.connect(self._delete_node_by_id)

        # Inspector updates & resize
        self.inspector.property_changed.connect(self._on_inspector_property_changed)
        self.inspector.connect_signal_requested.connect(self._on_connect_signal_requested)
        self.inspector.window_resized.connect(self._on_window_resized)

    def _spawn_widget(self, type_name: str) -> None:
        meta = WIDGET_REGISTRY.get(type_name)
        if not meta or not self.root_node:
            return

        counter = 1
        base_id = type_name.lower()
        new_id = f"{base_id}_{counter}"
        existing_ids = {c.id for c in self.root_node.children}
        while new_id in existing_ids:
            counter += 1
            new_id = f"{base_id}_{counter}"

        spawn_x = (self.canvas.width() // 2) - (meta.default_size[0] // 2)
        spawn_y = (self.canvas.height() // 2) - (meta.default_size[1] // 2)

        node = WidgetNode(
            id=new_id,
            type=type_name,
            x=max(20, spawn_x),
            y=max(20, spawn_y),
            width=meta.default_size[0],
            height=meta.default_size[1],
            properties=dict(meta.default_props)
        )

        self.root_node.children.append(node)
        self.canvas.rebuild_visuals()
        self.hierarchy.populate(self.root_node, active_node_id=node.id)
        self.canvas.select_node_by_id(node.id)
        self.log(f"Added widget: {node.id} ({node.type})")

    def _duplicate_node_by_id(self, node_id: str) -> None:
        if not self.root_node or node_id == self.root_node.id:
            return

        target_node = None
        for child in self.root_node.children:
            if child.id == node_id:
                target_node = child
                break

        if not target_node:
            return

        # Deep copy node
        new_node = copy.deepcopy(target_node)
        counter = 1
        base_id = target_node.type.lower()
        new_id = f"{base_id}_{counter}"
        existing_ids = {c.id for c in self.root_node.children}
        while new_id in existing_ids:
            counter += 1
            new_id = f"{base_id}_{counter}"

        new_node.id = new_id
        new_node.x = min(self.canvas.width() - new_node.width, target_node.x + 20)
        new_node.y = min(self.canvas.height() - new_node.height, target_node.y + 20)

        self.root_node.children.append(new_node)
        self.canvas.rebuild_visuals()
        self.hierarchy.populate(self.root_node, active_node_id=new_node.id)
        self.canvas.select_node_by_id(new_node.id)
        self.log(f"Duplicated {node_id} -> {new_node.id}")

    def _on_duplicate_clicked(self) -> None:
        if self.canvas.selected_node and self.canvas.selected_node.id != "root_window":
            self._duplicate_node_by_id(self.canvas.selected_node.id)

    def _align_center_horizontal(self) -> None:
        node = self.canvas.selected_node
        if node and node.id != "root_window":
            node.x = max(0, (self.canvas.width() - node.width) // 2)
            if self.canvas.grid_enabled:
                node.x = round(node.x / self.canvas.grid_size) * self.canvas.grid_size
            self.canvas.rebuild_visuals()
            self.inspector.inspect_node(node)
            self.log(f"Centered {node.id} horizontally to X={node.x}")

    def _align_center_vertical(self) -> None:
        node = self.canvas.selected_node
        if node and node.id != "root_window":
            node.y = max(0, (self.canvas.height() - node.height) // 2)
            if self.canvas.grid_enabled:
                node.y = round(node.y / self.canvas.grid_size) * self.canvas.grid_size
            self.canvas.rebuild_visuals()
            self.inspector.inspect_node(node)
            self.log(f"Centered {node.id} vertically to Y={node.y}")

    def _on_canvas_node_selected(self, node: Optional[WidgetNode]) -> None:
        self.inspector.inspect_node(node)
        if node:
            self.hierarchy.select_node(node.id)

    def _on_canvas_node_modified(self, node: WidgetNode) -> None:
        self.inspector.inspect_node(node)

    def _on_canvas_double_clicked(self, node: WidgetNode) -> None:
        meta = WIDGET_REGISTRY.get(node.type)
        if meta and meta.supported_signals:
            primary_sig = meta.supported_signals[0]
            cb_name = node.signals.get(primary_sig, f"on_{node.id}_{primary_sig}")
            node.signals[primary_sig] = cb_name
            self._on_connect_signal_requested(node.id, primary_sig, cb_name)

    def _on_inspector_property_changed(self, node: WidgetNode) -> None:
        self.canvas.rebuild_visuals()
        self.hierarchy.populate(self.root_node, active_node_id=node.id)

    def _on_window_resized(self, width: int, height: int) -> None:
        self.project_config.window_width = width
        self.project_config.window_height = height
        self.canvas.setFixedSize(width, height)
        self.log(f"Resized canvas window to {width}x{height}")

    def _on_connect_signal_requested(self, node_id: str, sig_name: str, callback_name: str) -> None:
        self.center_tabs.setCurrentWidget(self.script_tab)
        self.script_tab.editor.append_callback_scaffold(callback_name, sig_name)
        self.log(f"Linked signal '{node_id}.{sig_name}' -> '{callback_name}()'")

    def _delete_node_by_id(self, node_id: str) -> None:
        if not self.root_node or node_id == self.root_node.id:
            return

        self.root_node.children = [c for c in self.root_node.children if c.id != node_id]
        self.canvas.rebuild_visuals()
        self.hierarchy.populate(self.root_node)
        self.inspector.inspect_node(None)
        self.log(f"Deleted node: {node_id}")

    def log(self, text: str) -> None:
        self.console.appendPlainText(f"[HomiCraft] {text}")

    def new_default_project(self) -> None:
        self.project_dir = None
        self.project_config = ProjectConfig(name="Untitled App", window_width=600, window_height=400)
        self.root_node = WidgetNode(id="root_window", type="Window")
        self.canvas.set_scene(self.root_node, 600, 400)
        self.hierarchy.populate(self.root_node)
        self.script_tab.load_code("# HomiCraft App Script\n\ndef _ready(app):\n    pass\n")

    def load_project(self, project_dir: str) -> None:
        self.project_dir = os.path.abspath(project_dir)
        proj_file = os.path.join(self.project_dir, "project.json")
        if os.path.exists(proj_file):
            self.project_config = load_project_config(proj_file)
        else:
            self.project_config = ProjectConfig()

        scene_file = os.path.join(self.project_dir, self.project_config.entry_scene)
        if os.path.exists(scene_file):
            self.root_node = load_scene(scene_file)
        else:
            self.root_node = WidgetNode(id="root_window", type="Window")

        self.canvas.set_scene(self.root_node, self.project_config.window_width, self.project_config.window_height)
        self.hierarchy.populate(self.root_node)
        self.inspector.inspect_node(None)

        script_file = os.path.join(self.project_dir, "main.py")
        if os.path.exists(script_file):
            with open(script_file, "r", encoding="utf-8") as f:
                self.script_tab.load_code(f.read())
        else:
            self.script_tab.load_code("# HomiCraft App Script\n\ndef _ready(app):\n    pass\n")

        self.setWindowTitle(f"HomiCraft — {self.project_config.name} ({self.project_dir})")
        self.log(f"Loaded project from {self.project_dir}")

    def save_current_project(self) -> None:
        if not self.project_dir:
            chosen = QFileDialog.getExistingDirectory(self, "Select Project Folder")
            if not chosen:
                return
            self.project_dir = chosen

        os.makedirs(self.project_dir, exist_ok=True)

        # 1. Save project.json
        proj_path = os.path.join(self.project_dir, "project.json")
        save_project_config(proj_path, self.project_config)

        # 2. Save scene file
        scene_path = os.path.join(self.project_dir, self.project_config.entry_scene)
        save_scene(scene_path, self.root_node)

        # 3. Save main.py
        script_path = os.path.join(self.project_dir, "main.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(self.script_tab.get_code())

        self.log(f"Project saved successfully to {self.project_dir}")

    def _on_open_project_clicked(self) -> None:
        chosen = QFileDialog.getExistingDirectory(self, "Open HomiCraft Project")
        if chosen:
            self.load_project(chosen)

    def _on_export_clicked(self) -> None:
        self.save_current_project()
        if not self.project_dir:
            return
        dlg = ExportDialog(self.project_dir, default_name=self.project_config.name.replace(" ", ""), parent=self)
        dlg.exec()

    def run_project(self) -> None:
        self.save_current_project()

        if self.runner_process and self.runner_process.state() == QProcess.ProcessState.Running:
            self.log("Stopping previous instance...")
            self.runner_process.kill()
            self.runner_process.waitForFinished(1000)

        runner_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "runner.py"))
        
        self.log("▶ Launching project runtime...")
        self.runner_process = QProcess(self)
        self.runner_process.readyReadStandardOutput.connect(self._on_process_stdout)
        self.runner_process.readyReadStandardError.connect(self._on_process_stderr)
        self.runner_process.finished.connect(self._on_process_finished)

        self.btn_run.setEnabled(False)
        self.btn_stop.setEnabled(True)

        self.runner_process.start(sys.executable, [runner_script, self.project_dir])

    def stop_project(self) -> None:
        if self.runner_process and self.runner_process.state() == QProcess.ProcessState.Running:
            self.runner_process.kill()
            self.log("⏹ Application stopped by user.")

    def _on_process_stdout(self) -> None:
        if self.runner_process:
            data = self.runner_process.readAllStandardOutput().data().decode("utf-8", errors="replace")
            self.console.appendPlainText(data.strip())

    def _on_process_stderr(self) -> None:
        if self.runner_process:
            data = self.runner_process.readAllStandardError().data().decode("utf-8", errors="replace")
            self.console.appendPlainText(f"[ERROR] {data.strip()}")

    def _on_process_finished(self, exit_code, exit_status) -> None:
        self.log(f"Application closed (exit code: {exit_code}).")
        self.btn_run.setEnabled(True)
        self.btn_stop.setEnabled(False)
