# 🎨 Chapter 7: Catppuccin Theming & Custom UI Styling

HomiCraft is designed with modern aesthetics at its core. It features the official **Catppuccin** color palette suite with rounded corner styling inspired by [catppuccin.com](https://catppuccin.com/palette/).

---

## 🌈 The Four Catppuccin Themes

HomiCraft includes all four official Catppuccin flavors:

| Theme Name | Tone | Background (`Base`) | Foreground (`Text`) | Accent (`Lavender`) | Best For |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **🌿 Mocha** | Deep Dark | `#1e1e2e` | `#cdd6f4` | `#b4befe` | Late-night coding, maximum contrast |
| **☕ Macchiato** | Medium Dark | `#24273a` | `#cad3f5` | `#b7bdf8` | Balanced dark mode with rich saturation |
| **🍨 Frappé** | Soft Pastel | `#303446` | `#c6d0f5` | `#babbf1` | Low eye-strain, softer dark palette |
| **🥛 Latte** | Crisp Light | `#eff1f5` | `#4c4f69` | `#7287fd` | Daytime working, bright environments |

---

## 🎛️ Live Theme Switching & UI Scaling

You can switch the entire application's theme instantly from the **`🎨 Theme`** selector in the main toolbar or via the **`⚙️ Settings`** window (`Ctrl+,`):
* All docks, tabs, buttons, scrollbars, and panels update immediately.
* The built-in **Code Editor** instantly reconfigures its syntax highlighting colors (keywords, strings, comments, numbers) to match the selected palette.
* The selected theme and UI scale are automatically saved in your user preferences (`%APPDATA%\HomiCraft\Settings.ini`) and restored the next time you open HomiCraft!

### 🔍 Display & Text Scaling (Windows Scale Equivalent)
HomiCraft includes dynamic UI scaling from **50% to 250%**:
* Proportional scaling of all application fonts, button paddings, tab sizes, dock titlebars, input fields, and margins.
* Ideal for multi-DPI setups (e.g. 100% on 1080p, 150% on 1440p, 200% on 4K).
* Can be tweaked live via **`⚙️ Settings` ➔ Display & Scaling** with real-time preview!

---

## 🔘 Rounded Modern UI Aesthetic

In accordance with modern interface design standards, all HomiCraft UI elements feature soft, rounded corners and generous padding:
* **Buttons**: Rounded with `8px` to `10px` border radius, subtle hover elevation, and pressed feedback.
* **Input Fields**: Soft borders, rounded pill corners, and glowing focus borders.
* **Docks & Panels**: Clean 1px separator borders with rounded tab corners.
* **Autocompletion Popup**: Floating card layout with `8px` rounded corners and category badges.

---

## 🖌️ Custom CSS / QSS Styling Per Widget

Every widget in HomiCraft can be customized with CSS (Qt Style Sheets) directly from the **Property Inspector**. Changes are rendered live on the canvas and in the exported executable.

### 1. Custom Button Styles
```css
/* Neon Purple Pill Button */
QPushButton {
    background-color: #cba6f7;
    color: #11111b;
    border-radius: 12px;
    font-weight: bold;
    padding: 6px 16px;
    border: none;
}
QPushButton:hover {
    background-color: #b4befe;
}
QPushButton:pressed {
    background-color: #89b4fa;
}
```

### 2. Sleek Modern Card Panel
```css
/* Glassmorphism / Frosted Card */
QFrame {
    background-color: rgba(30, 30, 46, 0.7);
    border: 1px solid #45475a;
    border-radius: 14px;
}
```

### 3. Styled Header Label
```css
/* Gradient Header Label */
QLabel {
    color: #89dceb;
    font-size: 20px;
    font-weight: bold;
    font-family: 'Segoe UI', sans-serif;
}
```

### 4. Rounded Search Input Field
```css
/* Pill Search Box */
QLineEdit {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 16px;
    padding: 4px 12px;
}
QLineEdit:focus {
    border: 1px solid #b4befe;
}
```

---

## 💡 Dynamic Styling in Python

You can also change the styling of any widget dynamically from your Python scripts using the `.style` property:

```python
def _on_btn_error_clicked(app):
    # Flash button red
    app.btn_submit.style = "background-color: #f38ba8; color: #11111b; border-radius: 8px;"
    app.lbl_status.text = "Invalid credentials!"

def _on_input_name_text_changed(text, app):
    if len(text) > 3:
        # Green border when valid
        app.input_name.style = "border: 2px solid #a6e3a1; border-radius: 6px;"
    else:
        # Red border when invalid
        app.input_name.style = "border: 2px solid #f38ba8; border-radius: 6px;"
```
