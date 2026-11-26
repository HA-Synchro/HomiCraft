# 📚 Chapter 8: Complete API & Widget Reference

This document provides a complete technical reference for all built-in widgets, proxies, context methods, and properties in HomiCraft.

---

## 🧩 Widget Components Reference

---

### 1. `Button`
Standard interactive push button.

* **Underlying Qt Class**: `QPushButton`
* **Default Dimensions**: `120 x 36 px`
* **Category**: Basic

#### Properties
| Property | Type | Default | Access | Description |
| :--- | :--- | :--- | :--- | :--- |
| `text` | `str` | `"Button"` | Read / Write | The label text displayed on the button. |
| `enabled` | `bool` | `True` | Read / Write | Whether the button responds to clicks. |
| `visible` | `bool` | `True` | Read / Write | Whether the button is visible. |
| `style` | `str` | `""` | Read / Write | Custom CSS / QSS styling. |
| `x`, `y` | `int` | Canvas pos | Read / Write | Position coordinates in pixels. |
| `width`, `height` | `int` | `120`, `36` | Read / Write | Dimensions in pixels. |

#### Signals
| Signal | Description | Callback Signature |
| :--- | :--- | :--- |
| `clicked` | Emitted when the button is clicked. | `def callback(app):` or `def callback():` |
| `pressed` | Emitted immediately when mouse is pressed down. | `def callback(app):` or `def callback():` |
| `released` | Emitted when mouse button is released. | `def callback(app):` or `def callback():` |

#### Example Usage
```python
# Change text and disable
app.btn_save.text = "Saved!"
app.btn_save.enabled = False

# Trigger a programmatic click
app.btn_save.click()
```

---

### 2. `Label`
Displays static or dynamic read-only text.

* **Underlying Qt Class**: `QLabel`
* **Default Dimensions**: `140 x 30 px`
* **Category**: Basic

#### Properties
| Property | Type | Default | Access | Description |
| :--- | :--- | :--- | :--- | :--- |
| `text` | `str` | `"Label Text"` | Read / Write | The text string displayed in the label. |
| `alignment` | `str` | `"left"` | Read / Write | Text alignment: `"left"`, `"center"`, or `"right"`. |
| `visible` | `bool` | `True` | Read / Write | Whether the label is rendered. |
| `style` | `str` | `"font-size: 14px;"`| Read / Write | Custom CSS / QSS styling. |

#### Signals
* None (Labels are display-only by default).

#### Example Usage
```python
app.lbl_counter.text = f"Items: {len(app.state['items'])}"
app.lbl_counter.style = "color: #a6e3a1; font-weight: bold;"
```

---

### 3. `LineEdit`
Single-line text input field.

* **Underlying Qt Class**: `QLineEdit`
* **Default Dimensions**: `180 x 34 px`
* **Category**: Input

#### Properties
| Property | Type | Default | Access | Description |
| :--- | :--- | :--- | :--- | :--- |
| `text` | `str` | `""` | Read / Write | The current text inside the input box. |
| `placeholder` | `str` | `"Enter text..."`| Read / Write | Ghost placeholder text when empty. |
| `readOnly` | `bool` | `False` | Read / Write | If `True`, user cannot edit text. |
| `enabled` | `bool` | `True` | Read / Write | If `False`, input is disabled and grayed out. |

#### Signals
| Signal | Description | Callback Signature |
| :--- | :--- | :--- |
| `textChanged` | Emitted on every keystroke. | `def callback(text, app):` or `def callback(text):` |
| `returnPressed`| Emitted when user presses **Enter**. | `def callback(app):` or `def callback():` |

#### Example Usage
```python
def _on_input_name_return_pressed(app):
    user_name = app.input_name.text.strip()
    if user_name:
        app.lbl_greeting.text = f"Welcome, {user_name}!"
        app.input_name.clear()
```

---

### 4. `TextEdit`
Multi-line formatted or plain text editor area.

* **Underlying Qt Class**: `QTextEdit`
* **Default Dimensions**: `240 x 120 px`
* **Category**: Input

#### Properties
| Property | Type | Default | Access | Description |
| :--- | :--- | :--- | :--- | :--- |
| `text` | `str` | `""` | Read / Write | The full plain-text content of the editor. |
| `placeholder` | `str` | `"Enter long text..."`| Read / Write | Placeholder string. |
| `readOnly` | `bool` | `False` | Read / Write | If `True`, text is read-only. |

#### Signals
| Signal | Description | Callback Signature |
| :--- | :--- | :--- |
| `textChanged` | Emitted whenever text changes. | `def callback(app):` or `def callback():` |

---

### 5. `CheckBox`
Interactive binary toggle option with a text label.

* **Underlying Qt Class**: `QCheckBox`
* **Default Dimensions**: `120 x 30 px`
* **Category**: Input

#### Properties
| Property | Type | Default | Access | Description |
| :--- | :--- | :--- | :--- | :--- |
| `text` | `str` | `"Check Option"` | Read / Write | Label displayed alongside the checkmark. |
| `checked` | `bool` | `False` | Read / Write | `True` if checked; `False` if unchecked. |
| `enabled` | `bool` | `True` | Read / Write | Whether the checkbox can be toggled. |

#### Signals
| Signal | Description | Callback Signature |
| :--- | :--- | :--- |
| `toggled` | Emitted whenever check state changes. | `def callback(checked, app):` or `def callback(checked):` |

#### Example Usage
```python
def _on_chk_dark_mode_toggled(checked, app):
    if checked:
        app.window.setStyleSheet("background-color: #1e1e2e; color: #cdd6f4;")
    else:
        app.window.setStyleSheet("background-color: #eff1f5; color: #4c4f69;")
```

---

### 6. `Slider`
Horizontal slider for selecting a numeric value in a range.

* **Underlying Qt Class**: `QSlider` (Horizontal)
* **Default Dimensions**: `160 x 24 px`
* **Category**: Input

#### Properties
| Property | Type | Default | Access | Description |
| :--- | :--- | :--- | :--- | :--- |
| `value` | `int` | `50` | Read / Write | Current slider position. |
| `min` | `int` | `0` | Read / Write | Minimum value. |
| `max` | `int` | `100` | Read / Write | Maximum value. |

#### Signals
| Signal | Description | Callback Signature |
| :--- | :--- | :--- |
| `valueChanged` | Emitted as user drags or changes slider. | `def callback(value, app):` or `def callback(value):` |

---

### 7. `ProgressBar`
Horizontal visual indicator of task or value progress.

* **Underlying Qt Class**: `QProgressBar`
* **Default Dimensions**: `180 x 24 px`
* **Category**: Display

#### Properties
| Property | Type | Default | Access | Description |
| :--- | :--- | :--- | :--- | :--- |
| `value` | `int` | `0` | Read / Write | Current progress value. |
| `min` | `int` | `0` | Read / Write | Minimum range value. |
| `max` | `int` | `100` | Read / Write | Maximum range value. |

#### Signals
| Signal | Description | Callback Signature |
| :--- | :--- | :--- |
| `valueChanged` | Emitted when the progress value changes. | `def callback(value, app):` |

---

### 8. `Panel`
Visual container frame for grouping components or creating cards.

* **Underlying Qt Class**: `QFrame`
* **Default Dimensions**: `250 x 180 px`
* **Category**: Containers
* **Default Style**: `background-color: #2b2b2b; border-radius: 8px;`

---

## 🎛️ `HomiAppContext` API

Passed to `_ready(app)` and event callbacks.

| Method / Attribute | Type | Description |
| :--- | :--- | :--- |
| `app.<node_id>` | `HomiWidgetProxy` | Direct attribute access to any widget by its Node ID. |
| `app.get_widget(id)`| `Optional[HomiWidgetProxy]` | Retrieves a widget proxy by string ID safely. |
| `app.state` | `Dict[str, Any]` | Shared dictionary for application-wide state. |
| `app.window` | `QMainWindow` | Reference to the main window host. |
| `app.close()` | `None` | Gracefully closes the running application. |

---

## 🛡️ `HomiWidgetProxy` API

Every widget accessed through `app` or direct injection is wrapped in `HomiWidgetProxy`.

| Property / Method | Return Type | Description |
| :--- | :--- | :--- |
| `.raw_widget` | `QWidget` | The underlying PySide6 Qt widget instance. |
| `.text` | `str` | Text content (getter & setter). |
| `.placeholder` | `str` | Placeholder text (getter & setter). |
| `.value` | `int` | Numeric value (getter & setter). |
| `.min`, `.max` | `int` | Numeric range limits. |
| `.enabled` | `bool` | Interaction enabled state. |
| `.visible` | `bool` | Visibility state. |
| `.checked` | `bool` | Boolean check state. |
| `.x`, `.y` | `int` | Position coordinates on canvas. |
| `.width`, `.height`| `int` | Size dimensions in pixels. |
| `.style` | `str` | CSS/QSS stylesheet string. |
| `.<qt_method>(...)`| `Any` | Automatic fallback forwarding to underlying Qt methods. |

---

## 🖥️ Standalone CLI Runner (`runner.py`)

Run any project from the terminal without loading the editor GUI:

```powershell
python runner.py <path_to_project_folder>
```

### Examples:
```powershell
# Run the built-in counter demo
python runner.py examples/counter_app

# Run a custom project
python runner.py C:\Users\ocean\Documents\HomiCraftProjects\MyCalculator
```
