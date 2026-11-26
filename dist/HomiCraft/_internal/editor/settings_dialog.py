"""
HomiCraft Settings Window
Allows configuring UI text/display scale (100%, 200%, etc.), Catppuccin themes,
code editor font, canvas grid snapping, layout persistence, and export options.
"""

from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QSlider, QSpinBox, QComboBox, QCheckBox, QRadioButton,
    QPushButton, QGroupBox, QFormLayout, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QSettings
from PySide6.QtGui import QFont


DEFAULT_SETTINGS: Dict[str, Any] = {
    "ui_scale": 100,
    "theme_flavor": "Mocha",
    "editor_font_family": "Consolas",
    "editor_font_size": 11,
    "grid_snap_enabled": True,
    "grid_snap_size": 10,
    "remember_layout": True,
    "auto_save_on_run": True,
    "default_export_mode": "windowed",
    "default_export_folder": "dist"
}


def load_editor_settings() -> Dict[str, Any]:
    """Loads all editor settings from persistent QSettings (IniFormat in AppData)."""
    settings = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, "HomiCraft", "Settings")
    result = dict(DEFAULT_SETTINGS)

    result["ui_scale"] = int(settings.value("ui_scale", DEFAULT_SETTINGS["ui_scale"]))
    result["theme_flavor"] = str(settings.value("theme_flavor", DEFAULT_SETTINGS["theme_flavor"]))
    result["editor_font_family"] = str(settings.value("editor_font_family", DEFAULT_SETTINGS["editor_font_family"]))
    result["editor_font_size"] = int(settings.value("editor_font_size", DEFAULT_SETTINGS["editor_font_size"]))

    val_snap = settings.value("grid_snap_enabled", DEFAULT_SETTINGS["grid_snap_enabled"])
    result["grid_snap_enabled"] = val_snap if isinstance(val_snap, bool) else (str(val_snap).lower() in ("true", "1"))

    result["grid_snap_size"] = int(settings.value("grid_snap_size", DEFAULT_SETTINGS["grid_snap_size"]))

    val_layout = settings.value("remember_layout", DEFAULT_SETTINGS["remember_layout"])
    result["remember_layout"] = val_layout if isinstance(val_layout, bool) else (str(val_layout).lower() in ("true", "1"))

    val_save = settings.value("auto_save_on_run", DEFAULT_SETTINGS["auto_save_on_run"])
    result["auto_save_on_run"] = val_save if isinstance(val_save, bool) else (str(val_save).lower() in ("true", "1"))

    result["default_export_mode"] = str(settings.value("default_export_mode", DEFAULT_SETTINGS["default_export_mode"]))
    result["default_export_folder"] = str(settings.value("default_export_folder", DEFAULT_SETTINGS["default_export_folder"]))

    return result


def save_editor_settings(cfg: Dict[str, Any]) -> None:
    """Saves all editor settings into persistent QSettings (IniFormat in AppData)."""
    settings = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, "HomiCraft", "Settings")
    for k, v in cfg.items():
        settings.setValue(k, v)
    settings.sync()


class HomiCraftSettingsDialog(QDialog):
    """
    Dedicated Preferences & Settings Window for HomiCraft.
    Supports scaling UI texts and controls (50% to 250%), themes, fonts, and grid options.
    """
    settings_applied = Signal(dict)
    reset_layout_requested = Signal()

    def __init__(self, parent=None, current_settings: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ HomiCraft — Editor Settings")
        self.resize(620, 520)
        self.setModal(True)

        self.initial_settings = current_settings or load_editor_settings()
        self.current_settings = dict(self.initial_settings)

        self._init_ui()
        self._load_values(self.current_settings)

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)

        # Tab Widget
        self.tabs = QTabWidget(self)
        main_layout.addWidget(self.tabs)

        # Tab 1: Display & UI Scaling
        self.tab_display = QWidget()
        self._build_display_tab(self.tab_display)
        self.tabs.addTab(self.tab_display, "🖥️ Display & Scaling")

        # Tab 2: Canvas & Grid Snapping
        self.tab_canvas = QWidget()
        self._build_canvas_tab(self.tab_canvas)
        self.tabs.addTab(self.tab_canvas, "📐 Canvas & Grid")

        # Tab 3: Workspace & Layout
        self.tab_workspace = QWidget()
        self._build_workspace_tab(self.tab_workspace)
        self.tabs.addTab(self.tab_workspace, "🗂️ Workspace & Layout")

        # Tab 4: Build & Export
        self.tab_export = QWidget()
        self._build_export_tab(self.tab_export)
        self.tabs.addTab(self.tab_export, "📦 Build & Export")

        # Bottom Button Bar
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(10)

        self.btn_defaults = QPushButton("↺ Restore Defaults")
        self.btn_defaults.clicked.connect(self._on_restore_defaults_clicked)
        btn_bar.addWidget(self.btn_defaults)

        btn_bar.addStretch()

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self._on_cancel_clicked)
        btn_bar.addWidget(self.btn_cancel)

        self.btn_apply = QPushButton("Apply")
        self.btn_apply.clicked.connect(self._on_apply_clicked)
        btn_bar.addWidget(self.btn_apply)

        self.btn_save = QPushButton("Save & Close")
        self.btn_save.setDefault(True)
        self.btn_save.setObjectName("btn_run")  # Accent green pill styling
        self.btn_save.clicked.connect(self._on_save_clicked)
        btn_bar.addWidget(self.btn_save)

        main_layout.addLayout(btn_bar)

    # --- TAB 1: DISPLAY & SCALING ---
    def _build_display_tab(self, parent: QWidget) -> None:
        layout = QVBoxLayout(parent)
        layout.setSpacing(14)

        # Group 1: UI Scale Factor
        grp_scale = QGroupBox("🔍 Display & Text Scale (Windows Scale Equivalent)")
        grp_scale_layout = QVBoxLayout(grp_scale)

        lbl_desc = QLabel("Adjusts the scale of all editor texts, buttons, docks, tabs, and controls:")
        lbl_desc.setStyleSheet("color: #a6adc8; font-size: 11px;")
        grp_scale_layout.addWidget(lbl_desc)

        slider_row = QHBoxLayout()
        self.slider_scale = QSlider(Qt.Orientation.Horizontal)
        self.slider_scale.setRange(50, 250)
        self.slider_scale.setSingleStep(5)
        self.slider_scale.setTickInterval(25)
        self.slider_scale.setTickPosition(QSlider.TickPosition.TicksBelow)

        self.spin_scale = QSpinBox()
        self.spin_scale.setRange(50, 250)
        self.spin_scale.setSuffix("%")
        self.spin_scale.setSingleStep(5)
        self.spin_scale.setFixedWidth(80)

        # Synchronize slider & spinbox
        self.slider_scale.valueChanged.connect(self.spin_scale.setValue)
        self.spin_scale.valueChanged.connect(self.slider_scale.setValue)
        self.slider_scale.valueChanged.connect(self._on_scale_slider_changed)

        slider_row.addWidget(self.slider_scale)
        slider_row.addWidget(self.spin_scale)
        grp_scale_layout.addLayout(slider_row)

        # Preset buttons
        preset_row = QHBoxLayout()
        preset_row.setSpacing(6)
        presets = [75, 100, 125, 150, 175, 200]
        for p in presets:
            btn = QPushButton(f"{p}%")
            btn.setFixedWidth(60)
            btn.clicked.connect(lambda checked=False, val=p: self.spin_scale.setValue(val))
            preset_row.addWidget(btn)
        preset_row.addStretch()
        grp_scale_layout.addLayout(preset_row)

        # Live scale preview box
        self.lbl_preview = QLabel("The quick brown fox jumps over the lazy dog (100% Preview)")
        self.lbl_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_preview.setStyleSheet("background-color: #181825; border: 1px dashed #585b70; border-radius: 6px; padding: 10px;")
        grp_scale_layout.addWidget(self.lbl_preview)

        layout.addWidget(grp_scale)

        # Group 2: Theme Flavor
        grp_theme = QGroupBox("🎨 Color Palette & Appearance")
        theme_form = QFormLayout(grp_theme)

        self.combo_theme = QComboBox()
        self.combo_theme.addItems([
            "🌿 Mocha (Deep Dark)",
            "☕ Macchiato (Medium Dark)",
            "🍨 Frappé (Soft Pastel)",
            "🥛 Latte (Crisp Light)"
        ])
        theme_form.addRow("Theme Flavor:", self.combo_theme)

        # Code Editor Font
        self.combo_font_family = QComboBox()
        self.combo_font_family.addItems([
            "Consolas",
            "Cascadia Code",
            "JetBrains Mono",
            "Fira Code",
            "Courier New",
            "Segoe UI"
        ])
        theme_form.addRow("Code Editor Font:", self.combo_font_family)

        self.spin_font_size = QSpinBox()
        self.spin_font_size.setRange(8, 28)
        self.spin_font_size.setSuffix(" pt")
        self.spin_font_size.setFixedWidth(80)
        theme_form.addRow("Code Font Size:", self.spin_font_size)

        layout.addWidget(grp_theme)
        layout.addStretch()

    # --- TAB 2: CANVAS & GRID ---
    def _build_canvas_tab(self, parent: QWidget) -> None:
        layout = QVBoxLayout(parent)
        layout.setSpacing(14)

        grp_grid = QGroupBox("📐 Visual Canvas Alignment & Snapping")
        form = QFormLayout(grp_grid)

        self.chk_grid_snap = QCheckBox("Enable Grid Snapping by Default")
        form.addRow(self.chk_grid_snap)

        self.spin_grid_size = QSpinBox()
        self.spin_grid_size.setRange(2, 64)
        self.spin_grid_size.setSuffix(" px")
        self.spin_grid_size.setFixedWidth(90)
        form.addRow("Grid Step Size:", self.spin_grid_size)

        # Quick presets
        preset_row = QHBoxLayout()
        for sz in [5, 10, 16, 20]:
            btn = QPushButton(f"{sz}px")
            btn.setFixedWidth(55)
            btn.clicked.connect(lambda checked=False, val=sz: self.spin_grid_size.setValue(val))
            preset_row.addWidget(btn)
        preset_row.addStretch()
        form.addRow("Grid Presets:", preset_row)

        layout.addWidget(grp_grid)
        layout.addStretch()

    # --- TAB 3: WORKSPACE & LAYOUT ---
    def _build_workspace_tab(self, parent: QWidget) -> None:
        layout = QVBoxLayout(parent)
        layout.setSpacing(14)

        grp_layout = QGroupBox("💾 Session & Layout Memory")
        vbox = QVBoxLayout(grp_layout)

        self.chk_remember_layout = QCheckBox("Remember Dock Layout & Window Geometry on Exit")
        vbox.addWidget(self.chk_remember_layout)

        lbl_info = QLabel("When enabled, dock positions, tabs, floating windows, and sizes are restored when reopening.")
        lbl_info.setStyleSheet("color: #a6adc8; font-size: 11px;")
        vbox.addWidget(lbl_info)

        self.chk_auto_save = QCheckBox("Auto-Save Project Before Running (F5)")
        vbox.addWidget(self.chk_auto_save)

        vbox.addSpacing(10)

        # Reset button
        btn_reset_dock = QPushButton("📐 Reset Dock Layout to Default Now")
        btn_reset_dock.clicked.connect(self._on_reset_layout_clicked)
        vbox.addWidget(btn_reset_dock)

        btn_clear_layout = QPushButton("🗑️ Clear Saved Layout Cache")
        btn_clear_layout.clicked.connect(self._on_clear_layout_cache_clicked)
        vbox.addWidget(btn_clear_layout)

        layout.addWidget(grp_layout)
        layout.addStretch()

    # --- TAB 4: BUILD & EXPORT ---
    def _build_export_tab(self, parent: QWidget) -> None:
        layout = QVBoxLayout(parent)
        layout.setSpacing(14)

        grp_export = QGroupBox("📦 Standalone Executable Packaging Defaults")
        form = QFormLayout(grp_export)

        self.rad_windowed = QRadioButton("Windowed Mode (GUI Only - No Console)")
        self.rad_console = QRadioButton("Console Mode (Debug Console Output Visible)")
        form.addRow("Default Executable Mode:", self.rad_windowed)
        form.addRow("", self.rad_console)

        self.edit_export_folder = QLineEdit()
        form.addRow("Default Output Subfolder:", self.edit_export_folder)

        layout.addWidget(grp_export)
        layout.addStretch()

    # --- LOGIC & HELPERS ---
    def _load_values(self, cfg: Dict[str, Any]) -> None:
        scale = int(cfg.get("ui_scale", 100))
        self.slider_scale.setValue(scale)
        self.spin_scale.setValue(scale)
        self._update_preview(scale)

        flavor = cfg.get("theme_flavor", "Mocha")
        flavor_map = {"Mocha": 0, "Macchiato": 1, "Frappé": 2, "Latte": 3}
        self.combo_theme.setCurrentIndex(flavor_map.get(flavor, 0))

        font_fam = cfg.get("editor_font_family", "Consolas")
        idx = self.combo_font_family.findText(font_fam)
        if idx >= 0:
            self.combo_font_family.setCurrentIndex(idx)

        self.spin_font_size.setValue(int(cfg.get("editor_font_size", 11)))

        self.chk_grid_snap.setChecked(bool(cfg.get("grid_snap_enabled", True)))
        self.spin_grid_size.setValue(int(cfg.get("grid_snap_size", 10)))

        self.chk_remember_layout.setChecked(bool(cfg.get("remember_layout", True)))
        self.chk_auto_save.setChecked(bool(cfg.get("auto_save_on_run", True)))

        mode = cfg.get("default_export_mode", "windowed")
        if mode == "console":
            self.rad_console.setChecked(True)
        else:
            self.rad_windowed.setChecked(True)

        self.edit_export_folder.setText(str(cfg.get("default_export_folder", "dist")))

    def _collect_values(self) -> Dict[str, Any]:
        flavors = ["Mocha", "Macchiato", "Frappé", "Latte"]
        chosen_flavor = flavors[self.combo_theme.currentIndex()]

        return {
            "ui_scale": self.spin_scale.value(),
            "theme_flavor": chosen_flavor,
            "editor_font_family": self.combo_font_family.currentText(),
            "editor_font_size": self.spin_font_size.value(),
            "grid_snap_enabled": self.chk_grid_snap.isChecked(),
            "grid_snap_size": self.spin_grid_size.value(),
            "remember_layout": self.chk_remember_layout.isChecked(),
            "auto_save_on_run": self.chk_auto_save.isChecked(),
            "default_export_mode": "console" if self.rad_console.isChecked() else "windowed",
            "default_export_folder": self.edit_export_folder.text().strip() or "dist"
        }

    def _on_scale_slider_changed(self, value: int) -> None:
        self._update_preview(value)

    def _update_preview(self, scale_percent: int) -> None:
        font_size = max(8, round(12 * (scale_percent / 100.0)))
        self.lbl_preview.setText(f"Sample UI Text ({scale_percent}% Scale)")
        self.lbl_preview.setFont(QFont("Segoe UI", font_size))

    def _on_apply_clicked(self) -> None:
        self.current_settings = self._collect_values()
        save_editor_settings(self.current_settings)
        self.settings_applied.emit(self.current_settings)

    def _on_save_clicked(self) -> None:
        self._on_apply_clicked()
        self.accept()

    def _on_cancel_clicked(self) -> None:
        # Revert to initial settings if applied previously
        if self.current_settings != self.initial_settings:
            save_editor_settings(self.initial_settings)
            self.settings_applied.emit(self.initial_settings)
        self.reject()

    def _on_restore_defaults_clicked(self) -> None:
        reply = QMessageBox.question(
            self,
            "Restore Defaults",
            "Are you sure you want to restore all settings to default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._load_values(DEFAULT_SETTINGS)
            self._on_apply_clicked()

    def _on_reset_layout_clicked(self) -> None:
        self.reset_layout_requested.emit()
        QMessageBox.information(self, "Layout Reset", "Dock layout has been restored to default!")

    def _on_clear_layout_cache_clicked(self) -> None:
        settings = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, "HomiCraft", "Layout")
        settings.clear()
        settings.sync()
        QMessageBox.information(self, "Layout Cleared", "Saved layout cache cleared from AppData.")
