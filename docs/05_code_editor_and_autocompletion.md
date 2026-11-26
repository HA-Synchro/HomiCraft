# 💻 Chapter 5: Code Editor & Autocompletion

HomiCraft includes a modern, built-in code editor built directly into the central workspace. It provides a full IDE editing experience tailored for Python and PySide6 with zero external dependencies.

---

## 🖥️ Script Workspace Features

```
┌────────────────────────────────────────────────────────────────────────┐
│ [ 🟡 Visual Canvas ]  [ 📝 Script Workspace ]                          │
├────────────────────────────────────────────────────────────────────────┤
│ [ main.py  x ] [ counter.py  x ]                                       │
├────────────────────────────────────────────────────────────────────────┤
│ 1  def _ready(app):                                                    │
│ 2      app.lbl_title.text = "Counter App"                              │
│ 3                                                                      │
│ 4  def _on_btn_inc_clicked(app):                                       │
│ 5      imp                                                             │
│ 6          ┌───────────────────────────────────┐                       │
│ 7          │ [K] import                        │                       │
│ 8          │ [E] ImportError                   │                       │
│ 9          │ [E] ImportWarning                 │                       │
│ 10         │ [f] __import__                    │                       │
│ 11         │ [C] NotImplemented                │                       │
│ 12         │ [E] NotImplementedError           │                       │
│            └───────────────────────────────────┘                       │
└────────────────────────────────────────────────────────────────────────┘
```

### 1. Multi-Tab Interface
* Open as many scripts as needed simultaneously.
* Each tab has a close (`x`) button.
* Unsaved changes are safely tracked and saved automatically when pressing **`Ctrl + S`** or running the app (**`F5`**).

### 2. Full Syntax Highlighting
* **Keywords**: Highlighted in vibrant Mauve/Blue (e.g. `def`, `class`, `import`, `return`, `if`, `for`).
* **Strings**: Rendered in soft Green (e.g. `"Hello World"`, `f"Count: {val}"`).
* **Comments**: Styled in muted Gray/Subtext (e.g. `# TODO: implement`).
* **Numbers**: Crisp Peach/Orange.
* **Functions & Classes**: Distinctly colored for effortless scanning.
* Automatically adjusts color contrast when switching Catppuccin themes.

### 3. Smart Indentation & Formatting
* **Auto-Indent**: Pressing **Enter** after a colon (`:`) automatically indents the next line by 4 spaces.
* **4-Space Tab**: Pressing **Tab** inserts 4 soft spaces.
* **Smart Backspace**: Pressing **Backspace** at an indentation level un-indents by 4 spaces cleanly.
* **Line Number Margin**: Shows line numbers with active line highlighting for easy debugging.

---

## ⚡ The Intelligent Autocompletion Engine

HomiCraft features a custom, fuzzy-matching autocompletion engine designed specifically for GUI development.

### Substring / Fuzzy Matching (`MatchContains`)
Unlike basic editors that only match prefixes, HomiCraft matches characters anywhere in the keyword:
* Typing **`imp`** surfaces:
  * `import` (starts with `imp`)
  * `ImportError` (starts with `imp`)
  * `ImportWarning` (starts with `imp`)
  * `__import__` (contains `imp`)
  * `NotImplemented` (contains `imp`)
  * `NotImplementedError` (contains `imp`)
* Typing **`de`** surfaces:
  * `def`
  * `del`
  * `delattr`
  * `_ready` snippet

---

## 🏷️ Completion Badges & Categories

Every item in the autocompletion popup displays a category badge so you can instantly identify what type of symbol you are selecting:

| Badge | Category | Description | Examples |
| :---: | :--- | :--- | :--- |
| `[K]` | **Keyword** | Core Python language keywords | `import`, `def`, `class`, `return`, `if`, `while` |
| `[f]` | **Function** | Built-in Python functions | `print`, `len`, `range`, `enumerate`, `__import__` |
| `[C]` | **Class** | Standard Python types & classes | `dict`, `list`, `int`, `str`, `NotImplemented` |
| `[E]` | **Exception** | Built-in Python exceptions | `ImportError`, `ValueError`, `KeyError` |
| `[w]` | **Widget** | **Live Scene Tree Node!** | `button_1`, `lbl_title`, `slider_speed` |
| `[p]` | **Property** | Pythonic widget properties | `text`, `value`, `enabled`, `checked`, `visible` |
| `[s]` | **Snippet** | Reusable code templates | `_ready(app)`, `def function():`, `try/except` |
| `[v]` | **Variable** | Injected runtime variables | `app`, `state` |

---

## 🎯 Context-Aware Dot Completion

HomiCraft's autocompletion engine analyzes what you are typing before the dot (`.`):

### 1. `app.` Dot Completion
When you type `app.` in any script, HomiCraft automatically inspects your active scene hierarchy and lists all widgets currently present in your scene:

```python
app.
    ├── [w] btn_increment
    ├── [w] btn_decrement
    ├── [w] lbl_counter
    ├── [w] slider_scale
    ├── [v] state
    └── [f] close()
```
You never have to guess or remember what you named a button in the visual canvas!

### 2. Widget Dot Completion (`<widget_id>.`)
When you type a dot after any widget name (for example, `button_1.` or `lbl_counter.`), the completion engine displays:
* Pythonic properties: `text`, `value`, `min`, `max`, `enabled`, `visible`, `checked`, `placeholder`, `style`, `x`, `y`, `width`, `height`.
* PySide6 methods: `click()`, `setFocus()`, `clear()`, `selectAll()`, `raw_widget`.

---

## ⌨️ Keyboard Shortcuts for Autocompletion

* **`Ctrl + Space`**: Force the autocompletion popup to appear at the current cursor position.
* **`Tab` or `Enter`**: Insert the currently highlighted completion into your code.
* **`Up` / `Down` Arrow Keys**: Navigate through the suggestions list.
* **`Escape`**: Dismiss the completion popup.

---

## 🔄 Real-Time Scene Tree Synchronization

The autocompletion engine is deeply integrated with the visual canvas. Whenever you:
* Add a new widget from the palette,
* Duplicate an existing widget (`Ctrl + D`),
* Rename a Node ID in the Inspector, or
* Delete a widget (`Delete`),

HomiCraft updates the autocompletion symbol table in the background. The new node IDs and updated names become available in code suggestions immediately without restarting the editor!
