"""
HomiCraft Runtime Engine
Dynamically loads UI JSON scenes, builds PySide6 widget hierarchies,
binds Python controller scripts, and executes the user's application.
"""

from __future__ import annotations
import os
import sys
import importlib.util
import inspect
from typing import Dict, Any, Optional
from PySide6.QtWidgets import QMainWindow, QWidget, QApplication
from PySide6.QtCore import Qt

from core.schema import ProjectConfig, WidgetNode, load_project_config, load_scene
from core.registry import WIDGET_REGISTRY, apply_widget_properties


class HomiAppContext:
    """
    Context object passed to user Python scripts.
    Allows accessing any widget by its ID:
        app.my_button.setText("Clicked!")
    Just like `get_node("my_button")` in Godot!
    """
    def __init__(self, window: HomiRuntimeWindow):
        self._window = window
        self._widgets: Dict[str, QWidget] = {}
        self.state: Dict[str, Any] = {}

    def _register_widget(self, widget_id: str, widget_instance: QWidget) -> None:
        self._widgets[widget_id] = widget_instance
        setattr(self, widget_id, widget_instance)

    def get_widget(self, widget_id: str) -> Optional[QWidget]:
        return self._widgets.get(widget_id)

    @property
    def window(self) -> HomiRuntimeWindow:
        return self._window

    def close(self) -> None:
        self._window.close()


class HomiRuntimeWindow(QMainWindow):
    """The host window that displays a loaded HomiCraft scene."""

    def __init__(self, project_dir: str):
        super().__init__()
        self.project_dir = os.path.abspath(project_dir)
        self.project_config: ProjectConfig = ProjectConfig()
        self.context = HomiAppContext(self)
        self.user_module = None

        self._central_widget = QWidget(self)
        self.setCentralWidget(self._central_widget)

        self._load_and_build()

    def _load_and_build(self) -> None:
        # 1. Load project.json
        proj_path = os.path.join(self.project_dir, "project.json")
        if os.path.exists(proj_path):
            self.project_config = load_project_config(proj_path)
            self.setWindowTitle(self.project_config.window_title)
            self.resize(self.project_config.window_width, self.project_config.window_height)
            if not self.project_config.window_resizable:
                self.setFixedSize(self.project_config.window_width, self.project_config.window_height)

        # 2. Load Entry Scene
        scene_path = os.path.join(self.project_dir, self.project_config.entry_scene)
        if not os.path.exists(scene_path):
            raise FileNotFoundError(f"Scene file not found: {scene_path}")

        scene_root = load_scene(scene_path)

        # 3. Load user Python script (e.g. main.py)
        script_path = os.path.join(self.project_dir, "main.py")
        if os.path.exists(script_path):
            self._load_user_script(script_path)

        # 4. Instantiate widgets recursively
        self._build_node(scene_root, self._central_widget)

        # 5. Call ready / _ready hook if defined (just like Godot!)
        if self.user_module:
            ready_func = getattr(self.user_module, "ready", None) or getattr(self.user_module, "_ready", None)
            if ready_func and callable(ready_func):
                ready_func(self.context)

    def _load_user_script(self, script_path: str) -> None:
        module_name = "homi_user_script"
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            self.user_module = module

    def _build_node(self, node: WidgetNode, parent_widget: QWidget) -> None:
        # If node is the root Window itself, apply root properties
        if node.type in ("Window", "Root"):
            if "title" in node.properties:
                self.setWindowTitle(str(node.properties["title"]))
            if "styleSheet" in node.properties:
                self._central_widget.setStyleSheet(str(node.properties["styleSheet"]))
        else:
            meta = WIDGET_REGISTRY.get(node.type)
            if not meta:
                print(f"[HomiCraft Runtime] Warning: Unknown widget type '{node.type}'")
                return

            # Instantiate PySide6 widget
            qt_instance = meta.qt_class(parent_widget)
            
            # Special setup for slider orientation
            if node.type == "Slider":
                qt_instance.setOrientation(Qt.Orientation.Horizontal)

            # Set geometry (Absolute positioning)
            qt_instance.setGeometry(node.x, node.y, node.width, node.height)

            # Apply properties (merge defaults + custom)
            merged_props = dict(meta.default_props)
            merged_props.update(node.properties)
            apply_widget_properties(qt_instance, merged_props)

            # Register in context
            self.context._register_widget(node.id, qt_instance)

            # Connect Signals to User Script functions
            self._bind_signals(node, qt_instance)

            # Recurse children if any
            for child in node.children:
                self._build_node(child, qt_instance)
            return

        # For root node, process its children
        for child in node.children:
            self._build_node(child, parent_widget)

    def _bind_signals(self, node: WidgetNode, qt_instance: QWidget) -> None:
        if not self.user_module:
            return

        for signal_name, callback_name in node.signals.items():
            handler = getattr(self.user_module, callback_name, None)
            if not handler or not callable(handler):
                print(f"[HomiCraft Runtime] Warning: Callback function '{callback_name}' not found in script for {node.id}.{signal_name}")
                continue

            # Look up Qt signal object
            qt_signal = getattr(qt_instance, signal_name, None)
            if not qt_signal:
                print(f"[HomiCraft Runtime] Warning: Signal '{signal_name}' not supported on {node.type}")
                continue

            # Determine parameter count of the user's function
            sig = inspect.signature(handler)
            param_count = len(sig.parameters)

            # Create signal forwarder
            def make_slot(fn, params_len):
                def slot(*args):
                    try:
                        if params_len == 0:
                            fn()
                        elif params_len == 1:
                            fn(self.context)
                        else:
                            # Pass app context + signal arguments
                            fn(self.context, *args)
                    except Exception as e:
                        print(f"[HomiCraft Runtime Error in {fn.__name__}]: {e}", file=sys.stderr)
                return slot

            qt_signal.connect(make_slot(handler, param_count))
