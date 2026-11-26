# 🎨 Chapter 2: The Visual Editor Interface

The HomiCraft editor is designed for speed, clarity, and visual precision. The interface organizes tools into dedicated docks and workspaces while remaining completely customizable.

---

## 🖥️ Editor Layout Overview

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🏠 Projects │ 💾 Save (Ctrl+S) │ 📑 Duplicate │ ↔️ Center H │ ↕️ Center V │ ▶ Run (F5) │ ⏹ Stop │ 📦 Export │
├─────────────────┬───────────────────────────────────────────────────────────────┬──────────────────────┤
│ SCENE WIDGETS   │  [ 🟡 Visual Canvas ]  [ 📝 Script Workspace ]                │ PROPERTY INSPECTOR   │
│ ├─ Scene Tree   │ ┌───────────────────────────────────────────────────────────┐ │ ├─ Identity        │
│ │  ├─ root      │ │                                                           │ │ │  ├─ ID: btn_inc  │
│ │  ├─ btn_inc   │ │                  [ Click Me! ]                            │ │ │  └─ Script: ...  │
│ │  └─ lbl_title │ │                                                           │ │ ├─ Transform (X,Y) │
│ └─ Widget Tools │ │                                                           │ │ ├─ Properties      │
│                 │ └───────────────────────────────────────────────────────────┘ │ ├─ Style (CSS)     │
│                 │ 📐 Grid Snap: [x] 10px                   🎨 Theme: [Mocha]  │ └─ ⚡ Signals (Events)│
├─────────────────┴───────────────────────────────────────────────────────────────┴──────────────────────┤
│ 📁 FileSystem (res://)                                 │ 🖥️ Output / Debug Console                     │
│ ├── main.py                                            │ [HomiCraft] Application started.              │
│ ├── main.ui.json                                       │ [HomiCraft] Signal connected: clicked         │
│ └── assets/                                            │                                               │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

The editor consists of four primary areas:
1. **Top Toolbar**: Quick actions for file saving, alignment, process execution, export, and theming.
2. **Central Workspace**: Switchable between the **Visual Canvas** (drag-and-drop designer) and the **Script Workspace** (multi-tab code editor).
3. **Left & Right Docks**: Scene Hierarchy & Widget Palette on the left; Property Inspector & Signals on the right.
4. **Bottom Docks**: Project FileSystem (`res://`) and the Output/Debug Console.

---

## 🛠️ The Main Toolbar

| Button / Control | Shortcut | Description |
| :--- | :--- | :--- |
| **🏠 Projects** | — | Returns cleanly to the Project Manager hub without exiting HomiCraft. |
| **💾 Save** | `Ctrl + S` | Saves all changes to `main.ui.json`, `project.json`, and any open scripts. |
| **📑 Duplicate** | `Ctrl + D` | Clones the selected widget, auto-assigning an incremented ID (e.g. `button_1` ➔ `button_2`). |
| **↔️ Center H** | — | Centers the selected widget horizontally inside the window. |
| **↕️ Center V** | — | Centers the selected widget vertically inside the window. |
| **▶ Run** | `F5` | Launches the current project in a separate runtime process with real-time log streaming. |
| **⏹ Stop** | — | Immediately terminates the running application process. |
| **📦 Export .EXE** | — | Opens the 1-Click PyInstaller Exporter dialog to create standalone Windows executables. |
| **🎨 Theme Selector**| — | Switch on the fly between **Mocha**, **Macchiato**, **Frappé**, and **Latte** Catppuccin palettes. |
| **⚙️ Settings** | `Ctrl + ,` | Opens the dedicated Preferences window (UI Scale, Themes, Fonts, Grid & Layout). |
| **📐 Reset Layout** | — | Restores all docks to their default arrangement. |
| **🔲 Grid Snap** | — | Toggles alignment grid snapping on the visual canvas. |

---

## ⚙️ The Editor Settings Window

Accessed by clicking **`⚙️ Settings`** in the main toolbar or pressing **`Ctrl + ,`**, this dedicated preferences window provides full control over your development environment:

```
┌────────────────────────────────────────────────────────────────────────┐
│ ⚙️ HomiCraft — Editor Settings                                          │
├────────────────────────────────────────────────────────────────────────┤
│ [ 🖥️ Display & Scaling ] [ 📐 Canvas & Grid ] [ 🗂️ Workspace ] [ 📦 Export ] │
├────────────────────────────────────────────────────────────────────────┤
│ 🔍 Display & Text Scale (Windows Scale Equivalent):                     │
│ Adjusts the scale of all editor texts, buttons, docks, and controls:   │
│                                                                        │
│ [━━━━━━●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━] [ 150% ▲▼ ]                 │
│ Quick Presets: [ 75% ] [ 100% ] [ 125% ] [ 150% ] [ 175% ] [ 200% ]    │
│ ┌────────────────────────────────────────────────────────────────────┐ │
│ │ Sample UI Text (150% Scale)                                        │ │
│ └────────────────────────────────────────────────────────────────────┘ │
│                                                                        │
│ Theme Flavor:     [ 🌿 Mocha (Deep Dark)                           ▼ ] │
│ Code Editor Font: [ Consolas                                       ▼ ] │
│ Code Font Size:   [ 11 pt                                          ▲▼ ]│
├────────────────────────────────────────────────────────────────────────┤
│ [ ↺ Restore Defaults ]         [ Cancel ]  [ Apply ]  [ Save & Close ] │
└────────────────────────────────────────────────────────────────────────┘
```

### 1. 🖥️ Display & Scaling Tab
* **UI Scale Slider & SpinBox (50% to 250%)**: Works like the Windows Display Scale setting. Scales all UI texts, buttons, tabs, docks, padding, and dialogs cleanly to match your monitor resolution (e.g. 1080p, 1440p, 4K High-DPI).
* **Scale Quick Presets**: Instant one-click scale buttons (`75%`, `100%`, `125%`, `150%`, `175%`, `200%`).
* **Live Scale Preview**: Real-time sample box that shows the exact text size before applying.
* **Theme Flavor**: Switch between Mocha, Macchiato, Frappé, and Latte.
* **Code Editor Font & Size**: Choose any system monospace font (e.g. `Consolas`, `Cascadia Code`, `JetBrains Mono`) and set custom point size.

### 2. 📐 Canvas & Grid Tab
* **Grid Snapping**: Toggle default grid snapping behavior.
* **Grid Step Size (2px to 64px)**: Configure custom grid step intervals (presets: `5px`, `10px`, `16px`, `20px`).

### 3. 🗂️ Workspace & Layout Tab
* **Remember Dock Layout on Exit**: Checkbox (enabled by default). Saves dock positions, sizes, active tabs, floating windows, and main window dimensions to `%APPDATA%\HomiCraft\Layout.ini`.
* **Auto-Save on Run (F5)**: Automatically saves project files before executing.
* **📐 Reset Dock Layout Now**: One-click action to untabify, un-float, and restore default dock layout.
* **🗑️ Clear Saved Layout Cache**: Resets saved layout cache if you ever want a fresh start.

### 4. 📦 Build & Export Tab
* **Default Executable Mode**: Choose default mode for standalone exports (`Windowed` vs `Console Debug`).
* **Default Output Folder**: Customize the default output destination directory.

---

The Visual Canvas is your live interactive layout stage. It renders your user interface exactly as it will appear when your application runs.

### 1. Adding Widgets to the Canvas
* Click the **Widgets** tab on the left dock to open the Widget Palette.
* Click on any widget (`Button`, `Label`, `LineEdit`, `CheckBox`, `Slider`, `ProgressBar`, `Panel`) to instantly spawn it onto the canvas at a default position.

### 2. Selecting & Moving Widgets
* **Click** on any widget to select it. A bounding box with a resize handle will indicate selection.
* **Drag** the widget anywhere across the canvas. If **Grid Snap** is enabled, coordinates snap to 10-pixel increments automatically.
* **Arrow Keys**: Move the selected widget by 10 pixels in any direction.
* **Shift + Arrow Keys**: Micro-nudge the widget by single pixels (`1px`) for pixel-perfect alignment.
* **Click Background**: Clicking the canvas background selects the root `Window`, allowing you to inspect and modify the main window's title, default size, and background CSS.

### 3. Resizing Widgets
* Hover over the **bottom-right corner handle** of a selected widget.
* Click and drag to resize the widget to your desired dimensions. If grid snapping is active, dimensions snap to multiples of 10px.

### 4. Duplication & Deletion
* Press **`Ctrl + D`** (or click **Duplicate** in the toolbar) to clone the selected widget. The duplicate is placed slightly offset and given a unique, auto-incremented ID.
* Press **`Delete`** or **`Backspace`** (or click the red **Delete Node** button in the Scene Hierarchy) to remove the selected widget from the scene.

### 5. Double-Click to Jump to Code
* Double-clicking any interactive widget (like a Button) on the canvas immediately switches to the **Script Workspace**, opens the relevant script, and scaffolds the default event handler (e.g. `def _on_button_1_clicked(app):`)!

---

## 🌳 The Scene Hierarchy Dock

The Scene Hierarchy displays your application's widget tree.

* **Root Window**: The top-level container of your application.
* **Child Nodes**: Every button, label, input, or container in your scene is listed with its **Node ID** and **Type**.
* **Selection Sync**: Clicking a node in the hierarchy selects it on the canvas and loads its properties in the Inspector. Conversely, clicking a widget on the canvas highlights it in the hierarchy.

### 🚀 Pro-Tip: Drag Node to Script
Easily generate references directly into your code:
1. Click and drag any node (e.g. `lbl_counter`) from the Scene Hierarchy dock.
2. Drop it directly into the **Script Editor**!
   * If dropped on a blank line, it inserts:
     ```python
     lbl_counter = app.lbl_counter
     ```
   * If dropped inside an existing expression or function call, it inserts:
     ```python
     app.lbl_counter
     ```

---

## 🔍 The Property Inspector Dock

When any node is selected, the Property Inspector dock displays all editable attributes in clean, organized sections:

### 1. Identity
* **Node ID**: The unique variable name used to access this widget in Python scripts (e.g. `btn_submit`, `lbl_score`).
* **Type**: The widget component type (`Button`, `Label`, `Slider`, etc.).
* **Script**: Shows which `.py` script is currently attached to this node. You can drag any script from the FileSystem dock and drop it directly onto this slot!

### 2. Transform & Geometry
* **X / Y**: The horizontal and vertical position in pixels.
* **Width / Height**: The dimensions of the widget in pixels.
* You can type values directly into these fields for precision layout.

### 3. Custom Properties
Depending on the widget type, relevant properties appear automatically:
* **Button**: `text`, `enabled`
* **Label**: `text`, `alignment` (left, center, right)
* **LineEdit**: `text`, `placeholder`, `readOnly`
* **TextEdit**: `plainText`, `placeholder`, `readOnly`
* **CheckBox**: `text`, `checked`
* **Slider / ProgressBar**: `min`, `max`, `value`

### 4. Custom CSS Styling (QSS)
HomiCraft allows full CSS styling per widget. You can enter CSS rules directly into the **Style (CSS)** field:
```css
background-color: #f38ba8; color: #1e1e2e; font-weight: bold; border-radius: 12px;
```
Changes render immediately on the visual canvas!

### 5. Signals (Events)
Displays all supported signals for the selected widget (e.g. `clicked`, `pressed`, `released` for Buttons; `valueChanged` for Sliders).
* **Green Indicator**: The signal is currently connected to a Python callback function.
* **`Code` Button**: Clicking this jumps straight to the script where the callback function is defined.
* **`❌` Button**: Disconnects the signal handler.

---

## 📁 The FileSystem Dock (`res://`)

The FileSystem dock displays all files in your project directory (the `res://` root):

* **`+ Script` Button**: Creates a new Python script file in the project.
* **`+ Folder` Button**: Creates a new subdirectory.
* **Right-Click Context Menu**:
  * **Open in Script Workspace**: Opens the script in a new editor tab.
  * **Attach to Selected Node**: Attaches the script to whichever widget is currently selected in the Inspector.
  * **Rename**: Safely renames the file on disk.
  * **Delete**: Removes the file from the project.
* **Drag & Drop**: Drag any `.py` script onto a widget on the canvas or onto the Inspector's Script slot to attach it.

---

## 🖥️ The Output / Debug Console Dock

The Output Console captures all process output in real time when you run your application (`F5`):

* **Standard Output (`stdout`)**: Printed messages from Python (`print("...")`).
* **Error Output (`stderr`)**: Syntax errors, unhandled exceptions, and traceback logs.
* **Lifecycle Events**: Displays notification messages when scenes load, signals bind, or scripts execute.
* **Clear Console**: Right-click to clear previous run logs.

---

## 🧩 Dock Customization & Persistent Layouts

Every dock in HomiCraft is a fully modular Qt dock widget designed for maximum workspace flexibility:
* **Tabbing**: Drag a dock header over another dock to combine them into tabbed panels.
* **Splitting**: Drag a dock to any border of another dock to split horizontally or vertically.
* **Floating**: Drag a dock outside the main window to turn it into an independent floating window (perfect for multi-monitor setups).
* **Dock Resizing**: Drag the splitters between docks to adjust their relative widths and heights.

### 💾 Automatic Layout Memory
HomiCraft automatically remembers your exact layout between sessions:
* **Auto-Save**: Whenever you rearrange docks, tab panels together, detach floating windows, or resize docks, HomiCraft records the layout state instantly.
* **Session Persistence**: When you close the editor and reopen it later—or switch between different projects via the Project Manager—your exact customized layout (including dock positions, sizes, active tabs, and window geometry) is restored automatically.
* **📐 Reset Layout**: If your workspace ever becomes cluttered or you want to return to the clean default arrangement, click **📐 Reset Layout** in the main toolbar. This safely un-floats, untabifies, and docks all panels back into their default positions, making all docks visible and saving the clean default state.
