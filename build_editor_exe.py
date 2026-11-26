"""
Build script to compile HomiCraft Editor into standalone Windows .exe applications
Builds both:
  1. Directory distribution: dist/HomiCraft/HomiCraft.exe (fastest launch)
  2. Single-file standalone: dist/HomiCraft_SingleFile.exe (one portable file)
"""

import os
import sys
import shutil
import subprocess

HOMI_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(HOMI_DIR, "dist")
BUILD_DIR = os.path.join(HOMI_DIR, "build_editor")


def build_editor():
    print("=" * 60)
    print("🚀 Building HomiCraft Editor Executables")
    print("=" * 60)

    ico_path = os.path.join(HOMI_DIR, "icon.ico")
    png_path = os.path.join(HOMI_DIR, "icon.png")
    entry_script = os.path.join(HOMI_DIR, "homi_editor.py")

    hidden_imports = [
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtGui",
        "--hidden-import=PySide6.QtWidgets",
        "--hidden-import=core.paths",
        "--hidden-import=core.schema",
        "--hidden-import=core.registry",
        "--hidden-import=core.proxy",
        "--hidden-import=core.runtime",
        "--hidden-import=core.exporter",
        "--hidden-import=editor.canvas",
        "--hidden-import=editor.code_editor",
        "--hidden-import=editor.connect_dialog",
        "--hidden-import=editor.export_dialog",
        "--hidden-import=editor.filesystem",
        "--hidden-import=editor.hierarchy",
        "--hidden-import=editor.inspector",
        "--hidden-import=editor.main_window",
        "--hidden-import=editor.palette",
        "--hidden-import=editor.project_manager",
        "--hidden-import=editor.settings_dialog",
        "--hidden-import=editor.theme",
    ]

    add_data = [
        f"--add-data={os.path.join(HOMI_DIR, 'core')};core",
        f"--add-data={os.path.join(HOMI_DIR, 'editor')};editor",
        f"--add-data={os.path.join(HOMI_DIR, 'examples')};examples",
        f"--add-data={os.path.join(HOMI_DIR, 'runner.py')};.",
        f"--add-data={ico_path};.",
        f"--add-data={png_path};.",
    ]

    # --- 1. BUILD ONEDIR VERSION ---
    print("\n[1/2] Building Directory Version (dist/HomiCraft)...")
    cmd_onedir = [
        sys.executable, "-m", "PyInstaller",
        "--name", "HomiCraft",
        "--onedir",
        "--windowed",
        "--noconfirm",
        "--clean",
        f"--distpath={DIST_DIR}",
        f"--workpath={BUILD_DIR}",
        f"--specpath={BUILD_DIR}",
        f"--icon={ico_path}",
    ] + add_data + hidden_imports + [entry_script]

    result = subprocess.run(cmd_onedir, cwd=HOMI_DIR)
    if result.returncode != 0:
        print("❌ Onedir build failed with code:", result.returncode)
        sys.exit(result.returncode)

    out_folder = os.path.join(DIST_DIR, "HomiCraft")
    shutil.copytree(os.path.join(HOMI_DIR, "examples"), os.path.join(out_folder, "examples"), dirs_exist_ok=True)
    shutil.copy2(os.path.join(HOMI_DIR, "runner.py"), os.path.join(out_folder, "runner.py"))
    shutil.copy2(ico_path, os.path.join(out_folder, "icon.ico"))
    shutil.copy2(png_path, os.path.join(out_folder, "icon.png"))

    # --- 2. BUILD SINGLE-FILE STANDALONE VERSION ---
    print("\n[2/2] Building Single-File Standalone Version (dist/HomiCraft_SingleFile.exe)...")
    temp_work = os.path.join(os.environ.get("TEMP", "C:/Temp"), "homi_onefile_work")
    temp_spec = os.path.join(os.environ.get("TEMP", "C:/Temp"), "homi_onefile_spec")
    cmd_onefile = [
        sys.executable, "-m", "PyInstaller",
        "--name", "HomiCraft_SingleFile",
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--clean",
        f"--distpath={DIST_DIR}",
        f"--workpath={temp_work}",
        f"--specpath={temp_spec}",
        f"--icon={ico_path}",
    ] + add_data + hidden_imports + [entry_script]

    result2 = subprocess.run(cmd_onefile, cwd=HOMI_DIR)
    if result2.returncode != 0:
        print("❌ Onefile build failed with code:", result2.returncode)

    # Clean up intermediate build directories
    shutil.rmtree(BUILD_DIR, ignore_errors=True)
    shutil.rmtree(temp_work, ignore_errors=True)
    shutil.rmtree(temp_spec, ignore_errors=True)

    print("=" * 60)
    print("✅ All HomiCraft Executables successfully built!")
    print(f"📁 Directory Distribution: {os.path.join(DIST_DIR, 'HomiCraft', 'HomiCraft.exe')}")
    print(f"🎯 Single-File Executable: {os.path.join(DIST_DIR, 'HomiCraft_SingleFile.exe')}")
    print("=" * 60)


if __name__ == "__main__":
    build_editor()
