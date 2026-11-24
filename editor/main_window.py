"""
HomiCraft IDE Main Window
The central visual development environment integrating Canvas, Hierarchy,
FileSystem Dock, Inspector, Multi-Script Editor, App Runner, and Standalone Exporter.
Styled with official Catppuccin palettes (Mocha, Macchiato, Frappé, Latte)
and rounded-corner UI inspired by catppuccin.com.
"""

import os
import sys
import copy
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QDockWidget, QTabWidget, QVBoxLayout,
    QHBoxLayout, QToolBar, QPushButton, QLabel, QFileDialog,
    QPlainTextEdit, QScrollArea, QMessageBox, QCheckBox, QComboBox
)
from PySide6.QtCore import Qt, QProcess, QSettings, Signal
from PySide6.QtGui import QAction, QIcon, QKeySequence

from core.schema import (
    ProjectConfig, WidgetNode, save_project_config, load_project_config,
    save_scene, load_scene
)
from core.registry import WIDGET_REGISTRY
from core.paths import resolve_resource_path
from editor.canvas import DesignCanvas
from editor.palette import WidgetPalette
from editor.hierarchy import HierarchyDock
from editor.filesystem import FileSystemDock
from editor.inspector import InspectorDock
from editor.code_editor import ScriptEditorTab
from editor.export_dialog import ExportDialog
from editor.theme import build_catppuccin_stylesheet, CATPPUCCIN_PALETTES


class HomiCraftEditorWindow(QMainWindow):
    project_manager_requested = Signal()

    def __init__(self, project_dir: Optional[str] = None):
        super().__init__()
        self.setWindowTitle("HomiCraft — Software Engine")
        self.resize(1420, 880)

        self.project_dir: Optional[str] = None
        self.project_config: ProjectConfig = ProjectConfig()
        self.root_node: WidgetNode = WidgetNode(id="root_window", type="Window")

        # Background runner process (F5)
        self.runner_process: Optional[QProcess] = None

        # Current Catppuccin flavor
        settings = QSettings("HomiCraft", "Theme")
        self.current_flavor = settings.value("flavor", "Mocha")

        # Full dock flexibility: allow nesting, tab grouping, and moving everywhere!
        self.setDockOptions(
            QMainWindow.DockOption.AnimatedDocks |
            QMainWindow.DockOption.AllowNestedDocks |
            QMainWindow.DockOption.AllowTabbedDocks |
            QMainWindow.DockOption.GroupedDragging
        )

        self._init_ui()
        self.apply_theme(self.current_flavor)

        if project_dir and os.path.isdir(project_dir):
            self.load_project(project_dir)
        else:
            default_demo = resolve_resource_path("examples", "counter_app")
            if os.path.exists(default_demo):
                self.load_project(default_demo)
            else:
                self.new_default_project()

    def _init_ui(self) -> None:
        # Central Workspace Tabs (Canvas + Script Editor)
        self.center_tabs = QTabWidget(self)
        self.setCentralWidget(self.center_tabs)

        # Tab 0: Visual Canvas wrapped in scroll area
        self.canvas_scroll = QScrollArea(self)
        self.canvas_scroll.setWidgetResizable(True)
        self.canvas_scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.canvas_scroll.setStyleSheet("background-color: transparent; border: none;")

        self.canvas = DesignCanvas(self)
        self.canvas_scroll.setWidget(self.canvas)
        self.center_tabs.addTab(self.canvas_scroll, "🎨 Visual Canvas")

        # Tab 1: Multi-Script Editor (Godot style)
        self.script_tab = ScriptEditorTab(self, self.current_flavor)
        self.center_tabs.addTab(self.script_tab, "🐍 Script Workspace")

        # Docks & Toolbar
        self._setup_docks()
        self._setup_toolbar()
        self._connect_signals()

    def _setup_toolbar(self) -> None:
        toolbar = QToolBar("Main Toolbar", self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        btn_pm = QPushButton("🏠 Projects")
        btn_pm.setToolTip("Return to HomiCraft Project Manager")
        btn_pm.clicked.connect(self._on_project_manager_clicked)
        toolbar.addWidget(btn_pm)

        btn_open = QPushButton("📁 Open")
        btn_open.clicked.connect(self._on_open_project_clicked)
        toolbar.addWidget(btn_open)

        btn_save = QPushButton("💾 Save (Ctrl+S)")
        btn_save.clicked.connect(self.save_current_project)
        btn_save.setShortcut(QKeySequence("Ctrl+S"))
        toolbar.addWidget(btn_save)

        toolbar.addSeparator()

        btn_dup = QPushButton("📋 Duplicate (Ctrl+D)")
        btn_dup.clicked.connect(self._on_duplicate_clicked)
        btn_dup.setShortcut(QKeySequence("Ctrl+D"))
        toolbar.addWidget(btn_dup)

        btn_center_h = QPushButton("↔ Center H")
        btn_center_h.clicked.connect(self._align_center_horizontal)
        toolbar.addWidget(btn_center_h)

        btn_center_v = QPushButton("↕ Center V")
        btn_center_v.clicked.connect(self._align_center_vertical)
        toolbar.addWidget(btn_center_v)

        toolbar.addSeparator()

        self.btn_run = QPushButton("▶ Run (F5)")
        self.btn_run.setObjectName("btn_run")
        self.btn_run.clicked.connect(self.run_project)
        self.btn_run.setShortcut(QKeySequence("F5"))
        toolbar.addWidget(self.btn_run)

        self.btn_stop = QPushButton("⏹ Stop")
        self.btn_stop.setObjectName("btn_stop")
        self.btn_stop.clicked.connect(self.stop_project)
        self.btn_stop.setEnabled(False)
        toolbar.addWidget(self.btn_stop)

        toolbar.addSeparator()

        btn_export = QPushButton("📦 Export .EXE")
        btn_export.setObjectName("btn_export")
        btn_export.clicked.connect(self._on_export_clicked)
        toolbar.addWidget(btn_export)

        toolbar.addSeparator()

        # Theme Selector (Catppuccin flavors)
        lbl_theme = QLabel("🎨 Theme:")
        lbl_theme.setStyleSheet("font-weight: bold; margin-left: 4px;")
        toolbar.addWidget(lbl_theme)

        self.combo_theme = QComboBox(self)
        self.combo_theme.addItems([
            "🌿 Mocha (Dark)",
            "☕ Macchiato (Medium)",
            "🍨 Frappé (Soft)",
            "🥛 Latte (Light)"
        ])
        
        # Set current index based on flavor
        flavor_to_idx = {"Mocha": 0, "Macchiato": 1, "Frappé": 2, "Latte": 3}
        self.combo_theme.setCurrentIndex(flavor_to_idx.get(self.current_flavor, 0))
        self.combo_theme.currentIndexChanged.connect(self._on_theme_changed)
        toolbar.addWidget(self.combo_theme)

        toolbar.addSeparator()

        btn_reset_layout = QPushButton("📐 Reset Layout")
        btn_reset_layout.setToolTip("Restore default Godot dock layout")
        btn_reset_layout.clicked.connect(self.reset_default_layout)
        toolbar.addWidget(btn_reset_layout)

        chk_grid = QCheckBox("Grid Snap (10px)")
        chk_grid.setChecked(True)
        chk_grid.toggled.connect(lambda state: setattr(self.canvas, "grid_enabled", state) or self.canvas.overlay.update())
        toolbar.addWidget(chk_grid)

    def _setup_docks(self) -> None:
        dock_features = (
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable |
            QDockWidget.DockWidgetFeature.DockWidgetClosable
        )

        # 1. Top-Left Dock: Hierarchy & Widget Palette tabs
        self.dock_scene = QDockWidget("Scene & Widgets", self)
        self.dock_scene.setObjectName("dock_scene")
        self.dock_scene.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.dock_scene.setFeatures(dock_features)
        
        scene_tabs = QTabWidget()
        self.hierarchy = HierarchyDock(self)
        self.palette = WidgetPalette(self)
        scene_tabs.addTab(self.hierarchy, "Hierarchy")
        scene_tabs.addTab(self.palette, "Widgets")
        self.dock_scene.setWidget(scene_tabs)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_scene)

        # 2. Bottom-Left Dock: FileSystem (res://) — Godot Style
        self.dock_filesystem = QDockWidget("FileSystem (res://)", self)
        self.dock_filesystem.setObjectName("dock_filesystem")
        self.dock_filesystem.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.dock_filesystem.setFeatures(dock_features)
        
        self.filesystem = FileSystemDock(self)
        self.dock_filesystem.setWidget(self.filesystem)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_filesystem)

        # 3. Right Dock: Property Inspector
        self.dock_right = QDockWidget("Property Inspector", self)
        self.dock_right.setObjectName("dock_right")
        self.dock_right.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.dock_right.setFeatures(dock_features)
        
        self.inspector = InspectorDock(self)
        self.dock_right.setWidget(self.inspector)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_right)

        # 4. Bottom Dock: Output & Debug Console
        self.dock_bottom = QDockWidget("Output & Debug Console", self)
        self.dock_bottom.setObjectName("dock_bottom")
        self.dock_bottom.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.dock_bottom.setFeatures(dock_features)
        
        self.console = QPlainTextEdit(self)
        self.console.setObjectName("console_output")
        self.console.setReadOnly(True)
        self.dock_bottom.setWidget(self.console)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dock_bottom)

    def _on_theme_changed(self, index: int) -> None:
        flavors = ["Mocha", "Macchiato", "Frappé", "Latte"]
        if 0 <= index < len(flavors):
            self.apply_theme(flavors[index])

    def apply_theme(self, flavor: str) -> None:
        self.current_flavor = flavor
        qss = build_catppuccin_stylesheet(flavor)
        self.setStyleSheet(qss)
        self.script_tab.apply_theme(flavor)
        
        # Save preference
        settings = QSettings("HomiCraft", "Theme")
        settings.setValue("flavor", flavor)
        self.log(f"Switched theme to Catppuccin {flavor}")

    def reset_default_layout(self) -> None:
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_scene)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_filesystem)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_right)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dock_bottom)
        
        self.dock_scene.show()
        self.dock_filesystem.show()
        self.dock_right.show()
        self.dock_bottom.show()
        self.log("Restored default dock layout.")

    def _connect_signals(self) -> None:
        self.palette.widget_spawn_requested.connect(self._spawn_widget)

        self.canvas.node_selected.connect(self._on_canvas_node_selected)
        self.canvas.node_modified.connect(self._on_canvas_node_modified)
        self.canvas.node_delete_requested.connect(self._delete_node_by_id)
        self.canvas.node_duplicate_requested.connect(self._duplicate_node_by_id)
        self.canvas.script_dropped_on_node.connect(self._on_script_dropped_on_node)

        self.hierarchy.node_selected.connect(self.canvas.select_node_by_id)
        self.hierarchy.node_delete_requested.connect(self._delete_node_by_id)

        # FileSystem dock signals
        self.filesystem.open_file_requested.connect(self._on_filesystem_file_opened)
        self.filesystem.script_created.connect(self._on_script_created)
        self.filesystem.file_renamed.connect(self._on_file_renamed)
        self.filesystem.file_deleted.connect(self._on_file_deleted)

        # Inspector interactions
        self.inspector.property_changed.connect(self._on_inspector_property_changed)
        self.inspector.connect_signal_requested.connect(self._on_connect_signal_requested)
        self.inspector.disconnect_signal_requested.connect(self._on_disconnect_signal_requested)
        self.inspector.jump_to_code_requested.connect(self._on_jump_to_code_requested)
        self.inspector.attach_script_requested.connect(self._on_attach_script_requested)
        self.inspector.detach_script_requested.connect(self._on_detach_script_requested)
        self.inspector.script_dropped_on_node.connect(self._on_script_dropped_on_node)
        self.inspector.window_resized.connect(self._on_window_resized)

    def _on_script_dropped_on_node(self, node_id: str, filename: str, full_path: str) -> None:
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.script_tab.open_script(filename, content)
        else:
            self.script_tab.open_script(filename, "")

        self.log(f"Attached '{filename}' to node '{node_id}' via drag-and-drop!")

    def _on_filesystem_file_opened(self, file_path: str) -> None:
        if not os.path.isfile(file_path):
            return

        fname = os.path.basename(file_path)

        if file_path.endswith(".py"):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.script_tab.open_script(fname, content)
            self.center_tabs.setCurrentWidget(self.script_tab)
            self.log(f"Opened script '{fname}' in editor.")

        elif file_path.endswith(".ui.json"):
            try:
                self.root_node = load_scene(file_path)
                self.canvas.set_scene(self.root_node, self.project_config.window_width, self.project_config.window_height)
                self.hierarchy.populate(self.root_node)
                self.center_tabs.setCurrentWidget(self.canvas_scroll)
                self.log(f"Loaded scene '{fname}' into canvas.")
            except Exception as e:
                self.log(f"Failed to load scene: {e}")

        else:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.script_tab.open_script(fname, content)
                self.center_tabs.setCurrentWidget(self.script_tab)
            except Exception:
                pass

    def _on_script_created(self, file_path: str) -> None:
        fname = os.path.basename(file_path)
        self.log(f"Created new Python script '{fname}'")

    def _on_file_renamed(self, old_path: str, new_path: str) -> None:
        old_name = os.path.basename(old_path)
        new_name = os.path.basename(new_path)
        self.script_tab.rename_script(old_name, new_name)
        self.log(f"Renamed '{old_name}' -> '{new_name}'")

    def _on_file_deleted(self, file_path: str) -> None:
        fname = os.path.basename(file_path)
        self.script_tab.close_script(fname)
        self.log(f"Deleted '{fname}'")

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
            script=None,
            signals={},
            properties=dict(meta.default_props)
        )

        self.root_node.children.append(node)
        self.canvas.rebuild_visuals()
        self.hierarchy.populate(self.root_node, active_node_id=node.id)
        self.update_script_autocomplete_nodes()
        self.canvas.select_node_by_id(node.id)
        self.log(f"Added new {node.type}: '{node.id}' (Unconnected)")

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

        new_node = copy.deepcopy(target_node)
        counter = 1
        base_id = target_node.type.lower()
        new_id = f"{base_id}_{counter}"
        existing_ids = {c.id for c in self.root_node.children}
        while new_id in existing_ids:
            counter += 1
            new_id = f"{base_id}_{counter}"

        new_node.id = new_id
        new_node.signals = {}
        new_node.x = min(self.canvas.width() - new_node.width, target_node.x + 20)
        new_node.y = min(self.canvas.height() - new_node.height, target_node.y + 20)

        self.root_node.children.append(new_node)
        self.canvas.rebuild_visuals()
        self.hierarchy.populate(self.root_node, active_node_id=new_node.id)
        self.update_script_autocomplete_nodes()
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

    def _on_inspector_property_changed(self, node: WidgetNode) -> None:
        self.canvas.rebuild_visuals()
        self.hierarchy.populate(self.root_node, active_node_id=node.id)

    def _on_window_resized(self, width: int, height: int) -> None:
        self.project_config.window_width = width
        self.project_config.window_height = height
        self.canvas.setFixedSize(width, height)
        self.log(f"Resized canvas window to {width}x{height}")

    def _on_connect_signal_requested(self, node_id: str, sig_name: str, callback_name: str, target_script: str) -> None:
        self.center_tabs.setCurrentWidget(self.script_tab)
        if target_script not in self.script_tab.editors and self.project_dir:
            target_path = os.path.join(self.project_dir, target_script)
            if os.path.isfile(target_path):
                with open(target_path, "r", encoding="utf-8") as f:
                    self.script_tab.open_script(target_script, f.read())
            else:
                self.script_tab.open_script(target_script, f'"""\n{target_script} — Controller Script\n"""\n\ndef _ready(app):\n    pass\n')
        self.script_tab.append_callback_scaffold(target_script, callback_name, sig_name)
        self.log(f"Connected signal '{node_id}.{sig_name}' -> '{callback_name}()' in {target_script}")

    def _on_disconnect_signal_requested(self, node_id: str, sig_name: str) -> None:
        if self.root_node:
            for child in self.root_node.children:
                if child.id == node_id:
                    child.signals.pop(sig_name, None)
                    break
        self.canvas.rebuild_visuals()
        self.log(f"Disconnected signal '{node_id}.{sig_name}'")

    def _on_jump_to_code_requested(self, target_script: str, callback_name: str) -> None:
        self.center_tabs.setCurrentWidget(self.script_tab)
        if callback_name:
            self.script_tab.jump_to_function(target_script, callback_name)
        else:
            self.script_tab.open_script(target_script)

    def _on_attach_script_requested(self, node_id: str) -> None:
        node = self.canvas.selected_node
        if not node or node.id != node_id:
            return

        script_name = f"{node_id}.py"
        node.script = script_name

        script_content = f'"""\nDedicated Controller Script for {node_id} ({node.type})\n"""\n\ndef _ready(app):\n    pass\n'
        self.script_tab.open_script(script_name, script_content)
        self.center_tabs.setCurrentWidget(self.script_tab)
        self.inspector.inspect_node(node)
        self.log(f"Attached script '{script_name}' to node '{node_id}'")

    def _on_detach_script_requested(self, node_id: str) -> None:
        node = self.canvas.selected_node
        if not node or node.id != node_id:
            return
        node.script = None
        self.inspector.inspect_node(node)
        self.log(f"Detached script from node '{node_id}'")

    def _delete_node_by_id(self, node_id: str) -> None:
        if not self.root_node or node_id == self.root_node.id:
            return

        self.root_node.children = [c for c in self.root_node.children if c.id != node_id]
        self.canvas.rebuild_visuals()
        self.hierarchy.populate(self.root_node)
        self.inspector.inspect_node(None)
        self.update_script_autocomplete_nodes()
        self.log(f"Deleted node: {node_id}")

    def get_all_node_ids(self) -> list[str]:
        ids = []
        if not self.root_node:
            return ids
        def _collect(node):
            if node.id and node.id != "root_window":
                ids.append(node.id)
            for child in node.children:
                _collect(child)
        _collect(self.root_node)
        return ids

    def update_script_autocomplete_nodes(self) -> None:
        if hasattr(self, "script_tab") and self.script_tab:
            self.script_tab.set_known_nodes(self.get_all_node_ids())

    def log(self, text: str) -> None:
        self.console.appendPlainText(f"[HomiCraft] {text}")

    def new_default_project(self) -> None:
        self.project_dir = None
        self.project_config = ProjectConfig(name="Untitled App", window_width=600, window_height=400)
        self.root_node = WidgetNode(id="root_window", type="Window")
        self.canvas.set_scene(self.root_node, 600, 400)
        self.hierarchy.populate(self.root_node)
        self.update_script_autocomplete_nodes()
        self.script_tab.open_script("main.py", "# HomiCraft App Script\n\ndef _ready(app):\n    pass\n")

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
        self.update_script_autocomplete_nodes()
        self.inspector.project_dir = self.project_dir
        self.inspector.inspect_node(None)

        self.filesystem.set_project_dir(self.project_dir)

        self.script_tab.editors.clear()
        while self.script_tab.tab_widget.count():
            self.script_tab.tab_widget.removeTab(0)

        main_py = os.path.join(self.project_dir, "main.py")
        if os.path.exists(main_py):
            with open(main_py, "r", encoding="utf-8") as f:
                self.script_tab.open_script("main.py", f.read())
        else:
            self.script_tab.open_script("main.py", "# HomiCraft App Script\n\ndef _ready(app):\n    pass\n")

        for fname in os.listdir(self.project_dir):
            if fname.endswith(".py") and fname != "main.py":
                fpath = os.path.join(self.project_dir, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    self.script_tab.open_script(fname, f.read())

        self.setWindowTitle(f"HomiCraft — {self.project_config.name} ({self.project_dir})")
        self.log(f"Loaded project from {self.project_dir}")

    def save_current_project(self) -> None:
        if not self.project_dir:
            chosen = QFileDialog.getExistingDirectory(self, "Select Project Folder")
            if not chosen:
                return
            self.project_dir = chosen

        os.makedirs(self.project_dir, exist_ok=True)

        proj_path = os.path.join(self.project_dir, "project.json")
        save_project_config(proj_path, self.project_config)

        scene_path = os.path.join(self.project_dir, self.project_config.entry_scene)
        save_scene(scene_path, self.root_node)

        for fname, content in self.script_tab.get_all_scripts().items():
            fpath = os.path.join(self.project_dir, fname)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)

        self.log(f"Project saved successfully to {self.project_dir}")

    def _on_project_manager_clicked(self) -> None:
        reply = QMessageBox.question(
            self,
            "Return to Project Manager",
            "Save current project before returning to Project Manager?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Yes
        )
        if reply == QMessageBox.StandardButton.Cancel:
            return
        if reply == QMessageBox.StandardButton.Yes:
            self.save_current_project()
        
        self.project_manager_requested.emit()

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

        if getattr(sys, "frozen", False):
            self.runner_process.start(sys.executable, ["--run", self.project_dir])
        else:
            runner_script = resolve_resource_path("runner.py")
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
