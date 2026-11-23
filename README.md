# ⚡ HomiCraft — Visual Software Engine for Python

**HomiCraft** is a Godot-inspired visual software development environment for creating native desktop applications with Python and PySide6 (Qt).

---

## 🚀 Quick Start

### 1. Launch via Standalone Executable (`HomiCraft.exe`)
You can launch the editor without Python installed by running the standalone executable directly:

```powershell
dist\HomiCraft\HomiCraft.exe
```
Or double-click **`HomiCraft.exe`** directly from Windows Explorer!

### 2. Launch via Python (Project Manager Hub)
If you prefer running from source:

```powershell
python homi_editor.py
```

When started without arguments, HomiCraft opens the **Project Manager** (Godot style):
* **Select & Edit:** Browse existing projects, double-click or press **✏️ Edit Project** to open the full IDE.
* **➕ New Project:** Create new projects anywhere on your drive with your choice of template:
  * **Empty Project (Clean Slate)**
  * **Counter & Controls Demo** (Preconfigured widgets and signal scripts)
* **▶ Run Standalone:** Launch any project instantly without loading the full editor.
* **📂 Import / Scan:** Import existing folders into your project list.
* **📝 Rename Project:** Rename projects directly with auto-updating `project.json`.
* **🔍 Show in Explorer:** Jump straight to the project folder on disk.
* **🗑️ Remove from List / 💥 Delete Files:** Safely remove projects from recent list or permanently delete files.
* **🏠 Return to Project Manager:** While inside the editor, click **"🏠 Projects"** in the top toolbar anytime to switch projects.

### 2. Launch Editor Directly for a Project
You can also open the editor directly for any project from the command line:

```powershell
python homi_editor.py examples/counter_app
```

### 3. Run an App Standalone (Without Editor)
You can run any HomiCraft project standalone via the CLI runner:

```powershell
python runner.py examples/counter_app
```

---

## 🛠️ Godot Concept Mapping

| Godot Concept | HomiCraft Equivalent | Description |
| :--- | :--- | :--- |
| **Node / Control** | **Widget Component** | `Button`, `LineEdit`, `Label`, `CheckBox`, `Slider`, `ProgressBar`, `Panel` |
| **Scene Tree** | **Scene Hierarchy Dock** | Visual tree dock showing nested components |
| **FileSystem (res://)** | **FileSystem Dock** | Project explorer with New Script, New Folder, Rename, Delete |
| **.tscn File** | **.ui.json File** | Clean, human-readable JSON storing layout & properties |
| **Inspector Dock** | **Property Inspector** | Live property & geometry tweaker with CSS styling |
| **Signals Dock** | **Signals & Events** | `clicked`, `textChanged`, `valueChanged`, `toggled` with 1-click code link |
| **Script (.gd)** | **Python Controller (`main.py`)** | Clean Python script containing event callbacks |
| **`$"btn"` / `get_node()`** | **`app.btn`** | Direct attribute access to any widget by its ID |
| **`func _ready():`** | **`def _ready(app):`** | Called automatically on application startup |
| **Play (F5)** | **Run App (F5)** | Starts project in a separate process with live log output |
| **Export Templates** | **📦 Export .EXE** | One-click standalone Windows `.exe` packager via PyInstaller |

---

## 🎨 Official Catppuccin Themes & Modern UI

HomiCraft now includes the complete palette suite from [catppuccin.com](https://catppuccin.com/palette/) with rounded-corner UI styling:
* 🌿 **Catppuccin Mocha** (Default Deep Dark)
* ☕ **Catppuccin Macchiato** (Medium Dark Contrast)
* 🍨 **Catppuccin Frappé** (Soft Dark Pastel)
* 🥛 **Catppuccin Latte** (Crisp Light Theme)

Switch between them on the fly from the **`🎨 Theme`** selector in the main toolbar! The code editor, docks, rounded buttons, and inputs update their color schemes and syntax highlighting instantly.

---

## 🎮 Keyboard Shortcuts & Workflow

* **Drag Node from Hierarchy to Script (Godot style):** Drag any node (e.g. `button_1`, `lbl_title`) from the Scene Hierarchy dock directly into the Script Editor!
  * On a blank line: inserts `{node_id} = app.{node_id}`
  * Inside an expression: inserts `app.{node_id}`
* **Pythonic Object Properties:** Access and modify widget properties directly without raw C++ methods:
  * `button_1.text = "Click Me"` (or `app.button_1.text = "Click Me"`)
  * `button_1.enabled = False`
  * `label.text = "Score: 100"`
  * `slider.value = 80`
  * `button_1.x += 10`, `button_1.width = 200`
* **Drag & Drop Scripts (Godot Style):** Drag any `.py` script from the FileSystem dock directly onto the **Script slot** in the Inspector (or drop it straight onto the button on the canvas) to instantly attach it!
* **Godot-Style Dock Customization:** All docks (Scene, FileSystem, Inspector, Debug Console) are completely unchained. You can drag the FileSystem dock next to the Output Console, tab docks together, split horizontally/vertically, or float them as independent windows. Click **"📐 Reset Layout"** in the toolbar at any time to return to the default layout.
* **Click & Drag:** Move widgets across the canvas (10px snap grid).
* **Corner Drag:** Resize widgets from the bottom-right handle.
* **Arrow Keys:** Nudge selected widget by grid units (hold **Shift** for 1px micro-adjustments).
* **Ctrl + D:** Duplicate the selected widget with an auto-incremented ID.
* **Delete / Backspace:** Remove the selected widget.
* **Double-Click Widget:** Jump straight into the script editor and scaffold the callback function.
* **Click Canvas Background:** Inspect and customize root Window properties (Title, Dimensions, Background CSS).
* **Ctrl + S:** Save project.
* **F5:** Run project.
* **📦 Export .EXE:** Open the standalone executable builder.

---

## 📁 Project Structure

Every HomiCraft project is self-contained:
```
my_app/
├── project.json            # Window title, default dimensions, entry scene
├── main.ui.json            # Visual layout, widget hierarchy, properties, signal bindings
└── main.py                 # Python controller logic
```
