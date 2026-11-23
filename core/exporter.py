"""
HomiCraft Standalone Executable Exporter
Packages HomiCraft projects into standalone Windows .exe applications
using PyInstaller, ensuring all attached scripts, scenes, and assets are bundled.
"""

import os
import sys
import shutil
import subprocess
from typing import Optional, Callable
from core.paths import get_homi_root


def generate_bootstrap_launcher(project_dir: str, output_script_path: str) -> None:
    """Creates a self-contained bootstrap Python script that runs the bundled project."""
    bootstrap_code = f'''"""
Auto-generated HomiCraft Standalone Launcher
"""
import os
import sys
from PySide6.QtWidgets import QApplication

# Get bundle directory (handles PyInstaller _MEIPASS extraction in _internal)
if getattr(sys, "frozen", False):
    EXE_DIR = os.path.dirname(os.path.abspath(sys.executable))
    INTERNAL_DIR = getattr(sys, "_MEIPASS", EXE_DIR)
    BASE_DIR = INTERNAL_DIR
    sys.path.insert(0, INTERNAL_DIR)
    sys.path.insert(0, EXE_DIR)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
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
    homi_root = get_homi_root()

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

    # 3. Copy ALL project files into build_temp (including all attached .py scripts!)
    ignored_items = {"__pycache__", "build", "dist", "temp_work", "build_temp", ".git"}
    project_items = []
    for fname in os.listdir(project_dir):
        if fname in ignored_items or fname.startswith("."):
            continue
        src = os.path.join(project_dir, fname)
        dst = os.path.join(build_temp, fname)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
            project_items.append((fname, False))
        elif os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
            project_items.append((fname, True))

    if log_callback:
        log_callback(f"Bundling project files: {[item[0] for item in project_items]}")

    # 4. Construct PyInstaller command
    if getattr(sys, "frozen", False):
        py_tool = shutil.which("pyinstaller") or shutil.which("python") or sys.executable
        if py_tool.lower().endswith("pyinstaller.exe") or py_tool.lower().endswith("pyinstaller"):
            cmd = [py_tool]
        else:
            cmd = [py_tool, "-m", "PyInstaller"]
    else:
        cmd = [sys.executable, "-m", "PyInstaller"]

    cmd.extend([
        "--name", app_name,
        "--onedir",
        "--clean",
        "--noconfirm",
        "--distpath", output_dir,
        "--workpath", os.path.join(output_dir, "temp_work"),
        "--specpath", build_temp,
    ])

    if noconsole:
        cmd.append("--noconsole")

    if icon_path and os.path.isfile(icon_path):
        cmd.extend(["--icon", icon_path])

    # Add core package
    cmd.extend(["--add-data", f"{os.path.join(build_temp, 'core')};core"])

    # Add EVERY project file (.py scripts, .ui.json scenes, assets, config)
    for fname, is_dir in project_items:
        src_path = os.path.join(build_temp, fname)
        if is_dir:
            cmd.extend(["--add-data", f"{src_path};{fname}"])
        else:
            cmd.extend(["--add-data", f"{src_path};."])

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
            app_folder = os.path.join(output_dir, app_name)
            internal_folder = os.path.join(app_folder, "_internal")

            # Post-build safeguard: ensure all project files are directly copied into _internal and app_folder
            for fname, is_dir in project_items:
                src_file = os.path.join(project_dir, fname)
                # Copy to _internal if exists
                if os.path.isdir(internal_folder):
                    dst_internal = os.path.join(internal_folder, fname)
                    if is_dir:
                        shutil.copytree(src_file, dst_internal, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src_file, dst_internal)

                # Also copy next to the exe
                dst_root = os.path.join(app_folder, fname)
                if is_dir:
                    shutil.copytree(src_file, dst_root, dirs_exist_ok=True)
                else:
                    shutil.copy2(src_file, dst_root)

            exe_path = os.path.join(app_folder, f"{app_name}.exe")
            if log_callback:
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
