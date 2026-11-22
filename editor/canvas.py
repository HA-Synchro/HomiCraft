"""
HomiCraft Visual Designer Canvas
Provides an interactive 2D design surface where widgets can be clicked,
dragged, resized, duplicated (Ctrl+D), deleted, and visually arranged.
Supports dragging .py scripts directly onto widgets to attach scripts (Godot style).
"""

import os
from typing import Optional, Callable, Dict, List
from PySide6.QtWidgets import QWidget, QFrame
from PySide6.QtCore import Qt, QPoint, QRect, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QMouseEvent, QKeyEvent, QDragEnterEvent, QDropEvent

from core.schema import WidgetNode
from core.registry import WIDGET_REGISTRY, apply_widget_properties


class CanvasOverlay(QWidget):
    """Transparent overlay on top of canvas for drawing selection handles and grid."""

    def __init__(self, parent_canvas: 'DesignCanvas'):
        super().__init__(parent_canvas)
        self.canvas = parent_canvas
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        # Draw light grid dots/lines
        if self.canvas.grid_enabled:
            grid_size = self.canvas.grid_size
            painter.setPen(QPen(QColor(50, 50, 62), 1, Qt.PenStyle.DotLine))
            w = self.width()
            h = self.height()
            for x in range(0, w, grid_size):
                painter.drawLine(x, 0, x, h)
            for y in range(0, h, grid_size):
                painter.drawLine(0, y, w, y)

        # Draw selection rectangle and handles for active widget
        selected = self.canvas.selected_node
        if selected and selected.id != "root_window" and selected.id in self.canvas.widget_instances:
            w_inst = self.canvas.widget_instances[selected.id]
            rect = w_inst.geometry()

            # Selection border (cyan)
            pen = QPen(QColor(78, 205, 196), 2, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(rect)

            # Draw 4 corner handles
            handle_size = 6
            painter.setBrush(QColor(255, 255, 255))
            painter.setPen(QColor(30, 30, 35))
            corners = [
                rect.topLeft(),
                rect.topRight(),
                rect.bottomLeft(),
                rect.bottomRight()
            ]
            for pt in corners:
                painter.drawRect(
                    pt.x() - handle_size // 2,
                    pt.y() - handle_size // 2,
                    handle_size,
                    handle_size
                )


class DesignCanvas(QFrame):
    """The 2D visual viewport where widgets are placed and manipulated."""

    node_selected = Signal(object)              # Emits selected WidgetNode
    node_modified = Signal(object)              # Emits modified WidgetNode (after move/resize)
    node_delete_requested = Signal(str)         # Emits node_id to delete
    node_duplicate_requested = Signal(str)      # Emits node_id to duplicate
    script_dropped_on_node = Signal(str, str, str)  # (node_id, filename, full_path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setStyleSheet("background-color: #1e1e24; border: 1px solid #333340;")
        self.setMouseTracking(True)
        self.setAcceptDrops(True)

        self.root_node: Optional[WidgetNode] = None
        self.selected_node: Optional[WidgetNode] = None
        self.widget_instances: Dict[str, QWidget] = {}

        self.grid_enabled = True
        self.grid_size = 10

        # Dragging & Resizing state
        self._is_dragging = False
        self._is_resizing = False
        self._drag_start_pos = QPoint()
        self._initial_geom = QRect()

        self.overlay = CanvasOverlay(self)
        self.overlay.setGeometry(self.rect())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.overlay.setGeometry(self.rect())

    def set_scene(self, root: WidgetNode, win_width: int = 600, win_height: int = 400) -> None:
        self.root_node = root
        self.selected_node = None
        self.setFixedSize(win_width, win_height)
        self.rebuild_visuals()

    def rebuild_visuals(self) -> None:
        for w in self.widget_instances.values():
            w.deleteLater()
        self.widget_instances.clear()

        if not self.root_node:
            self.overlay.update()
            return

        if "styleSheet" in self.root_node.properties:
            self.setStyleSheet(self.root_node.properties["styleSheet"])
        else:
            self.setStyleSheet("background-color: #1e1e24; border: 1px solid #333340;")

        for child in self.root_node.children:
            self._create_visual_widget(child)

        self.overlay.raise_()
        self.overlay.update()

    def _create_visual_widget(self, node: WidgetNode) -> None:
        meta = WIDGET_REGISTRY.get(node.type)
        if not meta:
            return

        instance = meta.qt_class(self)
        if node.type == "Slider":
            instance.setOrientation(Qt.Orientation.Horizontal)

        instance.setGeometry(node.x, node.y, node.width, node.height)
        props = dict(meta.default_props)
        props.update(node.properties)
        apply_widget_properties(instance, props)
        
        instance.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        instance.show()

        self.widget_instances[node.id] = instance

    def select_node_by_id(self, node_id: str) -> None:
        if not self.root_node:
            return
        if node_id == self.root_node.id:
            self.selected_node = self.root_node
            self.overlay.update()
            self.node_selected.emit(self.root_node)
            return

        found = self._find_node(self.root_node, node_id)
        if found:
            self.selected_node = found
            self.overlay.update()
            self.node_selected.emit(found)

    def _find_node(self, current: WidgetNode, target_id: str) -> Optional[WidgetNode]:
        if current.id == target_id:
            return current
        for child in current.children:
            res = self._find_node(child, target_id)
            if res:
                return res
        return None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            clicked_node = None

            if self.root_node:
                for child in reversed(self.root_node.children):
                    rect = QRect(child.x, child.y, child.width, child.height)
                    if rect.contains(pos):
                        clicked_node = child
                        break

            if not clicked_node and self.root_node:
                clicked_node = self.root_node

            self.selected_node = clicked_node
            self.overlay.update()
            self.node_selected.emit(clicked_node)

            if clicked_node and clicked_node.id != "root_window":
                self._is_dragging = True
                self._drag_start_pos = pos
                self._initial_geom = QRect(clicked_node.x, clicked_node.y, clicked_node.width, clicked_node.height)
                
                br = self._initial_geom.bottomRight()
                if (pos - br).manhattanLength() < 14:
                    self._is_resizing = True
                    self._is_dragging = False

        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.position().toPoint()
        delta = pos - self._drag_start_pos

        if self._is_dragging and self.selected_node and self.selected_node.id != "root_window":
            new_x = self._initial_geom.x() + delta.x()
            new_y = self._initial_geom.y() + delta.y()

            if self.grid_enabled:
                new_x = round(new_x / self.grid_size) * self.grid_size
                new_y = round(new_y / self.grid_size) * self.grid_size

            new_x = max(0, min(new_x, self.width() - self.selected_node.width))
            new_y = max(0, min(new_y, self.height() - self.selected_node.height))

            self.selected_node.x = new_x
            self.selected_node.y = new_y

            inst = self.widget_instances.get(self.selected_node.id)
            if inst:
                inst.move(new_x, new_y)

            self.overlay.update()
            self.node_modified.emit(self.selected_node)

        elif self._is_resizing and self.selected_node and self.selected_node.id != "root_window":
            new_w = max(20, self._initial_geom.width() + delta.x())
            new_h = max(15, self._initial_geom.height() + delta.y())

            if self.grid_enabled:
                new_w = round(new_w / self.grid_size) * self.grid_size
                new_h = round(new_h / self.grid_size) * self.grid_size

            self.selected_node.width = new_w
            self.selected_node.height = new_h

            inst = self.widget_instances.get(self.selected_node.id)
            if inst:
                inst.resize(new_w, new_h)

            self.overlay.update()
            self.node_modified.emit(self.selected_node)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._is_dragging or self._is_resizing:
            self._is_dragging = False
            self._is_resizing = False
            if self.selected_node:
                self.node_modified.emit(self.selected_node)
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        modifiers = event.modifiers()

        if key in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            if self.selected_node and self.selected_node.id != "root_window":
                self.node_delete_requested.emit(self.selected_node.id)
                event.accept()
                return

        if key == Qt.Key.Key_D and (modifiers & Qt.KeyboardModifier.ControlModifier):
            if self.selected_node and self.selected_node.id != "root_window":
                self.node_duplicate_requested.emit(self.selected_node.id)
                event.accept()
                return

        step = 1 if (modifiers & Qt.KeyboardModifier.ShiftModifier) else self.grid_size
        if self.selected_node and self.selected_node.id != "root_window":
            if key == Qt.Key.Key_Left:
                self.selected_node.x = max(0, self.selected_node.x - step)
            elif key == Qt.Key.Key_Right:
                self.selected_node.x = min(self.width() - self.selected_node.width, self.selected_node.x + step)
            elif key == Qt.Key.Key_Up:
                self.selected_node.y = max(0, self.selected_node.y - step)
            elif key == Qt.Key.Key_Down:
                self.selected_node.y = min(self.height() - self.selected_node.height, self.selected_node.y + step)
            else:
                super().keyPressEvent(event)
                return

            inst = self.widget_instances.get(self.selected_node.id)
            if inst:
                inst.move(self.selected_node.x, self.selected_node.y)

            self.overlay.update()
            self.node_modified.emit(self.selected_node)
            event.accept()
            return

        super().keyPressEvent(event)

    # DRAG & DROP PYTHON SCRIPTS ONTO CANVAS WIDGETS (Godot style)
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().endswith(".py"):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls() and self.root_node:
            pos = event.position().toPoint()
            # Find widget under drop location
            target_node = None
            for child in reversed(self.root_node.children):
                rect = QRect(child.x, child.y, child.width, child.height)
                if rect.contains(pos):
                    target_node = child
                    break

            if target_node:
                for url in event.mimeData().urls():
                    fpath = url.toLocalFile()
                    if fpath.endswith(".py"):
                        fname = os.path.basename(fpath)
                        target_node.script = fname
                        event.acceptProposedAction()
                        self.select_node_by_id(target_node.id)
                        self.script_dropped_on_node.emit(target_node.id, fname, fpath)
                        return
        event.ignore()
