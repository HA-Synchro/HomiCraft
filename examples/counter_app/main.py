"""
HomiCraft Demo Application Script (main.py)
Notice how similar this is to GDScript attached to a Godot scene root!
"""

def _ready(app):
    """Called when the application first starts, identical to Godot's _ready()."""
    app.state["count"] = 0
    print("[HomiCraft] Application initialized successfully!")


def _get_step(app) -> int:
    try:
        return int(app.input_step.text())
    except ValueError:
        return 1


def on_increment(app):
    step = _get_step(app)
    app.state["count"] += step
    app.lbl_counter.setText(str(app.state["count"]))


def on_decrement(app):
    step = _get_step(app)
    app.state["count"] -= step
    app.lbl_counter.setText(str(app.state["count"]))


def on_reset(app):
    app.state["count"] = 0
    app.lbl_counter.setText("0")


def on_slider_changed(app, value):
    app.lbl_slider_val.setText(f"Adjustment Slider: {value}")


def on_lock_toggled(app, is_checked):
    # Enable or disable the counter buttons
    app.btn_inc.setEnabled(not is_checked)
    app.btn_dec.setEnabled(not is_checked)
    app.btn_reset.setEnabled(not is_checked)
    app.input_step.setEnabled(not is_checked)
