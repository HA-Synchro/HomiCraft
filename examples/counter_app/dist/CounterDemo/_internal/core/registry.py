"""
HomiCraft Widget Registry
Maps abstract HomiCraft widget types to PySide6 widgets, their default properties,
and supported signals.
"""

from typing import Dict, Any, List, Type
from PySide6.QtWidgets import (
    QWidget, QPushButton, QLabel, QLineEdit, QTextEdit,
    QCheckBox, QSlider, QProgressBar, QFrame
)
from PySide6.QtCore import Qt


class WidgetMeta:
    def __init__(
        self,
        name: str,
        category: str,
        qt_class: Type[QWidget],
        default_size: tuple[int, int],
        default_props: Dict[str, Any],
        supported_signals: List[str]
    ):
        self.name = name
        self.category = category
        self.qt_class = qt_class
        self.default_size = default_size
        self.default_props = default_props
        self.supported_signals = supported_signals


WIDGET_REGISTRY: Dict[str, WidgetMeta] = {
    "Button": WidgetMeta(
        name="Button",
        category="Basic",
        qt_class=QPushButton,
        default_size=(120, 36),
        default_props={
            "text": "Button",
            "enabled": True,
            "styleSheet": ""
        },
        supported_signals=["clicked", "pressed", "released"]
    ),
    "Label": WidgetMeta(
        name="Label",
        category="Basic",
        qt_class=QLabel,
        default_size=(140, 30),
        default_props={
            "text": "Label Text",
            "styleSheet": "font-size: 14px;",
            "alignment": "left"
        },
        supported_signals=[]
    ),
    "LineEdit": WidgetMeta(
        name="LineEdit",
        category="Input",
        qt_class=QLineEdit,
        default_size=(180, 34),
        default_props={
            "text": "",
            "placeholder": "Enter text...",
            "readOnly": False,
            "styleSheet": ""
        },
        supported_signals=["textChanged", "returnPressed"]
    ),
    "TextEdit": WidgetMeta(
        name="TextEdit",
        category="Input",
        qt_class=QTextEdit,
        default_size=(240, 120),
        default_props={
            "plainText": "",
            "placeholder": "Enter long text...",
            "readOnly": False,
            "styleSheet": ""
        },
        supported_signals=["textChanged"]
    ),
    "CheckBox": WidgetMeta(
        name="CheckBox",
        category="Input",
        qt_class=QCheckBox,
        default_size=(120, 30),
        default_props={
            "text": "Check Option",
            "checked": False,
            "styleSheet": ""
        },
        supported_signals=["toggled"]
    ),
    "Slider": WidgetMeta(
        name="Slider",
        category="Input",
        qt_class=QSlider,
        default_size=(160, 24),
        default_props={
            "min": 0,
            "max": 100,
            "value": 50,
            "styleSheet": ""
        },
        supported_signals=["valueChanged"]
    ),
    "ProgressBar": WidgetMeta(
        name="ProgressBar",
        category="Display",
        qt_class=QProgressBar,
        default_size=(180, 24),
        default_props={
            "min": 0,
            "max": 100,
            "value": 0,
            "styleSheet": ""
        },
        supported_signals=["valueChanged"]
    ),
    "Panel": WidgetMeta(
        name="Panel",
        category="Containers",
        qt_class=QFrame,
        default_size=(250, 180),
        default_props={
            "styleSheet": "background-color: #2b2b2b; border-radius: 8px;"
        },
        supported_signals=[]
    )
}


def apply_widget_properties(widget: QWidget, props: Dict[str, Any]) -> None:
    """Applies property values from schema to a live PySide6 widget instance."""
    for key, val in props.items():
        if key == "text" and hasattr(widget, "setText"):
            widget.setText(str(val))
        elif key == "placeholder" and hasattr(widget, "setPlaceholderText"):
            widget.setPlaceholderText(str(val))
        elif key == "plainText" and hasattr(widget, "setPlainText"):
            widget.setPlainText(str(val))
        elif key == "enabled" and hasattr(widget, "setEnabled"):
            widget.setEnabled(bool(val))
        elif key == "checked" and hasattr(widget, "setChecked"):
            widget.setChecked(bool(val))
        elif key == "min" and hasattr(widget, "setMinimum"):
            widget.setMinimum(int(val))
        elif key == "max" and hasattr(widget, "setMaximum"):
            widget.setMaximum(int(val))
        elif key == "value" and hasattr(widget, "setValue"):
            widget.setValue(int(val))
        elif key == "readOnly" and hasattr(widget, "setReadOnly"):
            widget.setReadOnly(bool(val))
        elif key == "alignment" and hasattr(widget, "setAlignment"):
            if val == "center":
                widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            elif val == "right":
                widget.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            else:
                widget.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        elif key == "styleSheet" and hasattr(widget, "setStyleSheet"):
            if val:
                widget.setStyleSheet(str(val))
