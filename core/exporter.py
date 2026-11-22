"""
HomiCraft Standalone Executable Exporter
Packages HomiCraft projects into standalone Windows .exe applications
using PyInstaller.
"""

import os
import sys
import shutil
import subprocess
from typing import Optional, Callable


def generate_bootstrap_launcher(project_dir: str, output_script_path: str) -> None:
    """Creates a self-contained bootstrap Python script that runs the bundled project."""
    bootstrap_code = f'''"""
Auto-generated HomiCraft Standalone Launcher
"""
import os
import sys
from PySide6.QtWidgets import QApplication

# Get bundle directory (handles PyInstaller _MEIPASS extraction)
if getattr(sys, "frozen", False):
    BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Add core engine to path
sys.path.insert(0, BASE_DIR)

from core.runtime import HomiRuntimeWindow

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Project files are bundled inside BASE_DIR
    window = HomiRuntimeWindow(BASE_DIR)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
'''
    with open(output_script_path, "w", encoding="utf-8") as f:
        f.write(bootstrap_code)


def build_standalone_exe(
    project_dir: str,
    output_dir: str,
    app_name: str = "HomiCraftApp",
    noconsole: bool = True,
    icon_path: Optional[str] = None,
    log_callback: Optional[Callable[[str], None]] = None
) -> bool:
    """Compiles the project into an executable in output_dir."""
    project_dir = os.path.abspath(project_dir)
    output_dir = os.path.abspath(output_dir)
    homi_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    build_temp = os.path.join(output_dir, "build_temp")
    dist_temp = os.path.join(output_dir, "dist_temp")
    os.makedirs(build_temp, exist_ok=True)
    os.makedirs(dist_temp, exist_ok=True)

    if log_callback:
        log_callback(f"Preparing build environment in {build_temp}...")

    # 1. Create launcher bootstrap
    launcher_py = os.path.join(build_temp, "launcher.py")
    generate_bootstrap_launcher(project_dir, launcher_py)

    # 2. Copy core engine into build_temp
    shutil.copytree(os.path.join(homi_root, "core"), os.path.join(build_temp, "core"), dirs_exist_ok=True)

    # 3. Copy project files into build_temp
    for fname in os.listdir(project_dir):
        src = os.path.join(project_dir, fname)
        dst = os.path.join(build_temp, fname)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
        elif os.path.isdir(src) and fname not in ("__pycache__", "build", "dist"):
            shutil.copytree(src, dst, dirs_exist_ok=True)

    # 4. Construct PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", app_name,
        "--onedir",
        "--clean",
        "--distpath", output_dir,
        "--workpath", os.path.join(output_dir, "temp_work"),
        "--specpath", build_temp,
    ]

    if noconsole:
        cmd.append("--noconsole")

    if icon_path and os.path.isfile(icon_path):
        cmd.extend(["--icon", icon_path])

    # Add core package and project files to bundle
    # Windows PyInstaller data separator is ';'
    cmd.extend([
        "--add-data", f"{os.path.join(build_temp, 'core')};core",
        "--add-data", f"{os.path.join(build_temp, 'project.json')};.",
        "--add-data", f"{os.path.join(build_temp, 'main.ui.json')};.",
        "--add-data", f"{os.path.join(build_temp, 'main.py')};."
    ])

    cmd.append(launcher_py)

    if log_callback:
        log_callback(f"Running PyInstaller for {app_name}...")

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        for line in proc.stdout:
            if log_callback and line.strip():
                log_callback(line.strip())

        proc.wait()

        # Clean temporary build files
        shutil.rmtree(build_temp, ignore_errors=True)
        shutil.rmtree(os.path.join(output_dir, "temp_work"), ignore_errors=True)

        if proc.returncode == 0:
            if log_callback:
                exe_path = os.path.join(output_dir, app_name, f"{app_name}.exe")
                log_callback(f"BUILD SUCCESS! Executable created at: {exe_path}")
            return True
        else:
            if log_callback:
                log_callback(f"PyInstaller failed with return code {proc.returncode}")
            return False

    except Exception as e:
        if log_callback:
            log_callback(f"Export Error: {e}")
        return False
