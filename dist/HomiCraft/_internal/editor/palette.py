"""
HomiCraft Widget Palette Dock
Displays available UI widgets grouped by category. Clicking a widget adds it
to the current scene. Styled with Catppuccin rounded theme.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QToolBox, QPushButton, QScrollArea, QFrame, QLabel
)
from PySide6.QtCore import Signal, Qt
from core.registry import WIDGET_REGISTRY


class WidgetPalette(QWidget):
    widget_spawn_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        header = QLabel("📦 Widget Palette")
        header.setStyleSheet("font-weight: bold; font-size: 13px; padding: 4px;")
        layout.addWidget(header)

        self.toolbox = QToolBox(self)

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
            cat_layout.setSpacing(6)

            for type_name, meta in items:
                btn = QPushButton(f"+ {meta.name}")
                btn.setStyleSheet("text-align: left; padding: 6px 12px; border-radius: 8px;")
                btn.clicked.connect(lambda checked=False, t=type_name: self.widget_spawn_requested.emit(t))
                cat_layout.addWidget(btn)

            cat_layout.addStretch()
            self.toolbox.addItem(cat_widget, cat_name)

        layout.addWidget(self.toolbox)
