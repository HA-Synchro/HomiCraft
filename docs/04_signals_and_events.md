# ⚡ Chapter 4: Signals & Event Handling

Signals are HomiCraft's event notification mechanism, built on Python and Qt's signal/slot architecture. When a user interacts with a widget—such as clicking a button, moving a slider, or typing text—the widget emits a signal that executes your Python callback function.

---

## 🎯 Supported Signals by Widget

Every widget in HomiCraft comes with predefined signals corresponding to its user interaction events:

| Widget Component | Supported Signal | When It Fires | Callback Parameters |
| :--- | :--- | :--- | :--- |
| **Button** | `clicked` | User clicks and releases the button. | `(app)` or `()` |
| **Button** | `pressed` | User presses the mouse down on the button. | `(app)` or `()` |
| **Button** | `released` | User releases the mouse button. | `(app)` or `()` |
| **LineEdit** | `textChanged` | Every time the input text changes. | `(text, app)` or `(text)` or `(app)` or `()` |
| **LineEdit** | `returnPressed`| User presses the **Enter** key while focused. | `(app)` or `()` |
| **TextEdit** | `textChanged` | Any character is added or deleted in the editor. | `(app)` or `()` |
| **CheckBox** | `toggled` | The check state changes (checked/unchecked). | `(checked, app)` or `(checked)` or `(app)` or `()` |
| **Slider** | `valueChanged` | The slider position changes. | `(value, app)` or `(value)` or `(app)` or `()` |
| **ProgressBar** | `valueChanged` | The progress value updates. | `(value, app)` or `(value)` or `(app)` or `()` |

---

## 🔗 Connecting Signals Visually

HomiCraft makes connecting signals completely visual and intuitive:

```
┌──────────────────────────────────────────────────────────┐
│ ⚡ Connect Signal: clicked                                │
├──────────────────────────────────────────────────────────┤
│ Connect signal 'clicked' from 'button_1' to a method.     │
│                                                          │
│ Target Script: [ main.py                              ▼ ]│
│ Method Name:   [ _on_button_1_clicked                  ] │
│                                                          │
│                          [ Cancel ]  [ Connect & Code ]  │
└──────────────────────────────────────────────────────────┘
```

### Step-by-Step Connection Guide
1. **Select the Widget**: Click the widget on the Visual Canvas or in the Scene Hierarchy.
2. **Find the Signal**: In the Property Inspector, scroll down to the **⚡ Signals (Events)** section.
3. **Open Connection Dialog**: Click on the signal row you want to connect (for example, `clicked:`).
4. **Choose Target Script**: Select whether the callback should live in `main.py` or a dedicated node script.
5. **Set Method Name**: HomiCraft automatically generates a clean, readable method name (e.g. `_on_btn_inc_clicked`). You can accept this or type your own.
6. **Click "Connect & Code"**:
   * HomiCraft automatically records the connection in `main.ui.json`.
   * Switches to the **Script Workspace**.
   * Opens the target script.
   * Scaffolds the Python callback function at the end of the script:
     ```python
     def _on_button_1_clicked(app):
         # TODO: Handle 'clicked' event
         pass
     ```

---

## 💻 Writing Callback Functions

HomiCraft automatically inspects your callback function signature at runtime and passes parameters accordingly.

### 1. Button Click Handlers
```python
def _on_btn_inc_clicked(app):
    current = int(app.lbl_counter.text)
    app.lbl_counter.text = str(current + 1)
```
Or using direct node injection shorthand:
```python
def _on_btn_inc_clicked():
    current = int(lbl_counter.text)
    lbl_counter.text = str(current + 1)
```

### 2. CheckBox Toggle Handlers
When connecting a CheckBox's `toggled` signal, the callback receives a boolean `checked` status:
```python
def _on_chk_lock_toggled(checked, app):
    app.btn_delete.enabled = not checked
    if checked:
        app.lbl_status.text = "Actions are locked"
    else:
        app.lbl_status.text = "Actions are unlocked"
```

### 3. Slider Value Handlers
When connecting a Slider's `valueChanged` signal, the callback receives an integer `value`:
```python
def _on_slider_speed_value_changed(value, app):
    app.lbl_speed.text = f"Speed: {value} km/h"
    app.progress_bar.value = value
```

### 4. LineEdit Text Change & Return Handlers
```python
# Fired on every keystroke
def _on_input_search_text_changed(text, app):
    app.lbl_preview.text = f"Searching for: {text}"

# Fired when the user presses Enter
def _on_input_search_return_pressed(app):
    query = app.input_search.text
    print(f"Executing search for {query}...")
    app.input_search.clear()
```

---

## 🔍 Navigating & Disconnecting Signals

### Jumping Straight to Code
In the Property Inspector, whenever a signal has an active connection, a **`Code`** button appears next to it. Clicking **`Code`** instantly jumps to the Script Workspace, opens the correct script tab, and moves your cursor directly to the callback definition.

### Disconnecting a Signal
To disconnect a signal:
1. In the Property Inspector, find the connected signal.
2. Click the red **`❌`** button next to it.
3. The binding is removed from `main.ui.json`. The function code in your Python script remains intact so you never lose your work.

---

## 📄 Under the Hood: `main.ui.json`

Signals are saved cleanly inside each widget node's JSON representation:
```json
{
  "id": "btn_save",
  "type": "Button",
  "x": 200,
  "y": 150,
  "width": 120,
  "height": 36,
  "properties": {
    "text": "Save Data"
  },
  "signals": {
    "clicked": "_on_btn_save_clicked"
  }
}
```
This clean separation ensures that layout definitions and code logic remain independent and version-control friendly.
