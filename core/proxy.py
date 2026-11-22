"""
HomiCraft Widget Proxy
Wraps PySide6 QWidgets into intuitive Pythonic objects with direct property access.
Developers can write:
    button.text = "Click Me"
    print(button.text)
    slider.value = 80
    label.visible = False
    button.enabled = True
Instead of having to call raw Qt C++ style methods.
"""

from typing import Any
from PySide6.QtWidgets import QWidget


class HomiWidgetProxy:
    """
    Pythonic object wrapper around a live PySide6 QWidget.
    Supports direct attribute getters and setters for text, value, enabled,
    visible, checked, geometry, and styling.
    """

    def __init__(self, qt_widget: QWidget, widget_id: str = ""):
        super().__setattr__("_widget", qt_widget)
        super().__setattr__("_id", widget_id)

    @property
    def raw_widget(self) -> QWidget:
        """Returns the underlying PySide6 QWidget instance."""
        return self._widget

    def __repr__(self) -> str:
        w = self._widget
        extra = ""
        if hasattr(w, "text"):
            extra = f" text='{w.text()}'"
        elif hasattr(w, "value"):
            extra = f" value={w.value()}"
        return f"<HomiWidget id='{self._id}' type='{w.__class__.__name__}'{extra}>"

    def __getattr__(self, name: str) -> Any:
        w = self._widget

        # 1. Properties
        if name == "text":
            if hasattr(w, "text"):
                return w.text()
            elif hasattr(w, "toPlainText"):
                return w.toPlainText()
            return ""

        elif name == "placeholder":
            if hasattr(w, "placeholderText"):
                return w.placeholderText()
            return ""

        elif name == "value":
            if hasattr(w, "value"):
                return w.value()
            return 0

        elif name == "min":
            if hasattr(w, "minimum"):
                return w.minimum()
            return 0

        elif name == "max":
            if hasattr(w, "maximum"):
                return w.maximum()
            return 0

        elif name == "enabled":
            return w.isEnabled()

        elif name == "visible":
            return w.isVisible()

        elif name == "checked":
            if hasattr(w, "isChecked"):
                return w.isChecked()
            return False

        elif name == "x":
            return w.x()

        elif name == "y":
            return w.y()

        elif name == "width":
            return w.width()

        elif name == "height":
            return w.height()

        elif name in ("style", "styleSheet"):
            return w.styleSheet()

        # 2. Forward to underlying Qt Widget methods (click(), setFocus(), etc.)
        return getattr(w, name)

    def __setattr__(self, name: str, val: Any) -> None:
        if name in ("_widget", "_id"):
            super().__setattr__(name, val)
            return

        w = self._widget

        # 1. Text property
        if name == "text":
            text_str = str(val)
            if hasattr(w, "setText"):
                w.setText(text_str)
                return
            elif hasattr(w, "setPlainText"):
                w.setPlainText(text_str)
                return

        elif name == "placeholder":
            if hasattr(w, "setPlaceholderText"):
                w.setPlaceholderText(str(val))
                return

        elif name == "value":
            if hasattr(w, "setValue"):
                w.setValue(int(val))
                return

        elif name == "min":
            if hasattr(w, "setMinimum"):
                w.setMinimum(int(val))
                return

        elif name == "max":
            if hasattr(w, "setMaximum"):
                w.setMaximum(int(val))
                return

        elif name == "enabled":
            w.setEnabled(bool(val))
            return

        elif name == "visible":
            w.setVisible(bool(val))
            return

        elif name == "checked":
            if hasattr(w, "setChecked"):
                w.setChecked(bool(val))
                return

        elif name == "x":
            w.move(int(val), w.y())
            return

        elif name == "y":
            w.move(w.x(), int(val))
            return

        elif name == "width":
            w.resize(int(val), w.height())
            return

        elif name == "height":
            w.resize(w.width(), int(val))
            return

        elif name in ("style", "styleSheet"):
            w.setStyleSheet(str(val))
            return

        # Fallback to standard object assignment
        super().__setattr__(name, val)
