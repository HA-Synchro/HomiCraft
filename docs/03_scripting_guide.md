# 🐍 Chapter 3: Scripting Guide & Application Lifecycle

Scripting in HomiCraft is designed to feel intuitive, clean, and completely Pythonic. Write pure Python code to control widgets, react to signals, and manage state with zero boilerplate.

---

## 💡 Core Scripting Overview

| HomiCraft Pattern | Code Example | Description |
| :--- | :--- | :--- |
| **Lifecycle Hook** | `def _ready(app):` | Called once when the scene and widgets have finished initializing. |
| **Widget Access** | `app.btn_submit` or `btn_submit` | Direct attribute access or injected global access to any widget by its ID. |
| **Property Setters** | `btn.text = "Click Me"` | Intuitive property assignment. |
| **Interaction Control**| `btn.enabled = False` | Controlling component interaction state. |
| **Numeric Values** | `slider.value = 50` | Setting numeric progress or slider positions. |
| **Signal Binding** | Bound via Inspector or `.ui.json` | Visual signal binding linked directly to your Python functions. |

---

## ⏳ The Application Lifecycle: `def _ready(app)`

When an application launches, HomiCraft builds the Qt widget hierarchy, applies initial geometry and properties from the `.ui.json` file, injects widget proxies, and then invokes the `_ready` lifecycle hook.

### Example `_ready` Implementation
```python
def _ready(app):
    print("Application initialized!")
    
    # Set initial widget values
    app.lbl_title.text = "Welcome to HomiCraft"
    app.btn_submit.enabled = False
    app.slider_volume.value = 75
    
    # Initialize global application state
    app.state["click_count"] = 0
    app.state["user_authenticated"] = False
```

> [!NOTE]
> `_ready` can accept either 1 parameter (`def _ready(app):`) or 0 parameters (`def _ready():`). If no parameter is declared, HomiCraft invokes it without arguments.

---

## 🎛️ The `app` Context Object (`HomiAppContext`)

Whenever a callback or lifecycle hook is triggered, HomiCraft provides an instance of `HomiAppContext`. This object gives you full control over the application:

### 1. Accessing Widgets via Dot Notation
Every widget in the scene tree is registered as an attribute on `app` using its unique **Node ID**:
```python
app.lbl_counter.text = "Count: 42"
app.btn_increment.enabled = True
app.input_username.text = "Guest"
```

### 2. Global State Management (`app.state`)
`app.state` is a persistent Python dictionary shared across all scripts in the project:
```python
# In main.py
def _ready(app):
    app.state["theme"] = "dark"
    app.state["score"] = 100

# In another script (e.g. scoreboard.py)
def _on_btn_add_clicked(app):
    app.state["score"] += 10
    app.lbl_score.text = f"Score: {app.state['score']}"
```

### 3. Window Control
You can control the top-level application window directly through `app`:
```python
# Close the application
app.close()

# Access the underlying QMainWindow
app.window.setWindowTitle("Custom Dynamic Title")
```

---

## ⚡ Direct Node Injection (Shorthand Syntax)

In addition to `app.<node_id>`, HomiCraft automatically injects every widget proxy directly into the global namespace of your loaded scripts!

This means you can write:
```python
# Shorthand (Direct Node Injection)
def _on_button_clicked():
    lbl_title.text = "Button was clicked!"
    btn_submit.enabled = False
```
Instead of having to type:
```python
# Full form
def _on_button_clicked(app):
    app.lbl_title.text = "Button was clicked!"
    app.btn_submit.enabled = False
```

Both styles work identically. Use whichever syntax you find most readable!

---

## 🪄 Pythonic Widget Properties

In raw Qt/PySide6, modifying a widget requires calling explicit C++ style methods like `setText()`, `text()`, `setEnabled()`, `setValue()`, `setStyleSheet()`, etc. 

HomiCraft wraps every widget in a `HomiWidgetProxy` that supports direct Python properties for reading and writing:

### Supported Properties Across All Widgets

| Property | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `text` | `str` | Display text (Buttons, Labels, LineEdits, TextEdits) | `btn.text = "Saved!"` |
| `placeholder`| `str` | Placeholder text for input fields | `input_box.placeholder = "Enter email..."` |
| `value` | `int` | Current value for Sliders and ProgressBars | `slider.value = 50` |
| `min` / `max`| `int` | Minimum and maximum range for Sliders / ProgressBars | `progress.max = 200` |
| `enabled` | `bool`| Whether the widget accepts user interaction | `btn.enabled = False` |
| `visible` | `bool`| Whether the widget is shown or hidden | `lbl_error.visible = True` |
| `checked` | `bool`| Check state for CheckBoxes | `chk_agree.checked = True` |
| `x` / `y` | `int` | Horizontal / vertical position on the canvas | `btn.x += 10` |
| `width` / `height` | `int` | Dimensions of the widget in pixels | `btn.width = 160` |
| `style` | `str` | Custom CSS / QSS styling | `btn.style = "background: #a6e3a1;"` |

### Direct Qt Method Forwarding
If you need to call a PySide6 method not covered by property proxies (such as `setFocus()`, `selectAll()`, or `clear()`), the proxy forwards the call directly to the underlying Qt widget instance:
```python
# Forwarded to QLineEdit.clear()
app.input_search.clear()

# Forwarded to QWidget.setFocus()
app.input_search.setFocus()

# Forwarded to QPushButton.click()
app.btn_submit.click()
```

If you ever need the raw underlying PySide6 widget object, use `.raw_widget`:
```python
raw_qt_btn = app.btn_submit.raw_widget
```

---

## 📊 Variables & State Management in Scripts

HomiCraft provides two ways to store data in your application scripts, plus a dedicated **Visual Variables & Outline Panel** in the editor:

### 1. Module-Level Variables (and Python Scoping)
You can declare standard Python variables at the top of your script:
```python
text1 = "Nothing Here"
score = 0
```

> [!WARNING]
> **Python Variable Scoping Rule**:
> In Python, assigning to a variable inside a function (e.g. `text1 = textedit_1.text`) automatically treats that variable as a **local variable** inside that function. The module variable `text1` at the top will **not** be modified unless you declare `global text1`!
>
> ```python
> # ❌ Common Pitfall: creates a local variable 'text1' that is discarded when function exits:
> def _on_textedit_1_textChanged(app):
>     text1 = textedit_1.text
>
> # ✅ Correct: declare 'global text1' to modify the outer variable:
> def _on_textedit_1_textChanged(app):
>     global text1
>     text1 = textedit_1.text
> ```

### 2. App State (`app.state`) — Recommended Practice
To avoid having to remember `global`, use HomiCraft's built-in `app.state` dictionary. Because dictionary mutations update the shared object in-place, no `global` statement is ever required:

```python
def _ready(app):
    # Initialize state variable
    app.state["text1"] = "Nothing Here"

def _on_textedit_1_textChanged(app):
    # Update state variable anywhere
    app.state["text1"] = textedit_1.text

def _on_button_1_clicked(app):
    # Read state variable anywhere
    print(app.state["text1"])
    label_2.text = app.state["text1"]
```

---

## 📑 Visual Script Members & Variables Outline Panel

The Script Workspace includes a built-in **Script Outline & Variables Panel** on the left side of the code editor:

* **📊 Variables List**:
  * Displays all declared module variables, typed annotations, and `app.state` keys in the active script.
  * **`➕ Variable` Button**: Opens the **New Variable Definition Dialog** to visually create variables:
    * Choose Name, Type (`str`, `int`, `float`, `bool`, `list`, `dict`), and Default Value.
    * Select Scope: **Module Variable (Global)** or **App State Variable (`app.state`)**.
    * Automatically generates and inserts clean code into your script.
  * **Single-Click**: Jumps directly to where the variable is declared in the script.
  * **Double-Click**: Inserts the variable name into the code at the current cursor.
  * **Right-Click Menu**: Quick options to jump to definition, insert variable name, or insert `global <name>` at cursor!
* **⚡ Functions List**:
  * Displays all functions and signal handlers in the active script (`_ready`, callbacks).
  * **`➕ Function` Button**: Rapidly scaffolds new functions with parameters and docstrings.
* **◀ / ▶ Toggle**: Collapse or expand the outline panel anytime to maximize code editing space.

---

## 📑 Multi-Script Architecture

HomiCraft supports attaching independent dedicated scripts to individual nodes:

1. **Scene Script (`main.py`)**: The primary controller for the scene. Handles general layout, lifecycle initialization, and global events.
2. **Node Scripts (e.g. `counter.py`, `settings.py`)**: Individual scripts attached to specific widgets.
   * Attach a script to any node by selecting the node in the Scene Hierarchy or Canvas, then choosing or dragging a script into the **Script** slot in the Inspector.
   * Node scripts have their own `_ready(app)` lifecycle hook called automatically when the application starts.
   * Dedicated node scripts help organize large applications by keeping widget-specific logic isolated.
