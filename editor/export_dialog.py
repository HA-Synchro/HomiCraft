"""
HomiCraft Standalone Export Dialog
Provides a GUI dialog inside the editor to export the active project into a standalone .exe
"""

import os
import sys
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QFileDialog, QPlainTextEdit, QMessageBox,
    QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal

from core.exporter import build_standalone_exe


class ExportWorker(QThread):
    log_signal = Signal(str)
    finished_signal = Signal(bool)

    def __init__(self, project_dir: str, output_dir: str, app_name: str, noconsole: bool, icon_path: str):
        super().__init__()
        self.project_dir = project_dir
        self.output_dir = output_dir
        self.app_name = app_name
        self.noconsole = noconsole
        self.icon_path = icon_path

    def run(self):
        success = build_standalone_exe(
            project_dir=self.project_dir,
            output_dir=self.output_dir,
            app_name=self.app_name,
            noconsole=self.noconsole,
            icon_path=self.icon_path if self.icon_path else None,
            log_callback=self.log_signal.emit
        )
        self.finished_signal.emit(success)


class ExportDialog(QDialog):
    def __init__(self, project_dir: str, default_name: str, parent=None):
        super().__init__(parent)
        self.project_dir = project_dir
        self.setWindowTitle("Export Standalone Executable (.exe)")
        self.resize(650, 480)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e24;
                color: #e0e0e0;
            }
            QLabel { color: #cfd8dc; }
            QLineEdit {
                background-color: #2b2b36;
                color: white;
                border: 1px solid #455a64;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton {
                background-color: #37474f;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #455a64; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        header = QLabel("📦 Export Project to Standalone Windows .EXE")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4ecdc4; padding-bottom: 6px;")
        layout.addWidget(header)

        form = QFormLayout()
        form.setSpacing(8)

        # App Name
        self.inp_name = QLineEdit(default_name)
        form.addRow("Application Name:", self.inp_name)

        # Output Folder
        out_row = QHBoxLayout()
        default_out = os.path.join(self.project_dir, "dist")
        self.inp_out = QLineEdit(default_out)
        btn_browse_out = QPushButton("Browse...")
        btn_browse_out.clicked.connect(self._browse_out)
        out_row.addWidget(self.inp_out)
        out_row.addWidget(btn_browse_out)
        form.addRow("Output Folder:", out_row)

        # Icon file (optional)
        icon_row = QHBoxLayout()
        self.inp_icon = QLineEdit("")
        self.inp_icon.setPlaceholderText("(Optional) path to .ico file")
        btn_browse_icon = QPushButton("Browse...")
        btn_browse_icon.clicked.connect(self._browse_icon)
        icon_row.addWidget(self.inp_icon)
        icon_row.addWidget(btn_browse_icon)
        form.addRow("Application Icon:", icon_row)

        # No Console Toggle
        self.chk_noconsole = QCheckBox("Windowed Mode (Hide black command prompt window)")
        self.chk_noconsole.setChecked(True)
        form.addRow("", self.chk_noconsole)

        layout.addLayout(form)

        # Build Log Console
        layout.addWidget(QLabel("<b>Build Output Log:</b>"))
        self.log_console = QPlainTextEdit(self)
        self.log_console.setReadOnly(True)
        self.log_console.setStyleSheet("background-color: #121217; color: #a4b0be; font-family: Consolas; font-size: 11px;")
        layout.addWidget(self.log_console)

        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_export = QPushButton("🚀 Build Standalone Executable")
        self.btn_export.setStyleSheet("background-color: #2e7d32; color: white; padding: 8px 16px; font-size: 13px;")
        self.btn_export.clicked.connect(self._start_export)
        
        self.btn_open_folder = QPushButton("📂 Open Output Folder")
        self.btn_open_folder.setEnabled(False)
        self.btn_open_folder.clicked.connect(self._open_output_folder)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.close)

        btn_layout.addWidget(self.btn_export)
        btn_layout.addWidget(self.btn_open_folder)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

        self.worker: Optional[ExportWorker] = None

    def _browse_out(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Directory", self.inp_out.text())
        if folder:
            self.inp_out.setText(folder)

    def _browse_icon(self):
        fpath, _ = QFileDialog.getOpenFileName(self, "Select Icon File", "", "Icon Files (*.ico)")
        if fpath:
            self.inp_icon.setText(fpath)

    def _start_export(self):
        app_name = self.inp_name.text().strip() or "HomiCraftApp"
        out_dir = self.inp_out.text().strip()
        icon_path = self.inp_icon.text().strip()
        noconsole = self.chk_noconsole.isChecked()

        self.btn_export.setEnabled(False)
        self.log_console.clear()
        self.log_console.appendPlainText("[HomiCraft] Initializing PyInstaller build process...")

        self.worker = ExportWorker(self.project_dir, out_dir, app_name, noconsole, icon_path)
        self.worker.log_signal.connect(self.log_console.appendPlainText)
        self.worker.finished_signal.connect(self._on_export_finished)
        self.worker.start()

    def _on_export_finished(self, success: bool):
        self.btn_export.setEnabled(True)
        if success:
            self.btn_open_folder.setEnabled(True)
            QMessageBox.information(self, "Export Complete", "Standalone executable was successfully created!")
        else:
            QMessageBox.critical(self, "Export Failed", "PyInstaller encountered an error. Check the build log console.")

    def _open_output_folder(self):
        out_dir = self.inp_out.text().strip()
        if os.path.isdir(out_dir):
            os.startfile(out_dir)
