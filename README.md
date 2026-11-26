# ⚡ HomiCraft — Visual Software Engine for Python

**HomiCraft** is a modern visual software development engine for creating native desktop applications with Python and PySide6 (Qt).

---

## 📚 Complete Documentation Suite

Comprehensive and detailed documentation is available for all features:

* **📖 [Complete Developer Manual (DOCUMENTATION.md)](DOCUMENTATION.md)** — All-in-one offline guide, system architecture, API reference, and code recipes.
* **📂 [Modular Guides (docs/)](docs/)**:
  1. [**01: Getting Started & Project Manager**](docs/01_getting_started.md)
  2. [**02: The Visual Editor Interface**](docs/02_editor_guide.md)
  3. [**03: Scripting Guide & Lifecycle**](docs/03_scripting_guide.md)
  4. [**04: Signals & Event Handling**](docs/04_signals_and_events.md)
  5. [**05: Code Editor & Autocompletion Engine**](docs/05_code_editor_and_autocompletion.md)
  6. [**06: Exporting Standalone Applications (.EXE)**](docs/06_exporting_standalone_apps.md)
  7. [**07: Catppuccin Theming & UI Styling**](docs/07_catppuccin_theming.md)
  8. [**08: Complete API & Widget Reference**](docs/08_api_and_widget_reference.md)

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

When started without arguments, HomiCraft opens the **Project Manager** hub:
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

### 3. Launch Editor Directly for a Project
You can also open the editor directly for any project from the command line:

```powershell
python homi_editor.py examples/counter_app
```

### 4. Run an App Standalone (Without Editor)
You can run any HomiCraft project standalone via the CLI runner:

```powershell
python runner.py examples/counter_app
```

---

## 🛠️ Core Concepts & Architecture

| Component / Concept | HomiCraft Implementation | Description |
| :--- | :--- | :--- |
| **Widgets & Controls** | **Visual Components** | `Button`, `LineEdit`, `Label`, `CheckBox`, `Slider`, `ProgressBar`, `Panel` |
| **Scene Hierarchy** | **Scene Hierarchy Dock** | Visual tree dock showing nested components and parent-child order |
| **FileSystem Explorer** | **FileSystem Dock (`res://`)** | Project explorer with New Script, New Folder, Rename, Delete |
| **Declarative Layout** | **`.ui.json` Scene Files** | Clean, human-readable JSON storing layout, geometry & properties |
| **Property Inspector** | **Property Inspector Dock** | Live property & geometry tweaker with custom CSS styling |
| **Signals & Callbacks** | **Signals & Events** | `clicked`, `textChanged`, `valueChanged`, `toggled` with 1-click code wiring |
| **Script Controllers** | **Python Controller (`main.py`)** | Clean Python scripts containing event callbacks and business logic |
| **Node Referencing** | **`app.btn` or `btn`** | Direct attribute access or injected global access to any widget by its ID |
| **Lifecycle Entry** | **`def _ready(app):`** | Called automatically on application startup when widgets are initialized |
| **Process Runner** | **Run App (F5)** | Starts project in a separate process with live log output |
| **Executable Exporter** | **📦 Export .EXE** | One-click standalone Windows `.exe` packager via PyInstaller |

---

## 🎨 Official Catppuccin Themes & Modern UI

HomiCraft now includes the complete palette suite from [catppuccin.com](https://catppuccin.com/palette/) with rounded-corner UI styling:
* 🌿 **Catppuccin Mocha** (Default Deep Dark)
* ☕ **Catppuccin Macchiato** (Medium Dark Contrast)
* 🍨 **Catppuccin Frappé** (Soft Dark Pastel)
* 🥛 **Catppuccin Latte** (Crisp Light Theme)

Switch between them on the fly from the **`🎨 Theme`** selector in the main toolbar or the **`⚙️ Settings`** window (`Ctrl+,`). The code editor, docks, rounded buttons, and inputs update their color schemes and syntax highlighting instantly.

---

## 🔍 Display & Text Scaling (Windows Scale Equivalent)

HomiCraft includes dynamic UI scaling from **50% to 250%**:
* Scale all application texts, buttons, tabs, docks, padding, and dialogs smoothly to match 1080p, 1440p, or 4K monitors.
* Quick preset buttons (`75%`, `100%`, `125%`, `150%`, `175%`, `200%`) with live preview in the **`⚙️ Settings`** dialog.

---

## 💻 Intelligent Autocompletion Engine

The built-in code editor provides IDE-grade autocompletion:
* **Fuzzy Substring Matching**: Typing `imp` surfaces `import`, `ImportError`, `ImportWarning`, `__import__`, `NotImplemented`, etc.
* **Category Badges**: `[K]` Keyword, `[f]` Function, `[C]` Class, `[E]` Exception, `[w]` Widget, `[p]` Property, `[s]` Snippet, `[v]` Variable.
* **Contextual Dot Completion**:
  * Typing `app.` lists all live scene widgets.
  * Typing `<widget_id>.` lists all properties (`text`, `value`, `enabled`, etc.) and methods (`click()`, `setFocus()`).
* **Live Scene Sync**: Adding, duplicating, renaming, or deleting widgets updates the autocompletion engine instantly.
* **Keyboard Navigation**: `Ctrl + Space` to trigger, `Enter` / `Tab` to complete, `Up` / `Down` to navigate, `Escape` to dismiss.

---

## 🎮 Keyboard Shortcuts & Workflow

* **Drag Node from Hierarchy to Script:** Drag any node (e.g. `button_1`, `lbl_title`) from the Scene Hierarchy dock directly into the Script Editor!
  * On a blank line: inserts `{node_id} = app.{node_id}`
  * Inside an expression: inserts `app.{node_id}`
* **Pythonic Object Properties:** Access and modify widget properties directly without raw C++ methods:
  * `button_1.text = "Click Me"` (or `app.button_1.text = "Click Me"`)
  * `button_1.enabled = False`
  * `label.text = "Score: 100"`
  * `slider.value = 80`
  * `button_1.x += 10`, `button_1.width = 200`
* **Drag & Drop Scripts:** Drag any `.py` script from the FileSystem dock directly onto the **Script slot** in the Inspector (or drop it straight onto the button on the canvas) to instantly attach it!
* **Modular Dock Customization & Persistent Layouts:** All docks (Scene, FileSystem, Inspector, Debug Console) are completely unchained. You can drag the FileSystem dock next to the Output Console, tab docks together, split horizontally/vertically, or float them as independent windows. HomiCraft automatically remembers your exact custom layout and window geometry across sessions! Click **"📐 Reset Layout"** in the toolbar at any time to return to the default layout.
* **⚙️ Editor Settings (`Ctrl + ,`):** Configure UI scale, themes, fonts, canvas grid, and build options in a single modal hub.
* **Click & Drag:** Move widgets across the canvas (grid snapping).
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
