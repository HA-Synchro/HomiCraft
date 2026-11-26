# 📦 Chapter 6: Exporting Standalone Applications

HomiCraft includes a built-in, 1-click standalone application exporter powered by **PyInstaller**. With a single click, you can package your entire project into a native Windows executable (`.exe`) that runs on any modern Windows computer without requiring Python or external libraries to be installed.

---

## 🚀 1-Click Exporter Workflow

```
┌──────────────────────────────────────────────────────────────────┐
│ 📦 Export Standalone Executable (.EXE)                           │
├──────────────────────────────────────────────────────────────────┤
│ Configure standalone Windows executable settings:                │
│                                                                  │
│ Project Name:    [ Counter & Controls Demo                     ] │
│ Output Folder:   [ C:\Users\ocean\Documents\HomiCraftProjects... ]│
│                                                                  │
│ Executable Mode:                                                 │
│   (o) Windowed (GUI Application - No Console Window)             │
│   ( ) Console (Debug Mode - Shows Command Prompt)                │
│                                                                  │
│ Custom Icon:     [ res://icon.ico                            📂 ]│
│                                                                  │
│                                         [ Cancel ]  [ 📦 Export ]│
└──────────────────────────────────────────────────────────────────┘
```

### How to Export Your Project
1. Open your project in the HomiCraft editor.
2. In the top toolbar, click the **📦 Export .EXE** button.
3. In the exporter dialog, review your settings:
   * **Project Name**: The name of the final `.exe` (e.g. `Calculator.exe`).
   * **Output Folder**: Destination directory (defaults to `<project_dir>\dist`).
   * **Executable Mode**:
     * **Windowed (Recommended)**: Runs as a pure GUI application without showing an unsightly black command-prompt window.
     * **Console (Debug Mode)**: Keeps a terminal window open alongside your GUI. Ideal during development or beta testing so users can see `print()` logs and error tracebacks.
   * **Custom Icon**: Select any `.ico` file to set your application's Windows taskbar and desktop icon.
4. Click **📦 Export**.
5. HomiCraft invokes PyInstaller in the background. The Output Console streams compilation progress, and when finished, opens the target output folder in Windows File Explorer!

---

## 📂 What Gets Bundled?

The exporter automatically collects and packages:
1. **Application Engine**: The complete PySide6 runtime, Qt Qt6Core / Qt6Gui / Qt6Widgets libraries, and the Python runtime DLLs.
2. **Project Configurations**: `project.json` and all scene `.ui.json` files.
3. **Python Scripts**: `main.py` and any dedicated node scripts attached to widgets.
4. **Project Assets**: Any images, stylesheets, sounds, or custom data placed in your project directory.

---

## 🎁 Distributing to Users

### Standard Folder Distribution (`--onedir`)
By default, the exporter creates a folder inside `dist/`:
```
dist/
└── MyCoolApp/
    ├── MyCoolApp.exe       <-- The main executable the user double-clicks
    └── _internal/          <-- Required PySide6 DLLs, Python libraries, and assets
```

> [!IMPORTANT]
> When sharing your application with friends, clients, or players:
> 1. Zip the entire `MyCoolApp/` folder (or use an installer like Inno Setup).
> 2. Ensure users do **not** move `MyCoolApp.exe` out of its folder away from `_internal/`. The `.exe` relies on the files inside `_internal/` to run!

---

## 🛠️ Troubleshooting Export Issues

### 1. "Failed to load Python DLL" Error
* **Cause**: This error occurs when the `.exe` is moved or run from an incomplete folder (such as the temporary `build_editor` directory) where `_internal\python3xx.dll` is missing.
* **Fix**: Always run the final executable from the `dist\<AppName>\` folder, or ensure the entire folder is extracted before running.

### 2. Relative File Paths vs Saved Data
* When creating standalone applications, remember that single-file executables unpack temporary data to `%TEMP%\_MEIxxxxxx` which is deleted when the app closes.
* **Best Practice**: If your app saves persistent user files, configurations, or high scores, always save them to a permanent location such as:
  ```python
  import os
  from pathlib import Path

  # Save to user's Documents folder
  save_dir = Path.home() / "Documents" / "MyApp"
  save_dir.mkdir(parents=True, exist_ok=True)
  save_file = save_dir / "user_settings.json"
  ```

### 3. Missing External Python Packages
* If your scripts use third-party packages (such as `requests`, `numpy`, or `pillow`), ensure they are installed in your Python environment before running the exporter. PyInstaller will automatically detect and bundle them into the distribution!
