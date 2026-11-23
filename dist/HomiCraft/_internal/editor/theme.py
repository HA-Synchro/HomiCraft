"""
HomiCraft Catppuccin Theme Engine
Provides all 4 official Catppuccin palettes (Mocha, Macchiato, Frappé, Latte)
with modern rounded-corner UI styling inspired by catppuccin.com.
"""

from typing import Dict, Any


CATPPUCCIN_PALETTES: Dict[str, Dict[str, str]] = {
    "Mocha": {
        "rosewater": "#f5e0dc",
        "flamingo": "#f2cdcd",
        "pink": "#f5c2e7",
        "mauve": "#cba6f7",
        "red": "#f38ba8",
        "maroon": "#eba0ac",
        "peach": "#fab387",
        "yellow": "#f9e2af",
        "green": "#a6e3a1",
        "teal": "#94e2d5",
        "sky": "#89dceb",
        "sapphire": "#74c7ec",
        "blue": "#89b4fa",
        "lavender": "#b4befe",
        "text": "#cdd6f4",
        "subtext1": "#bac2de",
        "subtext0": "#a6adc8",
        "overlay2": "#9399b2",
        "overlay1": "#7f849c",
        "overlay0": "#6c7086",
        "surface2": "#585b70",
        "surface1": "#45475a",
        "surface0": "#313244",
        "base": "#1e1e2e",
        "mantle": "#181825",
        "crust": "#11111b",
        "is_dark": "true"
    },
    "Macchiato": {
        "rosewater": "#f4dbd6",
        "flamingo": "#f0c6c6",
        "pink": "#f5bde6",
        "mauve": "#c6a0f6",
        "red": "#ed8796",
        "maroon": "#ee99a0",
        "peach": "#f5a97f",
        "yellow": "#eed49f",
        "green": "#a6da95",
        "teal": "#8bd5ca",
        "sky": "#91d7e3",
        "sapphire": "#7dc4e4",
        "blue": "#8aadf4",
        "lavender": "#b7bdf8",
        "text": "#cad3f5",
        "subtext1": "#b8c0e0",
        "subtext0": "#a5adcb",
        "overlay2": "#939ab7",
        "overlay1": "#8087a2",
        "overlay0": "#6e738d",
        "surface2": "#5b6078",
        "surface1": "#494d64",
        "surface0": "#363a4f",
        "base": "#24273a",
        "mantle": "#1e2030",
        "crust": "#181926",
        "is_dark": "true"
    },
    "Frappé": {
        "rosewater": "#f2d5cf",
        "flamingo": "#eebebe",
        "pink": "#f4b8e4",
        "mauve": "#ca9ee6",
        "red": "#e78284",
        "maroon": "#ea999c",
        "peach": "#ef9f76",
        "yellow": "#e5c890",
        "green": "#a6d189",
        "teal": "#81c8be",
        "sky": "#99d1db",
        "sapphire": "#85c1dc",
        "blue": "#8caaee",
        "lavender": "#babbf1",
        "text": "#c6d0f5",
        "subtext1": "#b5bfe2",
        "subtext0": "#a5adce",
        "overlay2": "#949cbb",
        "overlay1": "#838ba7",
        "overlay0": "#737994",
        "surface2": "#626880",
        "surface1": "#51576d",
        "surface0": "#414559",
        "base": "#303446",
        "mantle": "#292c3c",
        "crust": "#232634",
        "is_dark": "true"
    },
    "Latte": {
        "rosewater": "#dc8a78",
        "flamingo": "#dd7878",
        "pink": "#ea76cb",
        "mauve": "#8839ef",
        "red": "#d20f39",
        "maroon": "#e64553",
        "peach": "#fe640b",
        "yellow": "#df8e1d",
        "green": "#40a02b",
        "teal": "#179299",
        "sky": "#04a5e5",
        "sapphire": "#209fb5",
        "blue": "#1e66f5",
        "lavender": "#7287fd",
        "text": "#4c4f69",
        "subtext1": "#5c5f77",
        "subtext0": "#6c6f85",
        "overlay2": "#7c7f93",
        "overlay1": "#8c8fa1",
        "overlay0": "#9ca0b0",
        "surface2": "#acb0be",
        "surface1": "#bcc0cc",
        "surface0": "#ccd0da",
        "base": "#eff1f5",
        "mantle": "#e6e9ef",
        "crust": "#dce0e8",
        "is_dark": "false"
    }
}


def build_catppuccin_stylesheet(flavor: str = "Mocha") -> str:
    """Builds a complete, modern rounded QSS stylesheet for the given Catppuccin flavor."""
    pal = CATPPUCCIN_PALETTES.get(flavor, CATPPUCCIN_PALETTES["Mocha"])

    return f"""
    /* --- Main Window & Core --- */
    QMainWindow {{
        background-color: {pal["crust"]};
        color: {pal["text"]};
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    }}
    QWidget {{
        color: {pal["text"]};
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        font-size: 12px;
    }}

    /* --- Toolbar --- */
    QToolBar {{
        background-color: {pal["mantle"]};
        border-bottom: 1px solid {pal["surface0"]};
        spacing: 8px;
        padding: 6px 10px;
    }}
    QToolBar::separator {{
        background: {pal["surface1"]};
        width: 1px;
        margin: 4px 6px;
    }}

    /* --- Rounded Buttons (Catppuccin style) --- */
    QPushButton {{
        background-color: {pal["surface0"]};
        color: {pal["text"]};
        border: 1px solid {pal["surface1"]};
        border-radius: 8px;
        padding: 6px 14px;
        font-weight: 600;
    }}
    QPushButton:hover {{
        background-color: {pal["surface1"]};
        border-color: {pal["mauve"]};
        color: {pal["mauve"]};
    }}
    QPushButton:pressed {{
        background-color: {pal["surface2"]};
    }}
    QPushButton:disabled {{
        background-color: {pal["mantle"]};
        color: {pal["overlay0"]};
        border-color: {pal["surface0"]};
    }}

    /* Accent Pill Buttons */
    QPushButton#btn_run {{
        background-color: {pal["green"]};
        color: {pal["crust"]};
        border: none;
        border-radius: 8px;
        font-weight: bold;
    }}
    QPushButton#btn_run:hover {{
        background-color: {pal["teal"]};
    }}
    QPushButton#btn_stop {{
        background-color: {pal["red"]};
        color: {pal["crust"]};
        border: none;
        border-radius: 8px;
        font-weight: bold;
    }}
    QPushButton#btn_export {{
        background-color: {pal["blue"]};
        color: {pal["crust"]};
        border: none;
        border-radius: 8px;
        font-weight: bold;
    }}
    QPushButton#btn_export:hover {{
        background-color: {pal["sapphire"]};
    }}

    /* --- Docks & Title Bars --- */
    QDockWidget {{
        background-color: {pal["mantle"]};
        color: {pal["text"]};
        font-weight: bold;
    }}
    QDockWidget::title {{
        background-color: {pal["surface0"]};
        color: {pal["lavender"]};
        padding: 8px 12px;
        border-radius: 8px;
        margin: 3px;
        font-weight: 600;
    }}
    QMainWindow::separator {{
        background: {pal["surface0"]};
        width: 5px;
        height: 5px;
        border-radius: 2px;
    }}
    QMainWindow::separator:hover {{
        background: {pal["mauve"]};
    }}

    /* --- Tabs (Pill style like Catppuccin web) --- */
    QTabWidget::pane {{
        border: 1px solid {pal["surface0"]};
        border-radius: 10px;
        background-color: {pal["base"]};
        padding: 4px;
    }}
    QTabBar::tab {{
        background: {pal["mantle"]};
        color: {pal["subtext0"]};
        padding: 8px 18px;
        margin-right: 4px;
        border-radius: 8px;
        font-weight: 600;
    }}
    QTabBar::tab:hover {{
        background: {pal["surface0"]};
        color: {pal["text"]};
    }}
    QTabBar::tab:selected {{
        background: {pal["surface1"]};
        color: {pal["mauve"]};
        border: 1px solid {pal["mauve"]};
    }}

    /* --- Trees & Lists (FileSystem & Hierarchy) --- */
    QTreeView, QTreeWidget {{
        background-color: {pal["base"]};
        color: {pal["text"]};
        border: 1px solid {pal["surface0"]};
        border-radius: 8px;
        padding: 4px;
        outline: none;
    }}
    QTreeView::item, QTreeWidget::item {{
        padding: 5px 8px;
        border-radius: 6px;
    }}
    QTreeView::item:hover, QTreeWidget::item:hover {{
        background-color: {pal["surface0"]};
    }}
    QTreeView::item:selected, QTreeWidget::item:selected {{
        background-color: {pal["surface1"]};
        color: {pal["mauve"]};
        font-weight: bold;
    }}
    QHeaderView::section {{
        background-color: {pal["mantle"]};
        color: {pal["subtext1"]};
        padding: 6px;
        border: none;
        border-radius: 4px;
        font-weight: bold;
    }}

    /* --- Inputs & Spinners --- */
    QLineEdit, QSpinBox, QComboBox {{
        background-color: {pal["surface0"]};
        color: {pal["text"]};
        border: 1px solid {pal["surface1"]};
        border-radius: 8px;
        padding: 6px 10px;
        font-family: Consolas, monospace;
    }}
    QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
        border: 2px solid {pal["mauve"]};
        background-color: {pal["surface1"]};
    }}
    QComboBox::drop-down {{
        border: none;
        background-color: {pal["surface1"]};
        width: 24px;
        border-top-right-radius: 8px;
        border-bottom-right-radius: 8px;
    }}

    /* --- Scrollbars --- */
    QScrollBar:vertical {{
        background: {pal["mantle"]};
        width: 10px;
        border-radius: 5px;
        margin: 2px;
    }}
    QScrollBar::handle:vertical {{
        background: {pal["surface1"]};
        min-height: 24px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {pal["mauve"]};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        background: {pal["mantle"]};
        height: 10px;
        border-radius: 5px;
        margin: 2px;
    }}
    QScrollBar::handle:horizontal {{
        background: {pal["surface1"]};
        min-width: 24px;
        border-radius: 5px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {pal["mauve"]};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}

    /* --- Menus & Floating Cards --- */
    QMenu {{
        background-color: {pal["mantle"]};
        color: {pal["text"]};
        border: 1px solid {pal["surface1"]};
        border-radius: 10px;
        padding: 6px;
    }}
    QMenu::item {{
        padding: 6px 22px;
        border-radius: 6px;
    }}
    QMenu::item:selected {{
        background-color: {pal["surface0"]};
        color: {pal["mauve"]};
        font-weight: bold;
    }}
    QMenu::separator {{
        height: 1px;
        background: {pal["surface0"]};
        margin: 4px 6px;
    }}

    /* --- Checkboxes & RadioButtons --- */
    QCheckBox, QRadioButton {{
        color: {pal["text"]};
        spacing: 8px;
        font-weight: 500;
    }}
    QCheckBox::indicator, QRadioButton::indicator {{
        width: 16px;
        height: 16px;
        border: 1px solid {pal["surface2"]};
        border-radius: 4px;
        background: {pal["surface0"]};
    }}
    QRadioButton::indicator {{
        border-radius: 8px;
    }}
    QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
        background: {pal["mauve"]};
        border-color: {pal["mauve"]};
    }}

    /* --- Output Console --- */
    QPlainTextEdit#console_output {{
        background-color: {pal["crust"]};
        color: {pal["subtext1"]};
        border: 1px solid {pal["surface0"]};
        border-radius: 8px;
        font-family: Consolas, monospace;
        font-size: 11px;
        padding: 6px;
    }}
    """
