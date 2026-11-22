"""
HomiCraft Widget Palette Dock
Displays available UI widgets grouped by category. Clicking a widget adds it
to the current scene.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QToolBox, QPushButton, QScrollArea, QFrame, QLabel
)
from PySide6.QtCore import Signal, Qt
from core.registry import WIDGET_REGISTRY


class WidgetPalette(QWidget):
    widget_spawn_requested = Signal(str)  # Emits widget type string (e.g. "Button")

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        header = QLabel("📦 Widget Palette")
        header.setStyleSheet("font-weight: bold; font-size: 13px; color: #4ecdc4; padding: 4px;")
        layout.addWidget(header)

        self.toolbox = QToolBox(self)
        self.toolbox.setStyleSheet("""
            QToolBox::tab {
                background: #25252e;
                color: #e0e0e0;
                border-radius: 4px;
                font-weight: bold;
                padding: 4px;
            }
            QToolBox::tab:selected {
                background: #37474f;
                color: #4ecdc4;
            }
        """)

        # Group by category
        categories = {}
        for type_name, meta in WIDGET_REGISTRY.items():
            cat = meta.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append((type_name, meta))

        for cat_name, items in categories.items():
            cat_widget = QWidget()
            cat_layout = QVBoxLayout(cat_widget)
            cat_layout.setContentsMargins(4, 6, 4, 6)
            cat_layout.setSpacing(4)

            for type_name, meta in items:
                btn = QPushButton(f"+ {meta.name}")
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2e2e38;
                        color: #ffffff;
                        border: 1px solid #404050;
                        border-radius: 5px;
                        padding: 6px;
                        text-align: left;
                    }
                    QPushButton:hover {
                        background-color: #3e3e4a;
                        border-color: #4ecdc4;
                    }
                    QPushButton:pressed {
                        background-color: #202028;
                    }
                """)
                # Capture current type_name in closure
                btn.clicked.connect(lambda checked=False, t=type_name: self.widget_spawn_requested.emit(t))
                cat_layout.addWidget(btn)

            cat_layout.addStretch()
            self.toolbox.addItem(cat_widget, cat_name)

        layout.addWidget(self.toolbox)
