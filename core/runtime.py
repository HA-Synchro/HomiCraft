"""
HomiCraft Runtime Engine
Dynamically loads UI JSON scenes, builds PySide6 widget hierarchies,
wraps widgets into Pythonic HomiWidgetProxy objects, and executes the user's application.
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
from core.proxy import HomiWidgetProxy


class HomiAppContext:
    """
    Context object passed to user Python scripts.
    Allows accessing any widget by its ID:
        app.button_1.text = "Clicked!"
        app.button_1.enabled = False
        app.slider.value = 80
    Just like `get_node("button_1")` in Godot!
    """
    def __init__(self, window: HomiRuntimeWindow):
        self._window = window
        self._widgets: Dict[str, HomiWidgetProxy] = {}
        self.state: Dict[str, Any] = {}

    def _register_widget(self, widget_id: str, widget_instance: QWidget) -> HomiWidgetProxy:
        proxy = HomiWidgetProxy(widget_instance, widget_id)
        self._widgets[widget_id] = proxy
        setattr(self, widget_id, proxy)
        return proxy

    def get_widget(self, widget_id: str) -> Optional[HomiWidgetProxy]:
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
        self.scene_module = None
        self.node_modules: Dict[str, Any] = {}

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

        # 3. Load Scene Python script (main.py)
        main_script_path = os.path.join(self.project_dir, "main.py")
        if os.path.exists(main_script_path):
            self.scene_module = self._load_script_module("homi_main_script", main_script_path)

        # 4. Instantiate widgets recursively
        self._build_node(scene_root, self._central_widget)

        # 5. Inject app context and widget proxies into all loaded modules
        self._inject_globals_into_modules()

        # 6. Call ready / _ready hook on scene script
        if self.scene_module:
            ready_func = getattr(self.scene_module, "ready", None) or getattr(self.scene_module, "_ready", None)
            if ready_func and callable(ready_func):
                sig = inspect.signature(ready_func)
                if len(sig.parameters) == 0:
                    ready_func()
                else:
                    ready_func(self.context)

    def _load_script_module(self, mod_name: str, script_path: str):
        if script_path in self.node_modules:
            return self.node_modules[script_path]
        try:
            spec = importlib.util.spec_from_file_location(mod_name, script_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[mod_name] = module
                spec.loader.exec_module(module)
                self.node_modules[script_path] = module
                return module
        except Exception as e:
            print(f"[HomiCraft Runtime Error loading {script_path}]: {e}", file=sys.stderr)
        return None

    def _inject_globals_into_modules(self) -> None:
        """Injects `app` and all widget proxies directly into loaded script modules."""
        all_modules = list(self.node_modules.values())
        if self.scene_module and self.scene_module not in all_modules:
            all_modules.append(self.scene_module)

        for mod in all_modules:
            # Provide global 'app'
            mod.__dict__["app"] = self.context
            # Provide direct widget variables (e.g. button_1, lbl_title)
            for widget_id, proxy in self.context._widgets.items():
                mod.__dict__[widget_id] = proxy

    def _build_node(self, node: WidgetNode, parent_widget: QWidget) -> None:
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

            qt_instance = meta.qt_class(parent_widget)
            
            if node.type == "Slider":
                qt_instance.setOrientation(Qt.Orientation.Horizontal)

            qt_instance.setGeometry(node.x, node.y, node.width, node.height)

            merged_props = dict(meta.default_props)
            merged_props.update(node.properties)
            apply_widget_properties(qt_instance, merged_props)

            # Register widget and get proxy
            proxy = self.context._register_widget(node.id, qt_instance)

            # Load node dedicated script if attached
            node_mod = None
            if node.script:
                node_script_path = os.path.join(self.project_dir, node.script)
                if os.path.exists(node_script_path):
                    node_mod = self._load_script_module(f"homi_{node.id}_script", node_script_path)
                    ready_fn = getattr(node_mod, "ready", None) or getattr(node_mod, "_ready", None)
                    if ready_fn and callable(ready_fn):
                        sig = inspect.signature(ready_fn)
                        if len(sig.parameters) == 0:
                            ready_fn()
                        else:
                            ready_fn(self.context)

            # Bind signals
            self._bind_signals(node, qt_instance, node_mod)

            for child in node.children:
                self._build_node(child, qt_instance)
            return

        for child in node.children:
            self._build_node(child, parent_widget)

    def _bind_signals(self, node: WidgetNode, qt_instance: QWidget, node_mod: Optional[Any]) -> None:
        if not node.signals:
            return

        for signal_name, callback_name in node.signals.items():
            handler = None
            if node_mod:
                handler = getattr(node_mod, callback_name, None)
            if not handler and self.scene_module:
                handler = getattr(self.scene_module, callback_name, None)

            if not handler or not callable(handler):
                print(f"[HomiCraft Runtime] Warning: Callback function '{callback_name}' not found for {node.id}.{signal_name}")
                continue

            qt_signal = getattr(qt_instance, signal_name, None)
            if not qt_signal:
                print(f"[HomiCraft Runtime] Warning: Signal '{signal_name}' not supported on {node.type}")
                continue

            sig = inspect.signature(handler)
            param_count = len(sig.parameters)

            def make_slot(fn, params_len):
                def slot(*args):
                    try:
                        if params_len == 0:
                            fn()
                        elif params_len == 1:
                            fn(self.context)
                        else:
                            fn(self.context, *args)
                    except Exception as e:
                        print(f"[HomiCraft Runtime Error in {fn.__name__}]: {e}", file=sys.stderr)
                return slot

            qt_signal.connect(make_slot(handler, param_count))
