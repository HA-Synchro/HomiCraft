"""
HomiCraft Hierarchy Tree Dock
Displays the Scene Tree of widgets, matching Godot's Scene dock.
Supports selecting, renaming, deleting, and DRAGGING nodes into the Script Editor
to automatically generate object references!
"""

from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Signal, Qt, QMimeData
from core.schema import WidgetNode


class HierarchyTreeWidget(QTreeWidget):
    """Draggable Scene Tree (Godot style). Allows dragging nodes directly into scripts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)

    def mimeData(self, items):
        mime = QMimeData()
        if items:
            node_id = items[0].data(0, Qt.ItemDataRole.UserRole)
            # Default text representation
            mime.setText(f"app.{node_id}")
            # Specific node ID mime data
            mime.setData("application/x-homi-node-id", str(node_id).encode("utf-8"))
        return mime


class HierarchyDock(QWidget):
    node_selected = Signal(str)          # Emits node_id
    node_delete_requested = Signal(str)  # Emits node_id to delete

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        header = QLabel("🌳 Scene Hierarchy")
        header.setStyleSheet("font-weight: bold; font-size: 13px; color: #4ecdc4; padding: 4px;")
        layout.addWidget(header)

        self.tree = HierarchyTreeWidget(self)
        self.tree.setHeaderLabels(["Node ID", "Type"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: #1e1e24;
                color: #e0e0e0;
                border: 1px solid #333340;
                border-radius: 4px;
            }
            QTreeWidget::item:selected {
                background-color: #2e4a46;
                color: #ffffff;
            }
        """)
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.tree)

        btn_layout = QHBoxLayout()
        self.btn_delete = QPushButton("🗑️ Delete Node")
        self.btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #5c2020;
                color: white;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #8c2828;
            }
        """)
        self.btn_delete.clicked.connect(self._on_delete_clicked)
        btn_layout.addWidget(self.btn_delete)
        layout.addLayout(btn_layout)

    def populate(self, root_node: WidgetNode, active_node_id: Optional[str] = None) -> None:
        self.tree.blockSignals(True)
        self.tree.clear()

        root_item = QTreeWidgetItem(self.tree, [root_node.id, root_node.type])
        root_item.setData(0, Qt.ItemDataRole.UserRole, root_node.id)

        for child in root_node.children:
            self._add_tree_node(root_item, child)

        root_item.setExpanded(True)
        self.tree.blockSignals(False)

        if active_node_id:
            self.select_node(active_node_id)

    def _add_tree_node(self, parent_item: QTreeWidgetItem, node: WidgetNode) -> None:
        item = QTreeWidgetItem(parent_item, [node.id, node.type])
        item.setData(0, Qt.ItemDataRole.UserRole, node.id)
        for child in node.children:
            self._add_tree_node(item, child)
        item.setExpanded(True)

    def select_node(self, node_id: str) -> None:
        self.tree.blockSignals(True)
        self._find_and_select(self.tree.invisibleRootItem(), node_id)
        self.tree.blockSignals(False)

    def _find_and_select(self, item: QTreeWidgetItem, target_id: str) -> bool:
        for i in range(item.childCount()):
            child = item.child(i)
            if child.data(0, Qt.ItemDataRole.UserRole) == target_id:
                self.tree.setCurrentItem(child)
                return True
            if self._find_and_select(child, target_id):
                return True
        return False

    def _on_selection_changed(self) -> None:
        items = self.tree.selectedItems()
        if items:
            node_id = items[0].data(0, Qt.ItemDataRole.UserRole)
            self.node_selected.emit(node_id)

    def _on_delete_clicked(self) -> None:
        items = self.tree.selectedItems()
        if items:
            node_id = items[0].data(0, Qt.ItemDataRole.UserRole)
            self.node_delete_requested.emit(node_id)
