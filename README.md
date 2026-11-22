# ⚡ HomiCraft — Visual Software Engine for Python

**HomiCraft** is a Godot-inspired visual software development environment for creating native desktop applications with Python and PySide6 (Qt).

---

## 🚀 Quick Start

### 1. Launch the HomiCraft Visual Editor
Open PowerShell or your command line inside `C:\Users\ocean\Documents\GitHub\HomiCraft`:

```powershell
python homi_editor.py
```

This launches the full HomiCraft IDE loaded with the included **Counter & Slider Demo App**.

### 2. Run an App Standalone (Without Editor)
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
