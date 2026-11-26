# ⚡ Chapter 1: Getting Started with HomiCraft

Welcome to **HomiCraft**, a modern visual software development engine for creating native desktop applications using **Python** and **PySide6 (Qt)**.

HomiCraft unifies visual canvas design and native desktop app development. If you know how to drag components onto a canvas, connect signals, and write clean Python scripts, you can build full-featured, professional Windows desktop applications in minutes.

---

## 🎯 Core Philosophy & Why HomiCraft?

Traditional GUI programming in Python often involves writing hundreds of lines of boilerplate code to create windows, position buttons, set margins, connect callbacks, and configure themes. Alternatively, tools like Qt Designer generate rigid XML files that require complex compilation steps (`pyside6-uic`) and awkward subclassing.

**HomiCraft reimagines desktop app creation with a modern visual philosophy:**
1. **Visual Canvas First**: Drag, resize, nudge, and snap widgets visually on a grid.
2. **Human-Readable Scenes**: Layouts are saved as clean `.ui.json` files that you can easily read, version control, or edit.
3. **Pure Python Scripting**: Write simple, readable Python scripts. No convoluted signal classes or complex metaclasses.
4. **Pythonic Property Access**: Modify widgets with intuitive dot notation (`btn.text = "Hello"`, `slider.value = 80`) instead of calling raw C++ style getters/setters (`btn.setText(...)`).
5. **Direct Node Injection**: Access any node in your scene either via `app.<node_id>` or directly by `<node_id>` in your script scope!
6. **1-Click Standalone Exporter**: Bundle your application into a standalone Windows `.exe` ready for distribution with a single click.

---

## 💻 System Requirements

* **Operating System**: Windows 10 or Windows 11 (64-bit).
* **Python Version**: Python 3.10 to 3.14 (only required if running from source; not needed if using the standalone pre-compiled executable).
* **Core Dependencies** (for source mode):
  * `PySide6 >= 6.5.0`
  * `PyInstaller >= 6.0.0` (for building executables)

---

## 🚀 Launching HomiCraft

There are two ways to launch HomiCraft:

### Method A: Standalone Executable (Recommended for End Users)
If you downloaded or built the standalone version, no Python installation or command-line setup is needed:
1. Navigate to `dist\HomiCraft\`.
2. Double-click **`HomiCraft.exe`**.
3. The **Project Manager** hub will appear instantly!

> [!NOTE]
> If you are using the single-file portable release (`HomiCraft_Portable_SingleFile.exe`), you can double-click it directly from anywhere on your drive.

### Method B: Launching from Source (For Developers)
To run the editor directly from source:
```powershell
python homi_editor.py
```

To open the editor directly into a specific project folder:
```powershell
python homi_editor.py examples/counter_app
```

To run a project standalone without opening the editor:
```powershell
python runner.py examples/counter_app
```

---

## 🏢 The Project Manager Hub

When you launch HomiCraft without specifying a project path, you are greeted by the **Project Manager** hub. This screen acts as your command center to create, manage, and run projects.

```
┌────────────────────────────────────────────────────────────────────────┐
│ ⚡ HomiCraft Engine                        🎨 Theme: [ Mocha (Dark) ▼ ]│
│ Select a project to edit, run, or create a new one.                    │
│ 🔍 [ Filter Projects...                                            ]   │
├─────────────────────────────────────────────────┬──────────────────────┤
│ ⚡ Counter & Controls Demo  v1.0.0              │ ✏️ Edit Project       │
│    C:\Users\ocean\Documents\HomiCraftProjects...│ ▶ Run Standalone     │
│                                                 │ ──────────────────── │
│                                                 │ ➕ New Project...     │
│                                                 │ 📂 Import / Scan...  │
│                                                 │ 📝 Rename Project... │
│                                                 │ 🔍 Show in Explorer  │
│                                                 │ ──────────────────── │
│                                                 │ 🗑️ Remove from List  │
│                                                 │ 💥 Delete Files...   │
└─────────────────────────────────────────────────┴──────────────────────┘
```

### Key Actions in the Project Manager

* **✏️ Edit Project**: Opens the selected project in the full HomiCraft visual editor. You can also simply double-click any project card in the list.
* **▶ Run Standalone**: Launches the project immediately in a dedicated runtime player without opening the editor interface. Great for quick testing or showing demos.
* **➕ New Project...**: Opens the New Project Wizard (see below).
* **📂 Import / Scan...**: Scans an existing folder for a `project.json` file and adds it to your project list.
* **📝 Rename Project...**: Renames the project. This updates both the project title and the `project.json` file safely on disk.
* **🔍 Show in Explorer**: Opens the selected project's folder directly in Windows File Explorer.
* **🗑️ Remove from List**: Removes the project from your recent projects list without touching the files on disk.
* **💥 Delete Project Files...**: Permanently deletes the project files and directory from your storage (requires explicit confirmation).
* **🎨 Theme Selector**: Choose between **Mocha**, **Macchiato**, **Frappé**, and **Latte** Catppuccin themes. Your preference is persisted automatically.

---

## 🪄 Creating Your First Project

1. Click **➕ New Project...** in the Project Manager.
2. In the dialog that appears:
   * **Project Name**: Enter a name (e.g. `MyFirstApp`).
   * **Project Location**: Choose the parent directory where the project folder should be created (defaults to `Documents\HomiCraftProjects`).
   * **Template**:
     * **Empty Project (Clean Slate)**: Starts with a blank window, a clean `main.ui.json`, and an empty `main.py` ready for your custom design.
     * **Counter & Controls Demo**: Starts with a pre-built interactive application featuring counters, buttons, sliders, text inputs, checkboxes, and signal connections.
3. Click **Create & Edit**. HomiCraft will generate the files and launch the visual editor immediately!

---

## 📁 Anatomy of a HomiCraft Project

Every HomiCraft project is completely self-contained in its own folder:

```
MyFirstApp/
├── project.json       # App configuration: window title, dimensions, resizability
├── main.ui.json       # Visual scene hierarchy, widget geometry, styles, and signal links
└── main.py            # Main application Python script (event handlers & lifecycle hooks)
```

### 1. `project.json`
Stores the project's metadata and initial window settings:
```json
{
  "name": "MyFirstApp",
  "version": "1.0.0",
  "window_title": "My First HomiCraft App",
  "window_width": 800,
  "window_height": 600,
  "window_resizable": true,
  "entry_scene": "main.ui.json"
}
```

### 2. `main.ui.json`
Defines the visual scene hierarchy, widget coordinates, dimensions, default properties, and signal callback bindings:
```json
{
  "root": {
    "id": "root_window",
    "type": "Window",
    "x": 0,
    "y": 0,
    "width": 800,
    "height": 600,
    "properties": {
      "title": "My First HomiCraft App"
    },
    "children": [
      {
        "id": "btn_hello",
        "type": "Button",
        "x": 340,
        "y": 260,
        "width": 120,
        "height": 36,
        "properties": {
          "text": "Click Me!"
        },
        "signals": {
          "clicked": "_on_btn_hello_clicked"
        }
      }
    ]
  }
}
```

### 3. `main.py`
The controller logic where you write pure Python code:
```python
def _ready(app):
    print("Application loaded successfully!")

def _on_btn_hello_clicked(app):
    app.btn_hello.text = "Hello World!"
```

---

## 🔄 Returning to the Project Manager

While working inside the visual editor, you never need to close and reopen the application to work on another project. Simply click the **🏠 Projects** button located at the top-left of the main toolbar to cleanly return to the Project Manager hub anytime!
