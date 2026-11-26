"""
HomiCraft Signal Connection Dialog
Connects widget signals to callback methods in user scripts.
Detects already attached scripts (e.g. newbutton.py), lists existing functions,
and never creates a new script if one is already attached!
"""

import os
import re
from typing import Optional, List
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QRadioButton, QButtonGroup, QFrame, QComboBox
)
from PySide6.QtCore import Qt


class SignalConnectDialog(QDialog):
    def __init__(
        self,
        node_id: str,
        node_type: str,
        signal_name: str,
        attached_script: Optional[str] = None,
        project_dir: Optional[str] = None,
        parent=None
    ):
        super().__init__(parent)
        self.node_id = node_id
        self.signal_name = signal_name
        self.attached_script = attached_script
        self.project_dir = project_dir

        self.setWindowTitle("Connect Signal to Script")
        self.resize(500, 310)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e24;
                color: #e0e0e0;
            }
            QLabel { color: #cfd8dc; font-size: 12px; }
            QLineEdit, QComboBox {
                background-color: #2b2b36;
                color: white;
                border: 1px solid #455a64;
                border-radius: 4px;
                padding: 6px;
                font-family: Consolas;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #37474f;
                width: 20px;
            }
            QRadioButton {
                color: #eceff1;
                font-size: 12px;
                spacing: 8px;
            }
            QPushButton {
                background-color: #37474f;
                color: white;
                border-radius: 4px;
                padding: 6px 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #455a64; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Header info
        header = QLabel(f"🔗 Connect <b>{node_id}</b> ({node_type})")
        header.setStyleSheet("font-size: 15px; font-weight: bold; color: #4ecdc4;")
        layout.addWidget(header)

        sig_info = QLabel(f"Signal: <b style='color:#ffd166;'>{signal_name}()</b>")
        layout.addWidget(sig_info)

        # Target Script selection group
        group_frame = QFrame()
        group_frame.setStyleSheet("background-color: #252530; border-radius: 6px; padding: 8px;")
        gf_layout = QVBoxLayout(group_frame)
        gf_layout.addWidget(QLabel("<b>Target Script:</b>"))

        self.btn_group = QButtonGroup(self)

        if self.attached_script:
            # Script is already attached! USE IT AS PRIMARY!
            self.rb_attached = QRadioButton(f"Attached Script (🐍 {self.attached_script})")
            self.rb_attached.setChecked(True)
            self.rb_scene = QRadioButton("Scene Script (main.py)")
            self.target_custom_name = self.attached_script
        else:
            # No script attached yet
            self.rb_scene = QRadioButton("Scene Script (main.py)")
            self.rb_scene.setChecked(True)
            self.rb_attached = QRadioButton(f"Create & Attach Dedicated Script (🐍 {self.node_id}.py)")
            self.target_custom_name = f"{self.node_id}.py"

        self.btn_group.addButton(self.rb_attached, 1)
        self.btn_group.addButton(self.rb_scene, 2)
        gf_layout.addWidget(self.rb_attached)
        gf_layout.addWidget(self.rb_scene)
        layout.addWidget(group_frame)

        # Receiver Method Selection (Dropdown + Editable)
        form = QFormLayout()
        self.combo_method = QComboBox(self)
        self.combo_method.setEditable(True)
        form.addRow("Receiver Method:", self.combo_method)
        layout.addLayout(form)

        # Populate functions based on selected script
        self.rb_attached.toggled.connect(self._refresh_available_methods)
        self.rb_scene.toggled.connect(self._refresh_available_methods)
        self._refresh_available_methods()

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)

        self.btn_connect = QPushButton("🔗 Connect")
        self.btn_connect.setStyleSheet("background-color: #2e7d32; color: white;")
        self.btn_connect.clicked.connect(self.accept)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(self.btn_connect)
        layout.addLayout(btn_layout)

    def _get_active_target_script(self) -> str:
        if self.rb_attached.isChecked():
            return self.target_custom_name
        return "main.py"

    def _refresh_available_methods(self) -> None:
        target = self._get_active_target_script()
        default_name = f"_on_{self.node_id}_{self.signal_name}"

        self.combo_method.clear()
        self.combo_method.addItem(default_name)

        if self.project_dir:
            target_path = os.path.join(self.project_dir, target)
            if os.path.isfile(target_path):
                try:
                    with open(target_path, "r", encoding="utf-8") as f:
                        code = f.read()
                    # Find all def my_function(...) names
                    funcs = re.findall(r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", code)
                    for fn in funcs:
                        if fn != default_name:
                            self.combo_method.addItem(fn)
                except Exception:
                    pass

        self.combo_method.setCurrentText(default_name)

    def get_result(self) -> tuple[str, str]:
        """Returns (target_script_filename, method_name)"""
        target_script = self._get_active_target_script()
        method_name = self.combo_method.currentText().strip() or f"_on_{self.node_id}_{self.signal_name}"
        return target_script, method_name
