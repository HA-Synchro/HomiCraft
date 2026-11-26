"""
HomiCraft Inspector & Signals Dock
Provides real-time property editing for widgets and the root window,
along with drag & drop script attachment & signal event binding.
"""

import os
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QSpinBox, QCheckBox, QPushButton, QScrollArea, QFrame, QMessageBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent

from core.schema import WidgetNode
from core.registry import WIDGET_REGISTRY
from editor.connect_dialog import SignalConnectDialog


class ScriptDropSlot(QFrame):
    """
    Drop target for Python script files.
    Allows dragging any .py file directly from the FileSystem dock to attach it!
    """
    script_dropped = Signal(str, str)  # (filename, full_path)
    attach_clicked = Signal()
    detach_clicked = Signal()
    code_clicked = Signal(str)

    def __init__(self, current_script: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.current_script = current_script

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(6)

        if current_script:
            self.setStyleSheet("""
                QFrame {
                    background-color: #202b30;
                    border: 1px solid #4ecdc4;
                    border-radius: 5px;
                }
            """)
            lbl = QLabel(f"🐍 {current_script}")
            lbl.setStyleSheet("color: #4ecdc4; font-weight: bold; font-family: Consolas;")
            layout.addWidget(lbl)
            layout.addStretch()

            btn_code = QPushButton("📝 Code")
            btn_code.setStyleSheet("padding: 2px 6px; background-color: #2e4a46; font-size: 11px;")
            btn_code.clicked.connect(lambda: self.code_clicked.emit(current_script))
            layout.addWidget(btn_code)

            btn_detach = QPushButton("❌")
            btn_detach.setToolTip("Detach Script")
            btn_detach.setStyleSheet("padding: 2px 6px; background-color: #5c2020; font-size: 11px;")
            btn_detach.clicked.connect(self.detach_clicked.emit)
            layout.addWidget(btn_detach)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #1a1a22;
                    border: 1px dashed #607d8b;
                    border-radius: 5px;
                }
            """)
            lbl = QLabel("⤓ Drag .py script here")
            lbl.setStyleSheet("color: #78909c; font-style: italic; font-size: 11px;")
            layout.addWidget(lbl)
            layout.addStretch()

            btn_attach = QPushButton("📜 New")
            btn_attach.setToolTip("Create & Attach Dedicated Script")
            btn_attach.setStyleSheet("padding: 2px 8px; background-color: #2e4a46; color: #4ecdc4; font-size: 11px; font-weight: bold;")
            btn_attach.clicked.connect(self.attach_clicked.emit)
            layout.addWidget(btn_attach)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                fpath = url.toLocalFile()
                if fpath.endswith(".py"):
                    event.acceptProposedAction()
                    self.setStyleSheet("""
                        QFrame {
                            background-color: #253835;
                            border: 2px solid #4ecdc4;
                            border-radius: 5px;
                        }
                    """)
                    return
        event.ignore()

    def dragLeaveEvent(self, event):
        if self.current_script:
            self.setStyleSheet("QFrame { background-color: #202b30; border: 1px solid #4ecdc4; border-radius: 5px; }")
        else:
            self.setStyleSheet("QFrame { background-color: #1a1a22; border: 1px dashed #607d8b; border-radius: 5px; }")
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                fpath = url.toLocalFile()
                if fpath.endswith(".py"):
                    fname = os.path.basename(fpath)
                    event.acceptProposedAction()
                    self.script_dropped.emit(fname, fpath)
                    return
        event.ignore()


class InspectorDock(QWidget):
    property_changed = Signal(object)                      # Emits modified WidgetNode
    connect_signal_requested = Signal(str, str, str, str)  # (node_id, signal_name, callback_name, target_script)
    disconnect_signal_requested = Signal(str, str)         # (node_id, signal_name)
    jump_to_code_requested = Signal(str, str)              # (target_script, callback_name)
    attach_script_requested = Signal(str)                  # (node_id)
    detach_script_requested = Signal(str)                  # (node_id)
    script_dropped_on_node = Signal(str, str, str)         # (node_id, filename, full_path)
    window_resized = Signal(int, int)                      # (new_width, new_height)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_node: Optional[WidgetNode] = None
        self.project_dir: Optional[str] = None

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

        # 1. Identity section (ID, Type, Script Drop Target)
        self.form_layout.addRow(QLabel("<b>Identity</b>"))
        id_input = QLineEdit(node.id)
        id_input.textChanged.connect(self._on_id_changed)
        self.form_layout.addRow("Node ID:", id_input)

        type_lbl = QLabel(f"<b>{node.type}</b>")
        type_lbl.setStyleSheet("color: #4ecdc4;")
        self.form_layout.addRow("Type:", type_lbl)

        # Drag & Drop Script Target
        script_slot = ScriptDropSlot(node.script, self)
        script_slot.script_dropped.connect(lambda fname, fpath: self._on_script_dropped(fname, fpath))
        script_slot.attach_clicked.connect(lambda: self.attach_script_requested.emit(node.id))
        script_slot.detach_clicked.connect(lambda: self.detach_script_requested.emit(node.id))
        script_slot.code_clicked.connect(lambda s: self.jump_to_code_requested.emit(s, ""))
        self.form_layout.addRow("Script:", script_slot)

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
                    continue

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

            style_edit = QLineEdit(str(props.get("styleSheet", "")))
            style_edit.setPlaceholderText("e.g. background-color: #2b2b2b;")
            style_edit.textChanged.connect(lambda t: self._update_prop("styleSheet", t))
            self.form_layout.addRow("Style (CSS):", style_edit)

        # 4. Signals & Events Section
        if meta and meta.supported_signals:
            self.form_layout.addRow(QLabel("<b>⚡ Signals (Events)</b>"))
            for sig in meta.supported_signals:
                is_connected = sig in node.signals
                sig_row = QHBoxLayout()

                if is_connected:
                    cb_name = node.signals[sig]
                    lbl_status = QLabel(f"<span style='color:#06d6a0;'>🟢 {cb_name}()</span>")
                    lbl_status.setStyleSheet("font-family: Consolas; font-size: 11px;")

                    btn_code = QPushButton("📝 Code")
                    btn_code.setStyleSheet("padding: 2px 6px; background-color: #2e4a46; font-size: 11px;")
                    target_script = node.script or "main.py"
                    btn_code.clicked.connect(lambda checked=False, s=target_script, c=cb_name: self.jump_to_code_requested.emit(s, c))

                    btn_disconn = QPushButton("❌")
                    btn_disconn.setToolTip(f"Disconnect {sig}()")
                    btn_disconn.setStyleSheet("padding: 2px 6px; background-color: #5c2020; font-size: 11px;")
                    btn_disconn.clicked.connect(lambda checked=False, s=sig: self._on_disconnect_clicked(s))

                    sig_row.addWidget(lbl_status)
                    sig_row.addStretch()
                    sig_row.addWidget(btn_code)
                    sig_row.addWidget(btn_disconn)
                else:
                    lbl_status = QLabel("<span style='color:#78909c;'>⚪ Disconnected</span>")
                    lbl_status.setStyleSheet("font-size: 11px;")

                    btn_connect = QPushButton("🔗 Connect...")
                    btn_connect.setStyleSheet("padding: 3px 8px; background-color: #37474f; color: #4ecdc4; font-weight: bold; font-size: 11px;")
                    btn_connect.clicked.connect(lambda checked=False, s=sig: self._open_connect_dialog(s))

                    sig_row.addWidget(lbl_status)
                    sig_row.addStretch()
                    sig_row.addWidget(btn_connect)

                self.form_layout.addRow(f"• {sig}:", sig_row)

    def _on_script_dropped(self, filename: str, full_path: str) -> None:
        if not self.active_node:
            return
        self.active_node.script = filename
        self.script_dropped_on_node.emit(self.active_node.id, filename, full_path)
        self.inspect_node(self.active_node)
        self.property_changed.emit(self.active_node)

    def _open_connect_dialog(self, sig: str) -> None:
        if not self.active_node:
            return
        dlg = SignalConnectDialog(
            node_id=self.active_node.id,
            node_type=self.active_node.type,
            signal_name=sig,
            attached_script=self.active_node.script,
            project_dir=self.project_dir,
            parent=self
        )
        if dlg.exec():
            target_script, method_name = dlg.get_result()
            self.active_node.signals[sig] = method_name
            if target_script != "main.py":
                self.active_node.script = target_script
            self.connect_signal_requested.emit(self.active_node.id, sig, method_name, target_script)
            self.inspect_node(self.active_node)
            self.property_changed.emit(self.active_node)

    def _on_disconnect_clicked(self, sig: str) -> None:
        if not self.active_node:
            return
        self.active_node.signals.pop(sig, None)
        self.disconnect_signal_requested.emit(self.active_node.id, sig)
        self.inspect_node(self.active_node)
        self.property_changed.emit(self.active_node)

    def _inspect_root_window(self, node: WidgetNode) -> None:
        self.form_layout.addRow(QLabel("<b>Window Settings (Root)</b>"))
        
        title = node.properties.get("title", "My HomiCraft App")
        title_inp = QLineEdit(str(title))
        title_inp.textChanged.connect(lambda t: self._update_prop("title", t))
        self.form_layout.addRow("Title:", title_inp)

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
