"""
HomiCraft Inspector & Signals Dock
Provides real-time property editing for widgets and the root window,
along with Godot-style signal event binding.
"""

from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QSpinBox, QCheckBox, QTextEdit, QPushButton, QScrollArea, QFrame
)
from PySide6.QtCore import Signal, Qt

from core.schema import WidgetNode
from core.registry import WIDGET_REGISTRY


class InspectorDock(QWidget):
    property_changed = Signal(object)  # Emits modified WidgetNode
    connect_signal_requested = Signal(str, str, str)  # (node_id, signal_name, callback_name)
    window_resized = Signal(int, int)  # Emits (new_width, new_height) when root window size changes

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_node: Optional[WidgetNode] = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        header = QLabel("🔍 Property Inspector")
        header.setStyleSheet("font-weight: bold; font-size: 13px; color: #4ecdc4; padding: 4px;")
        layout.addWidget(header)

        # Scrollable area for properties
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        self.container = QWidget()
        self.form_layout = QFormLayout(self.container)
        self.form_layout.setContentsMargins(4, 4, 4, 4)
        self.form_layout.setSpacing(8)
        scroll.setWidget(self.container)

        layout.addWidget(scroll)

    def inspect_node(self, node: Optional[WidgetNode]) -> None:
        self.active_node = node
        
        # Clear existing fields
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not node:
            lbl = QLabel("No item selected.\nClick a widget or canvas.")
            lbl.setStyleSheet("color: #78909c; font-style: italic; padding: 10px;")
            self.form_layout.addRow(lbl)
            return

        # Special Handling for Root Window
        if node.id == "root_window" or node.type in ("Window", "Root"):
            self._inspect_root_window(node)
            return

        # 1. Identity section
        self.form_layout.addRow(QLabel("<b>Identity</b>"))
        id_input = QLineEdit(node.id)
        id_input.textChanged.connect(self._on_id_changed)
        self.form_layout.addRow("Node ID:", id_input)

        type_lbl = QLabel(f"<b>{node.type}</b>")
        type_lbl.setStyleSheet("color: #4ecdc4;")
        self.form_layout.addRow("Type:", type_lbl)

        # 2. Geometry section (X, Y, Width, Height)
        self.form_layout.addRow(QLabel("<b>Transform & Geometry</b>"))
        
        spin_x = QSpinBox()
        spin_x.setRange(0, 4000)
        spin_x.setValue(node.x)
        spin_x.valueChanged.connect(lambda v: self._update_geom('x', v))
        self.form_layout.addRow("X:", spin_x)

        spin_y = QSpinBox()
        spin_y.setRange(0, 4000)
        spin_y.setValue(node.y)
        spin_y.valueChanged.connect(lambda v: self._update_geom('y', v))
        self.form_layout.addRow("Y:", spin_y)

        spin_w = QSpinBox()
        spin_w.setRange(10, 4000)
        spin_w.setValue(node.width)
        spin_w.valueChanged.connect(lambda v: self._update_geom('w', v))
        self.form_layout.addRow("Width:", spin_w)

        spin_h = QSpinBox()
        spin_h.setRange(10, 4000)
        spin_h.setValue(node.height)
        spin_h.valueChanged.connect(lambda v: self._update_geom('h', v))
        self.form_layout.addRow("Height:", spin_h)

        # 3. Widget Specific Properties
        meta = WIDGET_REGISTRY.get(node.type)
        if meta and meta.default_props:
            self.form_layout.addRow(QLabel("<b>Properties</b>"))
            props = dict(meta.default_props)
            props.update(node.properties)

            for key, default_val in props.items():
                if key == "styleSheet":
                    continue  # Style handled in custom field below

                val = props.get(key, default_val)
                if isinstance(default_val, bool):
                    chk = QCheckBox()
                    chk.setChecked(bool(val))
                    chk.toggled.connect(lambda state, k=key: self._update_prop(k, state))
                    self.form_layout.addRow(key.capitalize() + ":", chk)
                elif isinstance(default_val, int):
                    spin = QSpinBox()
                    spin.setRange(-10000, 10000)
                    spin.setValue(int(val))
                    spin.valueChanged.connect(lambda v, k=key: self._update_prop(k, v))
                    self.form_layout.addRow(key.capitalize() + ":", spin)
                else:
                    txt = QLineEdit(str(val))
                    txt.textChanged.connect(lambda t, k=key: self._update_prop(k, t))
                    self.form_layout.addRow(key.capitalize() + ":", txt)

            # Styling field (CSS/QSS)
            style_edit = QLineEdit(str(props.get("styleSheet", "")))
            style_edit.setPlaceholderText("e.g. background-color: #2b2b2b;")
            style_edit.textChanged.connect(lambda t: self._update_prop("styleSheet", t))
            self.form_layout.addRow("Style (CSS):", style_edit)

        # 4. Godot-style Signals Section
        if meta and meta.supported_signals:
            self.form_layout.addRow(QLabel("<b>⚡ Signals (Events)</b>"))
            for sig in meta.supported_signals:
                existing_cb = node.signals.get(sig, "")
                sig_row = QHBoxLayout()
                
                cb_input = QLineEdit(existing_cb)
                cb_input.setPlaceholderText(f"on_{node.id}_{sig}")
                cb_input.textChanged.connect(lambda t, s=sig: self._update_signal(s, t))
                
                connect_btn = QPushButton("⚡ Code")
                connect_btn.setStyleSheet("background-color: #37474f; color: #4ecdc4; font-weight: bold; padding: 3px 6px;")
                connect_btn.clicked.connect(lambda checked=False, s=sig, inp=cb_input: self._on_connect_clicked(s, inp))

                sig_row.addWidget(cb_input)
                sig_row.addWidget(connect_btn)
                self.form_layout.addRow(f"• {sig}:", sig_row)

    def _inspect_root_window(self, node: WidgetNode) -> None:
        self.form_layout.addRow(QLabel("<b>Window Settings (Root)</b>"))
        
        # Window Title
        title = node.properties.get("title", "My HomiCraft App")
        title_inp = QLineEdit(str(title))
        title_inp.textChanged.connect(lambda t: self._update_prop("title", t))
        self.form_layout.addRow("Title:", title_inp)

        # Window Width & Height
        width_spin = QSpinBox()
        width_spin.setRange(200, 3840)
        width_spin.setValue(node.width if node.width > 0 else 600)
        
        height_spin = QSpinBox()
        height_spin.setRange(200, 2160)
        height_spin.setValue(node.height if node.height > 0 else 400)

        def on_size_change():
            node.width = width_spin.value()
            node.height = height_spin.value()
            self.window_resized.emit(node.width, node.height)
            self.property_changed.emit(node)

        width_spin.valueChanged.connect(lambda _: on_size_change())
        height_spin.valueChanged.connect(lambda _: on_size_change())
        self.form_layout.addRow("Width:", width_spin)
        self.form_layout.addRow("Height:", height_spin)

        # Window Background CSS
        style_val = node.properties.get("styleSheet", "background-color: #1e1e24;")
        style_inp = QLineEdit(str(style_val))
        style_inp.setPlaceholderText("background-color: #1e1e24;")
        style_inp.textChanged.connect(lambda t: self._update_prop("styleSheet", t))
        self.form_layout.addRow("Background CSS:", style_inp)

    def _on_id_changed(self, new_id: str) -> None:
        if self.active_node and new_id.strip():
            self.active_node.id = new_id.strip()
            self.property_changed.emit(self.active_node)

    def _update_geom(self, field: str, val: int) -> None:
        if not self.active_node:
            return
        if field == 'x': self.active_node.x = val
        elif field == 'y': self.active_node.y = val
        elif field == 'w': self.active_node.width = val
        elif field == 'h': self.active_node.height = val
        self.property_changed.emit(self.active_node)

    def _update_prop(self, key: str, val) -> None:
        if not self.active_node:
            return
        self.active_node.properties[key] = val
        self.property_changed.emit(self.active_node)

    def _update_signal(self, sig: str, callback_name: str) -> None:
        if not self.active_node:
            return
        if callback_name.strip():
            self.active_node.signals[sig] = callback_name.strip()
        else:
            self.active_node.signals.pop(sig, None)
        self.property_changed.emit(self.active_node)

    def _on_connect_clicked(self, sig: str, cb_input: QLineEdit) -> None:
        if not self.active_node:
            return
        cb_name = cb_input.text().strip()
        if not cb_name:
            cb_name = f"on_{self.active_node.id}_{sig}"
            cb_input.setText(cb_name)
            self._update_signal(sig, cb_name)

        self.connect_signal_requested.emit(self.active_node.id, sig, cb_name)
