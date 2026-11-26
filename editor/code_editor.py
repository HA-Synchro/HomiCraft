"""
HomiCraft Embedded Python Script Editor & Multi-Script Workspace
Provides multi-tab script editing with Catppuccin syntax highlighting,
line numbers, closable tabs, auto-indentation on Enter, smart Tab/Backspace,
drag-and-drop node references from the Scene Tree, and rich IDE code autocompletion.
"""

import os
import re
import ast
from typing import Dict, List, Optional, Tuple, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPlainTextEdit,
    QTextEdit, QPushButton, QLabel, QCompleter, QListView, QAbstractItemView,
    QSplitter, QTreeWidget, QTreeWidgetItem, QMenu, QDialog, QFormLayout,
    QLineEdit, QComboBox, QRadioButton, QButtonGroup, QFrame, QToolButton,
    QMessageBox
)
from PySide6.QtGui import (
    QFont, QTextCursor, QColor, QPainter, QSyntaxHighlighter,
    QTextCharFormat, QKeyEvent, QDragEnterEvent, QDragMoveEvent, QDropEvent,
    QStandardItemModel, QStandardItem, QIcon, QPixmap
)
from PySide6.QtCore import Qt, QRect, QSize, QRegularExpression, QTimer, Signal

from editor.theme import CATPPUCCIN_PALETTES


def make_completion_icon(char: str, color_hex: str) -> QIcon:
    """Generates a modern rounded category badge icon for code completion."""
    pix = QPixmap(18, 18)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor(color_hex))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(1, 1, 16, 16, 4, 4)
    painter.setPen(QColor("#11111b"))
    font = QFont("Consolas", 9, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, char)
    painter.end()
    return QIcon(pix)


class PythonSyntaxHighlighter(QSyntaxHighlighter):
    """Catppuccin theme-aware syntax highlighter for Python code."""

    def __init__(self, document, flavor: str = "Mocha"):
        super().__init__(document)
        self.rules = []
        self.flavor = flavor
        self._build_rules()

    def set_flavor(self, flavor: str):
        self.flavor = flavor
        self._build_rules()
        self.rehighlight()

    def _build_rules(self):
        self.rules.clear()
        pal = CATPPUCCIN_PALETTES.get(self.flavor, CATPPUCCIN_PALETTES["Mocha"])

        # Keywords (Mauve)
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(pal["mauve"]))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = [
            "def", "class", "return", "if", "else", "elif", "for", "while",
            "try", "except", "finally", "import", "from", "as", "pass",
            "break", "continue", "in", "is", "not", "and", "or", "lambda",
            "global", "nonlocal", "raise", "yield", "with", "assert", "async", "await"
        ]
        for kw in keywords:
            pattern = QRegularExpression(rf"\b{kw}\b")
            self.rules.append((pattern, keyword_format))

        # Built-ins and constants (Pink / Red)
        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor(pal["pink"]))
        builtin_format.setFontWeight(QFont.Weight.Bold)
        builtins = ["True", "False", "None", "self", "app", "print", "len", "range", "int", "str", "float", "bool", "dict", "list"]
        for b in builtins:
            pattern = QRegularExpression(rf"\b{b}\b")
            self.rules.append((pattern, builtin_format))

        # Function definitions (Blue)
        func_format = QTextCharFormat()
        func_format.setForeground(QColor(pal["blue"]))
        func_format.setFontWeight(QFont.Weight.Bold)
        self.rules.append((QRegularExpression(r"\bdef\s+([A-Za-z_][A-Za-z0-9_]*)"), func_format))

        # Numbers (Peach)
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(pal["peach"]))
        self.rules.append((QRegularExpression(r"\b[0-9]+(\.[0-9]+)?\b"), number_format))

        # Strings (Green)
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(pal["green"]))
        self.rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        self.rules.append((QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format))

        # Comments (Overlay0)
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(pal["overlay0"]))
        comment_format.setFontItalic(True)
        self.rules.append((QRegularExpression(r"#.*"), comment_format))

    def highlightBlock(self, text: str):
        for pattern, fmt in self.rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)


class LineNumberArea(QWidget):
    def __init__(self, editor: 'ScriptEditorWidget'):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class ScriptEditorWidget(QPlainTextEdit):
    def __init__(self, parent=None, flavor: str = "Mocha"):
        super().__init__(parent)
        self.flavor = flavor
        self.line_number_area = LineNumberArea(self)
        self.setAcceptDrops(True)

        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        self.setTabStopDistance(32)

        self.highlighter = PythonSyntaxHighlighter(self.document(), flavor)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        # Autocompletion setup
        self.known_nodes: List[str] = []
        self._init_autocompletion()

        self.apply_theme(flavor)
        self.update_line_number_area_width(0)
        self.highlight_current_line()

    def _init_autocompletion(self):
        self.completer = QCompleter(self)
        self.completer.setWidget(self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.activated.connect(self.insert_completion)

        self._build_completion_models()
        self.completer.setModel(self.general_model)

    def _build_completion_models(self):
        pal = CATPPUCCIN_PALETTES.get(self.flavor, CATPPUCCIN_PALETTES["Mocha"])

        icon_kw = make_completion_icon("K", pal.get("mauve", "#cba6f7"))
        icon_fn = make_completion_icon("f", pal.get("blue", "#89b4fa"))
        icon_cl = make_completion_icon("C", pal.get("yellow", "#f9e2af"))
        icon_ex = make_completion_icon("E", pal.get("peach", "#fab387"))
        icon_wd = make_completion_icon("w", pal.get("green", "#a6e3a1"))
        icon_pr = make_completion_icon("p", pal.get("teal", "#94e2d5"))
        icon_sn = make_completion_icon("s", pal.get("flamingo", "#f2cdcd"))
        icon_vr = make_completion_icon("v", pal.get("lavender", "#b4befe"))

        # 1. GENERAL SCOPE MODEL
        self.general_model = QStandardItemModel(self)

        keywords = [
            "def", "class", "import", "from", "as", "return", "pass", "if", "else", "elif",
            "for", "while", "break", "continue", "in", "is", "not", "and", "or", "lambda",
            "try", "except", "finally", "raise", "with", "assert", "global", "nonlocal",
            "yield", "async", "await", "True", "False", "None"
        ]
        for kw in keywords:
            self.general_model.appendRow(QStandardItem(icon_kw, kw))

        builtins_fn = [
            "print", "len", "range", "enumerate", "zip", "open", "type", "isinstance",
            "hasattr", "getattr", "setattr", "delattr", "min", "max", "sum", "abs",
            "round", "all", "any", "filter", "map", "sorted", "reversed", "super",
            "property", "input", "help", "dir", "id", "__import__"
        ]
        for fn in builtins_fn:
            self.general_model.appendRow(QStandardItem(icon_fn, fn))

        builtin_types = ["str", "int", "float", "bool", "list", "dict", "set", "tuple", "object", "bytes", "NotImplemented"]
        for bt in builtin_types:
            self.general_model.appendRow(QStandardItem(icon_cl, bt))

        exceptions = [
            "ImportError", "ImportWarning", "ValueError", "TypeError", "KeyError",
            "IndexError", "AttributeError", "FileNotFoundError", "ZeroDivisionError",
            "Exception", "BaseException", "NotImplementedError", "RuntimeError",
            "StopIteration", "KeyboardInterrupt", "LookupError", "NameError",
            "OSError", "SyntaxError", "TimeoutError", "RecursionError"
        ]
        for ex in exceptions:
            self.general_model.appendRow(QStandardItem(icon_ex, ex))

        vars_special = ["app", "self", "_ready", "__name__", "__file__", "__doc__"]
        for v in vars_special:
            self.general_model.appendRow(QStandardItem(icon_vr, v))

        snippets = [
            "def _ready(app):",
            "def on_clicked(app):",
            "if __name__ == '__main__':",
            "for item in items:",
            "try:\n    pass\nexcept Exception as e:\n    pass"
        ]
        for sn in snippets:
            self.general_model.appendRow(QStandardItem(icon_sn, sn))

        for node_id in self.known_nodes:
            self.general_model.appendRow(QStandardItem(icon_wd, node_id))

        # 2. APP CONTEXT MODEL (after "app.")
        self.app_model = QStandardItemModel(self)
        self.app_model.appendRow(QStandardItem(icon_fn, "get_widget"))
        self.app_model.appendRow(QStandardItem(icon_fn, "close"))
        for node_id in self.known_nodes:
            self.app_model.appendRow(QStandardItem(icon_wd, node_id))

        # 3. WIDGET CONTEXT MODEL (after "widget.")
        self.widget_model = QStandardItemModel(self)
        widget_props = [
            ("text", icon_pr),
            ("enabled", icon_pr),
            ("visible", icon_pr),
            ("value", icon_pr),
            ("min_value", icon_pr),
            ("max_value", icon_pr),
            ("step", icon_pr),
            ("style", icon_pr),
            ("x", icon_pr),
            ("y", icon_pr),
            ("width", icon_pr),
            ("height", icon_pr),
            ("click()", icon_fn),
            ("show()", icon_fn),
            ("hide()", icon_fn),
            ("setFocus()", icon_fn),
            ("update()", icon_fn),
            ("setStyleSheet()", icon_fn),
        ]
        for name, ic in widget_props:
            self.widget_model.appendRow(QStandardItem(ic, name))

    def set_known_nodes(self, node_ids: List[str]):
        """Updates known scene widget IDs and refreshes autocomplete models."""
        self.known_nodes = list(node_ids)
        self._build_completion_models()

    def apply_theme(self, flavor: str):
        self.flavor = flavor
        pal = CATPPUCCIN_PALETTES.get(flavor, CATPPUCCIN_PALETTES["Mocha"])
        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {pal["base"]};
                color: {pal["text"]};
                border: 1px solid {pal["surface0"]};
                border-radius: 8px;
                selection-background-color: {pal["surface2"]};
            }}
        """)
        self.highlighter.set_flavor(flavor)
        self.highlight_current_line()
        self.line_number_area.update()

        # Style completion popup
        if hasattr(self, "completer") and self.completer:
            popup = self.completer.popup()
            popup.setStyleSheet(f"""
                QListView {{
                    background-color: {pal["mantle"]};
                    color: {pal["text"]};
                    border: 1px solid {pal["surface1"]};
                    border-radius: 8px;
                    padding: 4px;
                    font-family: Consolas, monospace;
                    font-size: 12px;
                    outline: none;
                }}
                QListView::item {{
                    padding: 4px 8px;
                    border-radius: 5px;
                    min-height: 22px;
                }}
                QListView::item:selected {{
                    background-color: {pal["surface0"]};
                    color: {pal["blue"]};
                    font-weight: bold;
                }}
                QListView::item:hover {{
                    background-color: {pal["surface1"]};
                }}
                QScrollBar:vertical {{
                    background: transparent;
                    width: 8px;
                    margin: 2px;
                }}
                QScrollBar::handle:vertical {{
                    background: {pal["surface2"]};
                    border-radius: 4px;
                    min-height: 20px;
                }}
            """)
            self._build_completion_models()

    def line_number_area_width(self):
        digits = 1
        max_b = max(1, self.blockCount())
        while max_b >= 10:
            max_b //= 10
            digits += 1
        space = 14 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        pal = CATPPUCCIN_PALETTES.get(self.flavor, CATPPUCCIN_PALETTES["Mocha"])
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(pal["mantle"]))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor(pal["overlay1"]))
                painter.drawText(0, top, self.line_number_area.width() - 8, self.fontMetrics().height(),
                                 Qt.AlignmentFlag.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def highlight_current_line(self):
        pal = CATPPUCCIN_PALETTES.get(self.flavor, CATPPUCCIN_PALETTES["Mocha"])
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor(pal["surface0"]))
            selection.format.setProperty(0x100000, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

    def get_context_before_cursor(self) -> Tuple[str, str]:
        """Extracts (object_identifier, current_word_prefix) right before the cursor."""
        cursor = self.textCursor()
        block = cursor.block().text()
        pos = cursor.positionInBlock()
        line_up_to_cursor = block[:pos]

        # Dot-completion: e.g. "app.btn" or "button_1.text"
        match_dot = re.search(r'([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z0-9_]*)$', line_up_to_cursor)
        if match_dot:
            return match_dot.group(1), match_dot.group(2)

        # Standard word completion: e.g. "imp", "de"
        match_word = re.search(r'([A-Za-z_][A-Za-z0-9_]*)$', line_up_to_cursor)
        if match_word:
            return '', match_word.group(1)

        return '', ''

    def insert_completion(self, completion: str):
        """Inserts selected completion string, replacing current word prefix."""
        if not self.completer:
            return
        tc = self.textCursor()
        obj_name, prefix = self.get_context_before_cursor()

        if prefix:
            tc.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor, len(prefix))

        tc.insertText(completion)
        self.setTextCursor(tc)

    def trigger_completion(self, force: bool = False):
        """Evaluates cursor context and pops up autocompletion suggestions."""
        if not self.completer:
            return

        obj_name, prefix = self.get_context_before_cursor()

        # Select appropriate model based on dot context
        if obj_name == "app":
            self.completer.setModel(self.app_model)
        elif obj_name in self.known_nodes or obj_name.endswith(("_btn", "_lbl", "_slider", "button", "label", "slider", "proxy")):
            self.completer.setModel(self.widget_model)
        else:
            self.completer.setModel(self.general_model)

        # Should show if explicitly forced (Ctrl+Space), prefix typed >= 1, or right after dot
        should_show = force or (len(prefix) >= 1) or (obj_name and len(prefix) == 0)

        if should_show:
            self.completer.setCompletionPrefix(prefix)
            m = self.completer.completionModel()
            if m.rowCount() > 0:
                self.completer.popup().setCurrentIndex(m.index(0, 0))
                cr = self.cursorRect()
                popup_width = max(260, self.completer.popup().sizeHintForColumn(0) + 45)
                cr.setWidth(min(420, popup_width))
                self.completer.complete(cr)
            else:
                self.completer.popup().hide()
        else:
            if self.completer.popup().isVisible():
                self.completer.popup().hide()

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()

        # 1. Autocompletion navigation & selection
        if self.completer and self.completer.popup().isVisible():
            if key in (Qt.Key.Key_Enter, Qt.Key.Key_Return, Qt.Key.Key_Tab):
                index = self.completer.popup().currentIndex()
                if not index.isValid():
                    index = self.completer.completionModel().index(0, 0)
                if index.isValid():
                    completion = index.data(Qt.ItemDataRole.DisplayRole)
                    self.insert_completion(completion)
                self.completer.popup().hide()
                event.accept()
                return

            if key == Qt.Key.Key_Escape:
                self.completer.popup().hide()
                event.accept()
                return

            if key in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_PageUp, Qt.Key.Key_PageDown):
                self.completer.popup().keyPressEvent(event)
                event.accept()
                return

        # 2. Manual trigger shortcut: Ctrl+Space
        is_shortcut = bool((event.modifiers() & Qt.KeyboardModifier.ControlModifier) and key == Qt.Key.Key_Space)
        if is_shortcut:
            self.trigger_completion(force=True)
            event.accept()
            return

        cursor = self.textCursor()

        # 3. ENTER / RETURN KEY: Auto-Indentation on Enter!
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            block = cursor.block()
            line_text = block.text()
            col = cursor.positionInBlock()
            line_up_to_cursor = line_text[:col]

            stripped = line_up_to_cursor.lstrip()
            indent = line_up_to_cursor[:len(line_up_to_cursor) - len(stripped)]

            code_no_comments = stripped.split('#')[0].rstrip()
            if code_no_comments.endswith(':'):
                indent += "    "

            cursor.insertText("\n" + indent)
            self.setTextCursor(cursor)
            self.ensureCursorVisible()
            if self.completer and self.completer.popup().isVisible():
                self.completer.popup().hide()
            event.accept()
            return

        # 4. TAB KEY: Insert 4 spaces or indent selection
        if key == Qt.Key.Key_Tab:
            if cursor.hasSelection():
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
                cursor.setPosition(start)
                start_block = cursor.blockNumber()
                cursor.setPosition(end)
                end_block = cursor.blockNumber()

                cursor.beginEditBlock()
                for b_num in range(start_block, end_block + 1):
                    b = self.document().findBlockByNumber(b_num)
                    cur = QTextCursor(b)
                    cur.insertText("    ")
                cursor.endEditBlock()
            else:
                cursor.insertText("    ")
            event.accept()
            return

        # 5. BACKTAB (SHIFT+TAB): Un-indent by 4 spaces
        if key == Qt.Key.Key_Backtab:
            cursor.beginEditBlock()
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            cursor.setPosition(start)
            start_block = cursor.blockNumber()
            cursor.setPosition(end)
            end_block = cursor.blockNumber()

            for b_num in range(start_block, end_block + 1):
                b = self.document().findBlockByNumber(b_num)
                txt = b.text()
                cur = QTextCursor(b)
                if txt.startswith("    "):
                    cur.setPosition(b.position())
                    cur.setPosition(b.position() + 4, QTextCursor.MoveMode.KeepAnchor)
                    cur.removeSelectedText()
                elif txt.startswith(" "):
                    spaces = len(txt) - len(txt.lstrip())
                    to_remove = min(spaces, 4)
                    cur.setPosition(b.position())
                    cur.setPosition(b.position() + to_remove, QTextCursor.MoveMode.KeepAnchor)
                    cur.removeSelectedText()
            cursor.endEditBlock()
            event.accept()
            return

        # 6. BACKSPACE: Smart delete 4 spaces
        if key == Qt.Key.Key_Backspace and not cursor.hasSelection():
            col = cursor.positionInBlock()
            line_text = cursor.block().text()[:col]
            if len(line_text) >= 4 and line_text.endswith("    ") and not line_text.strip():
                cursor.setPosition(cursor.position() - 4, QTextCursor.MoveMode.KeepAnchor)
                cursor.removeSelectedText()
                event.accept()
                self.trigger_completion()
                return

        # Normal key processing
        super().keyPressEvent(event)

        # Trigger or update autocompletion after typing
        self.trigger_completion()

    # 7. DRAG & DROP NODES FROM SCENE TREE
    def dragEnterEvent(self, event: QDragEnterEvent):
        mime = event.mimeData()
        if mime.hasFormat("application/x-homi-node-id") or (mime.hasText() and mime.text().startswith("app.")):
            event.acceptProposedAction()
            return
        super().dragEnterEvent(event)

    def dragMoveEvent(self, event: QDragMoveEvent):
        mime = event.mimeData()
        if mime.hasFormat("application/x-homi-node-id") or (mime.hasText() and mime.text().startswith("app.")):
            cur = self.cursorForPosition(event.position().toPoint())
            self.setTextCursor(cur)
            event.acceptProposedAction()
            return
        super().dragMoveEvent(event)

    def dropEvent(self, event: QDropEvent):
        mime = event.mimeData()
        node_id = None
        if mime.hasFormat("application/x-homi-node-id"):
            node_id = mime.data("application/x-homi-node-id").data().decode("utf-8")
        elif mime.hasText() and mime.text().startswith("app."):
            node_id = mime.text()[4:]

        if node_id:
            cur = self.cursorForPosition(event.position().toPoint())
            line_text = cur.block().text()
            is_blank_line = not line_text.strip()
            ctrl_pressed = bool(event.modifiers() & Qt.KeyboardModifier.ControlModifier)

            if is_blank_line or ctrl_pressed:
                cur.insertText(f"{node_id} = app.{node_id}")
            else:
                cur.insertText(f"app.{node_id}")

            self.setTextCursor(cur)
            self.setFocus()
            event.acceptProposedAction()
            return

        super().dropEvent(event)

    def append_callback_scaffold(self, func_name: str, sig_name: str) -> None:
        code = self.toPlainText()
        if f"def {func_name}" in code:
            cursor = self.textCursor()
            pos = code.find(f"def {func_name}")
            cursor.setPosition(pos)
            self.setTextCursor(cursor)
            self.centerCursor()
            self.setFocus()
            return

        scaffold = f"\n\ndef {func_name}(app):\n    # TODO: Handle '{sig_name}' event\n    pass\n"
        if not code.endswith("\n"):
            scaffold = "\n" + scaffold

        self.appendPlainText(scaffold)
        self.moveCursor(QTextCursor.MoveOperation.End)
        self.setFocus()


def extract_script_members(code: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Extracts module variables, app.state assignments, and function definitions
    from Python script code using AST with regex fallback.
    """
    variables: List[Dict[str, Any]] = []
    functions: List[Dict[str, Any]] = []

    if not code.strip():
        return variables, functions

    try:
        tree = ast.parse(code)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        val_str = ""
                        try:
                            val_str = ast.unparse(node.value)
                        except Exception:
                            val_str = str(getattr(node.value, "value", ""))
                        variables.append({
                            "name": target.id,
                            "type": "global",
                            "value": val_str,
                            "lineno": getattr(node, "lineno", 1)
                        })
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name):
                    val_str = ""
                    if node.value:
                        try:
                            val_str = ast.unparse(node.value)
                        except Exception:
                            val_str = str(getattr(node.value, "value", ""))
                    t_str = ""
                    try:
                        t_str = ast.unparse(node.annotation)
                    except Exception:
                        t_str = ""
                    variables.append({
                        "name": node.target.id,
                        "type": t_str or "global",
                        "value": val_str,
                        "lineno": getattr(node, "lineno", 1)
                    })
            elif isinstance(node, ast.FunctionDef):
                params = [arg.arg for arg in node.args.args]
                functions.append({
                    "name": node.name,
                    "params": params,
                    "lineno": getattr(node, "lineno", 1)
                })
                # Check for app.state assignments inside functions
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Assign):
                        for tgt in sub.targets:
                            if isinstance(tgt, ast.Subscript):
                                if isinstance(tgt.value, ast.Attribute) and getattr(tgt.value, "attr", "") == "state":
                                    key_name = ""
                                    if isinstance(tgt.slice, ast.Constant):
                                        key_name = str(tgt.slice.value)
                                    if key_name:
                                        val_repr = ""
                                        try:
                                            val_repr = ast.unparse(sub.value)
                                        except Exception:
                                            val_repr = ""
                                        variables.append({
                                            "name": f"app.state['{key_name}']",
                                            "type": "state",
                                            "value": val_repr,
                                            "lineno": getattr(sub, "lineno", 1)
                                        })
    except Exception:
        pass

    if not variables and not functions:
        lines = code.splitlines()
        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            # Function def
            m_fn = re.match(r"^def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*?)\):", stripped)
            if m_fn:
                p_list = [p.strip() for p in m_fn.group(2).split(",") if p.strip()]
                functions.append({"name": m_fn.group(1), "params": p_list, "lineno": idx})
                continue
            # Top-level variable
            if not line.startswith(" ") and not line.startswith("\t"):
                m_var = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*(?::\s*([a-zA-Z_0-9\[\], ]+))?\s*=\s*(.*)", line)
                if m_var:
                    variables.append({
                        "name": m_var.group(1),
                        "type": m_var.group(2) or "global",
                        "value": m_var.group(3).strip(),
                        "lineno": idx
                    })
            # app.state
            m_st = re.search(r"app\.state\[['\"]([a-zA-Z_0-9]+)['\"]\]\s*=\s*(.*)", stripped)
            if m_st:
                variables.append({
                    "name": f"app.state['{m_st.group(1)}']",
                    "type": "state",
                    "value": m_st.group(2).strip(),
                    "lineno": idx
                })

    return variables, functions


class AddVariableDialog(QDialog):
    """Dialog for creating new script variables visually with scope and typing assistance."""
    def __init__(self, parent=None, flavor: str = "Mocha"):
        super().__init__(parent)
        self.setWindowTitle("Create Script Variable")
        self.resize(460, 370)

        pal = CATPPUCCIN_PALETTES.get(flavor, CATPPUCCIN_PALETTES["Mocha"])
        bg = pal["mantle"]
        surface = pal["surface0"]
        text_col = pal["text"]
        accent = pal["blue"]

        self.setStyleSheet(f"""
            QDialog {{ background-color: {bg}; color: {text_col}; }}
            QLabel {{ color: {text_col}; font-size: 12px; }}
            QLineEdit, QComboBox {{
                background-color: {surface};
                color: {text_col};
                border: 1px solid {pal['surface1']};
                border-radius: 6px;
                padding: 6px 10px;
                font-family: Consolas;
            }}
            QRadioButton {{ color: {text_col}; font-size: 12px; spacing: 6px; }}
            QPushButton {{
                background-color: {surface};
                color: {text_col};
                border: 1px solid {pal['surface1']};
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {pal['surface1']}; }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        header = QLabel("📊 <b>New Variable Definition</b>")
        header.setStyleSheet(f"font-size: 14px; color: {accent};")
        layout.addWidget(header)

        form = QFormLayout()
        form.setSpacing(10)

        # Variable Name
        self.inp_name = QLineEdit("text1")
        self.inp_name.setPlaceholderText("e.g. text1, counter, is_active")
        form.addRow("Variable Name:", self.inp_name)

        # Variable Type
        self.combo_type = QComboBox()
        self.combo_type.addItems(["str", "int", "float", "bool", "list", "dict", "Any"])
        self.combo_type.currentTextChanged.connect(self._on_type_changed)
        form.addRow("Type:", self.combo_type)

        # Initial Value
        self.inp_value = QLineEdit('"Nothing Here"')
        self.inp_value.setPlaceholderText('Initial expression, e.g. "Nothing Here", 0, True')
        form.addRow("Initial Value:", self.inp_value)

        layout.addLayout(form)

        # Scope selection
        scope_group = QFrame()
        scope_group.setStyleSheet(f"background-color: {surface}; border-radius: 6px; padding: 10px;")
        sg_layout = QVBoxLayout(scope_group)
        sg_layout.setSpacing(6)
        sg_layout.addWidget(QLabel("<b>Storage Scope:</b>"))

        self.btn_group = QButtonGroup(self)
        self.rb_global = QRadioButton("Module Variable (Global) — e.g. text1 = \"...\"")
        self.rb_global.setChecked(True)
        self.rb_state = QRadioButton("App State Variable — e.g. app.state[\"text1\"] = \"...\"")
        self.btn_group.addButton(self.rb_global, 1)
        self.btn_group.addButton(self.rb_state, 2)
        sg_layout.addWidget(self.rb_global)
        sg_layout.addWidget(self.rb_state)
        layout.addWidget(scope_group)

        # Informative Hint
        self.lbl_tip = QLabel(
            "💡 <b>Tip:</b> If using a <b>Module Variable</b>, any function modifying it "
            "must declare <code style='color:#a6e3a1;'>global var_name</code>.<br>"
            "If using <b>App State</b>, it is accessible across all callbacks via "
            "<code style='color:#89b4fa;'>app.state['var_name']</code> without needing global!"
        )
        self.lbl_tip.setWordWrap(True)
        self.lbl_tip.setStyleSheet(f"background-color: {surface}; padding: 8px; border-radius: 6px; font-size: 11px; color: {pal['subtext0']};")
        layout.addWidget(self.lbl_tip)

        layout.addStretch()

        # Action Buttons
        btn_box = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)

        self.btn_ok = QPushButton("➕ Insert Variable")
        self.btn_ok.setStyleSheet(f"background-color: {pal['green']}; color: #11111b; font-weight: bold;")
        self.btn_ok.clicked.connect(self._on_accept)

        btn_box.addStretch()
        btn_box.addWidget(btn_cancel)
        btn_box.addWidget(self.btn_ok)
        layout.addLayout(btn_box)

    def _on_type_changed(self, new_type: str):
        defaults = {
            "str": '""',
            "int": '0',
            "float": '0.0',
            "bool": 'True',
            "list": '[]',
            "dict": '{}',
            "Any": 'None'
        }
        self.inp_value.setText(defaults.get(new_type, '""'))

    def _on_accept(self):
        name = self.inp_name.text().strip()
        if not name or not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name):
            QMessageBox.warning(self, "Invalid Name", "Variable name must be a valid Python identifier (e.g. text1, counter).")
            return
        self.accept()

    def get_result(self) -> Tuple[str, str, str, str]:
        """Returns (name, type, initial_value, scope_type['global' | 'state'])"""
        name = self.inp_name.text().strip()
        t = self.combo_type.currentText()
        val = self.inp_value.text().strip() or "None"
        scope = "global" if self.rb_global.isChecked() else "state"
        return name, t, val, scope


class AddFunctionDialog(QDialog):
    """Dialog for scaffolding new Python callback or helper functions."""
    def __init__(self, parent=None, flavor: str = "Mocha"):
        super().__init__(parent)
        self.setWindowTitle("Create Script Function")
        self.resize(440, 260)

        pal = CATPPUCCIN_PALETTES.get(flavor, CATPPUCCIN_PALETTES["Mocha"])
        bg = pal["mantle"]
        surface = pal["surface0"]
        text_col = pal["text"]
        accent = pal["blue"]

        self.setStyleSheet(f"""
            QDialog {{ background-color: {bg}; color: {text_col}; }}
            QLabel {{ color: {text_col}; font-size: 12px; }}
            QLineEdit {{
                background-color: {surface};
                color: {text_col};
                border: 1px solid {pal['surface1']};
                border-radius: 6px;
                padding: 6px 10px;
                font-family: Consolas;
            }}
            QPushButton {{
                background-color: {surface};
                color: {text_col};
                border: 1px solid {pal['surface1']};
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {pal['surface1']}; }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        header = QLabel("⚡ <b>New Function Scaffold</b>")
        header.setStyleSheet(f"font-size: 14px; color: {accent};")
        layout.addWidget(header)

        form = QFormLayout()
        form.setSpacing(10)

        self.inp_name = QLineEdit("calculate_total")
        self.inp_name.setPlaceholderText("e.g. on_event, calculate_score")
        form.addRow("Function Name:", self.inp_name)

        self.inp_params = QLineEdit("app")
        self.inp_params.setPlaceholderText("e.g. app or app, value")
        form.addRow("Parameters:", self.inp_params)

        self.inp_desc = QLineEdit("")
        self.inp_desc.setPlaceholderText("Brief docstring or description")
        form.addRow("Description:", self.inp_desc)

        layout.addLayout(form)
        layout.addStretch()

        btn_box = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)

        self.btn_ok = QPushButton("⚡ Add Function")
        self.btn_ok.setStyleSheet(f"background-color: {pal['blue']}; color: #11111b; font-weight: bold;")
        self.btn_ok.clicked.connect(self._on_accept)

        btn_box.addStretch()
        btn_box.addWidget(btn_cancel)
        btn_box.addWidget(self.btn_ok)
        layout.addLayout(btn_box)

    def _on_accept(self):
        name = self.inp_name.text().strip()
        if not name or not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name):
            QMessageBox.warning(self, "Invalid Name", "Function name must be a valid Python identifier.")
            return
        self.accept()

    def get_result(self) -> Tuple[str, str, str]:
        return self.inp_name.text().strip(), self.inp_params.text().strip(), self.inp_desc.text().strip()


class ScriptOutlinePanel(QWidget):
    """
    Sidebar panel displaying Variables, Members, and Functions of the active script.
    Provides 1-click creation of variables and functions, navigation jump,
    and automatic code generation.
    """
    variable_requested = Signal()
    function_requested = Signal()
    jump_to_line_requested = Signal(int)
    insert_text_requested = Signal(str)

    def __init__(self, parent=None, flavor: str = "Mocha"):
        super().__init__(parent)
        self.flavor = flavor
        self.current_editor: Optional[ScriptEditorWidget] = None
        self._sync_timer = QTimer(self)
        self._sync_timer.setSingleShot(True)
        self._sync_timer.setInterval(300)
        self._sync_timer.timeout.connect(self.refresh_outline)

        self._init_ui()
        self.apply_theme(flavor)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        # Header bar
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(4, 2, 4, 2)
        lbl_title = QLabel("📑 <b>Script Members</b>")
        lbl_title.setStyleSheet("font-size: 12px; font-weight: bold;")
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()

        self.btn_collapse = QToolButton(self)
        self.btn_collapse.setText("◀")
        self.btn_collapse.setToolTip("Collapse / Toggle Outline")
        self.btn_collapse.setStyleSheet("border: none; padding: 2px 6px; font-size: 11px;")
        header_layout.addWidget(self.btn_collapse)
        layout.addLayout(header_layout)

        # Outline Tree
        self.tree = QTreeWidget(self)
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(14)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)
        self.tree.itemClicked.connect(self._on_item_clicked)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.tree)

        # Top-level Tree Categories
        self.item_vars = QTreeWidgetItem(self.tree, ["📊 Variables"])
        self.item_vars.setExpanded(True)

        self.item_funcs = QTreeWidgetItem(self.tree, ["⚡ Functions & Events"])
        self.item_funcs.setExpanded(True)

        # Action Buttons row below tree
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(4)
        self.btn_add_var = QPushButton("➕ Variable")
        self.btn_add_var.setToolTip("Create new module or app.state variable")
        self.btn_add_var.setStyleSheet("padding: 4px 8px; font-size: 11px; font-weight: bold;")
        self.btn_add_var.clicked.connect(self.variable_requested.emit)

        self.btn_add_func = QPushButton("➕ Function")
        self.btn_add_func.setToolTip("Scaffold a new function")
        self.btn_add_func.setStyleSheet("padding: 4px 8px; font-size: 11px; font-weight: bold;")
        self.btn_add_func.clicked.connect(self.function_requested.emit)

        btn_bar.addWidget(self.btn_add_var)
        btn_bar.addWidget(self.btn_add_func)
        layout.addLayout(btn_bar)

    def apply_theme(self, flavor: str):
        self.flavor = flavor
        pal = CATPPUCCIN_PALETTES.get(flavor, CATPPUCCIN_PALETTES["Mocha"])
        bg = pal["mantle"]
        surface = pal["surface0"]
        text_col = pal["text"]

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg};
                color: {text_col};
            }}
            QTreeWidget {{
                background-color: {surface};
                color: {text_col};
                border: 1px solid {pal['surface1']};
                border-radius: 6px;
                padding: 4px;
                font-family: Consolas, Segoe UI;
                font-size: 11px;
            }}
            QTreeWidget::item {{
                padding: 3px 2px;
                border-radius: 4px;
            }}
            QTreeWidget::item:hover {{
                background-color: {pal['surface1']};
            }}
            QTreeWidget::item:selected {{
                background-color: {pal['surface2']};
                color: {pal['text']};
            }}
            QPushButton {{
                background-color: {surface};
                color: {text_col};
                border: 1px solid {pal['surface1']};
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {pal['surface1']};
            }}
        """)

    def set_active_editor(self, editor: Optional[ScriptEditorWidget]):
        if self.current_editor:
            try:
                self.current_editor.textChanged.disconnect(self._on_text_changed)
            except Exception:
                pass
        self.current_editor = editor
        if self.current_editor:
            self.current_editor.textChanged.connect(self._on_text_changed)
        self.refresh_outline()

    def _on_text_changed(self):
        self._sync_timer.start()

    def refresh_outline(self):
        self.item_vars.takeChildren()
        self.item_funcs.takeChildren()

        if not self.current_editor:
            return

        code = self.current_editor.toPlainText()
        pal = CATPPUCCIN_PALETTES.get(self.flavor, CATPPUCCIN_PALETTES["Mocha"])
        icon_vr = make_completion_icon("v", pal.get("lavender", "#b4befe"))
        icon_fn = make_completion_icon("f", pal.get("blue", "#89b4fa"))
        icon_st = make_completion_icon("s", pal.get("teal", "#94e2d5"))

        variables, functions = extract_script_members(code)

        for v in variables:
            v_name = v.get("name", "")
            v_val = v.get("value", "")
            lineno = v.get("lineno", 1)
            v_type = v.get("type", "global")

            label = f"{v_name}"
            if v_val:
                label += f" = {v_val}"

            item = QTreeWidgetItem(self.item_vars, [label])
            item.setIcon(0, icon_st if v_type == "state" else icon_vr)
            item.setData(0, Qt.ItemDataRole.UserRole, {"type": "variable", "name": v_name, "lineno": lineno, "vtype": v_type})
            item.setToolTip(0, f"Line {lineno}: {v_name} ({v_type})\nTip: Use 'global {v_name}' inside functions if modifying a module variable.")

        for f in functions:
            f_name = f.get("name", "")
            f_params = ", ".join(f.get("params", []))
            lineno = f.get("lineno", 1)

            label = f"{f_name}({f_params})"
            item = QTreeWidgetItem(self.item_funcs, [label])
            item.setIcon(0, icon_fn)
            item.setData(0, Qt.ItemDataRole.UserRole, {"type": "function", "name": f_name, "lineno": lineno})
            item.setToolTip(0, f"Line {lineno}: def {label}")

        self.item_vars.setExpanded(True)
        self.item_funcs.setExpanded(True)

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and "lineno" in data:
            self.jump_to_line_requested.emit(data["lineno"])

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and "name" in data:
            self.insert_text_requested.emit(data["name"])

    def _show_context_menu(self, pos):
        item = self.tree.itemAt(pos)
        if not item:
            return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return

        menu = QMenu(self)
        name = data.get("name", "")
        lineno = data.get("lineno", 1)
        item_type = data.get("type", "")

        act_jump = menu.addAction(f"📍 Jump to Line {lineno}")
        act_jump.triggered.connect(lambda: self.jump_to_line_requested.emit(lineno))

        if item_type == "variable":
            act_insert = menu.addAction(f"📋 Insert '{name}' at Cursor")
            act_insert.triggered.connect(lambda: self.insert_text_requested.emit(name))

            if not name.startswith("app.state"):
                act_global = menu.addAction(f"⚡ Insert 'global {name}' at Cursor")
                act_global.triggered.connect(lambda: self.insert_text_requested.emit(f"global {name}\n    "))

        menu.exec(self.tree.viewport().mapToGlobal(pos))


class ScriptEditorTab(QWidget):
    def __init__(self, parent=None, flavor: str = "Mocha"):
        super().__init__(parent)
        self.flavor = flavor
        self.known_nodes: List[str] = []
        self.editors: Dict[str, ScriptEditorWidget] = {}
        self.font_family = "Consolas"
        self.font_size = 11
        self.scale_percent = 100
        self._last_outline_size = 220

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Splitter dividing Outline Panel and Script Tabs
        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)

        # Left: Script Outline & Variables Panel
        self.outline_panel = ScriptOutlinePanel(self, self.flavor)
        self.outline_panel.variable_requested.connect(self._open_add_variable_dialog)
        self.outline_panel.function_requested.connect(self._open_add_function_dialog)
        self.outline_panel.jump_to_line_requested.connect(self._jump_to_line)
        self.outline_panel.insert_text_requested.connect(self._insert_text_at_cursor)
        self.outline_panel.btn_collapse.clicked.connect(self._toggle_outline)
        self.splitter.addWidget(self.outline_panel)

        # Right: Tabbed Script Workspace
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self._on_tab_close_requested)
        self.tab_widget.currentChanged.connect(self._on_current_tab_changed)
        self.splitter.addWidget(self.tab_widget)

        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([220, 800])
        layout.addWidget(self.splitter)

    def _toggle_outline(self):
        sizes = self.splitter.sizes()
        if sizes[0] > 0:
            self._last_outline_size = sizes[0]
            self.splitter.setSizes([0, sizes[0] + sizes[1]])
            self.outline_panel.btn_collapse.setText("▶")
        else:
            restore = getattr(self, "_last_outline_size", 220) or 220
            self.splitter.setSizes([restore, max(200, sizes[1] - restore)])
            self.outline_panel.btn_collapse.setText("◀")

    def _on_current_tab_changed(self, index: int):
        self.outline_panel.set_active_editor(self.get_current_editor())

    def get_current_editor(self) -> Optional[ScriptEditorWidget]:
        curr = self.tab_widget.currentWidget()
        if isinstance(curr, ScriptEditorWidget):
            return curr
        return None

    def _open_add_variable_dialog(self):
        editor = self.get_current_editor()
        if not editor:
            return
        dlg = AddVariableDialog(self, self.flavor)
        if dlg.exec():
            name, v_type, val, scope = dlg.get_result()
            code = editor.toPlainText()

            if scope == "state":
                # Add to _ready(app)
                if "def _ready(app):" in code:
                    pattern = r"(def\s+_ready\s*\(\s*app\s*\)\s*:(\s*\"\"\"[^\"]*\"\"\")?)"
                    match = re.search(pattern, code)
                    if match:
                        insert_pos = match.end()
                        new_code = code[:insert_pos] + f"\n    app.state[\"{name}\"] = {val}" + code[insert_pos:]
                        editor.setPlainText(new_code)
                    else:
                        editor.appendPlainText(f"\n    app.state[\"{name}\"] = {val}\n")
                else:
                    scaffold = f"\n\ndef _ready(app):\n    \"\"\"Called when the scene tree has loaded and is ready.\"\"\"\n    app.state[\"{name}\"] = {val}\n"
                    editor.appendPlainText(scaffold)
            else:
                # Add as module global variable near top (after docstring/imports)
                lines = code.splitlines(keepends=True)
                insert_idx = 0
                in_docstring = False
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped.startswith('"""') or stripped.startswith("'''"):
                        if in_docstring:
                            in_docstring = False
                            insert_idx = i + 1
                            continue
                        elif stripped.count('"""') == 1 or stripped.count("'''") == 1:
                            in_docstring = True
                            continue
                        else:
                            insert_idx = i + 1
                            continue
                    if in_docstring:
                        continue
                    if stripped.startswith("import ") or stripped.startswith("from "):
                        insert_idx = i + 1
                        continue
                    if stripped.startswith("def ") or stripped.startswith("class "):
                        break
                    if "=" in stripped:
                        insert_idx = i + 1

                var_decl = f"{name} = {val}\n"
                if insert_idx < len(lines):
                    lines.insert(insert_idx, "\n" + var_decl if insert_idx > 0 and lines[insert_idx - 1].strip() else var_decl)
                else:
                    lines.append("\n" + var_decl)
                editor.setPlainText("".join(lines))

            self.outline_panel.refresh_outline()
            self._jump_to_token(name)

    def _open_add_function_dialog(self):
        editor = self.get_current_editor()
        if not editor:
            return
        dlg = AddFunctionDialog(self, self.flavor)
        if dlg.exec():
            name, params, desc = dlg.get_result()
            scaffold = f"\n\ndef {name}({params}):\n"
            if desc:
                scaffold += f'    """{desc}"""\n'
            scaffold += "    pass\n"

            code = editor.toPlainText()
            if not code.endswith("\n"):
                scaffold = "\n" + scaffold
            editor.appendPlainText(scaffold)
            self.outline_panel.refresh_outline()
            self.jump_to_function(self.tab_widget.tabText(self.tab_widget.currentIndex()), name)

    def _jump_to_line(self, lineno: int):
        editor = self.get_current_editor()
        if not editor:
            return
        doc = editor.document()
        block = doc.findBlockByLineNumber(lineno - 1)
        if block.isValid():
            cur = editor.textCursor()
            cur.setPosition(block.position())
            editor.setTextCursor(cur)
            editor.centerCursor()
            editor.setFocus()

    def _jump_to_token(self, token: str):
        editor = self.get_current_editor()
        if not editor:
            return
        code = editor.toPlainText()
        pos = code.find(token)
        if pos != -1:
            cur = editor.textCursor()
            cur.setPosition(pos)
            cur.setPosition(pos + len(token), QTextCursor.MoveMode.KeepAnchor)
            editor.setTextCursor(cur)
            editor.centerCursor()
            editor.setFocus()

    def _insert_text_at_cursor(self, text: str):
        editor = self.get_current_editor()
        if not editor:
            return
        cur = editor.textCursor()
        cur.insertText(text)
        editor.setTextCursor(cur)
        editor.setFocus()

    def set_font_settings(self, family: str = "Consolas", size: int = 11, scale_percent: int = 100):
        """Updates font family, point size, and scaling across all open editor tabs."""
        self.font_family = family
        self.font_size = size
        self.scale_percent = scale_percent

        scale = max(0.5, min(3.0, scale_percent / 100.0))
        effective_size = max(8, round(size * scale))

        for ed in self.editors.values():
            font = QFont(family, effective_size)
            font.setStyleHint(QFont.StyleHint.Monospace)
            ed.setFont(font)
            ed.setTabStopDistance(max(16, round(32 * scale)))
            ed.update_line_number_area_width(0)
            ed.highlight_current_line()

    def set_known_nodes(self, node_ids: List[str]):
        """Propagates known node IDs to all active editor tabs."""
        self.known_nodes = list(node_ids)
        for ed in self.editors.values():
            ed.set_known_nodes(self.known_nodes)

    def apply_theme(self, flavor: str):
        self.flavor = flavor
        self.outline_panel.apply_theme(flavor)
        for ed in self.editors.values():
            ed.apply_theme(flavor)

    def open_script(self, filename: str, content: Optional[str] = None) -> ScriptEditorWidget:
        if filename in self.editors:
            for i in range(self.tab_widget.count()):
                if self.tab_widget.tabText(i) == filename:
                    self.tab_widget.setCurrentIndex(i)
                    break
            self.outline_panel.set_active_editor(self.editors[filename])
            return self.editors[filename]

        editor = ScriptEditorWidget(self, self.flavor)
        scale = max(0.5, min(3.0, self.scale_percent / 100.0))
        effective_size = max(8, round(self.font_size * scale))
        font = QFont(self.font_family, effective_size)
        font.setStyleHint(QFont.StyleHint.Monospace)
        editor.setFont(font)
        editor.setTabStopDistance(max(16, round(32 * scale)))
        editor.set_known_nodes(self.known_nodes)
        if content is not None:
            editor.setPlainText(content)
        self.editors[filename] = editor
        self.tab_widget.addTab(editor, filename)
        self.tab_widget.setCurrentWidget(editor)
        self.outline_panel.set_active_editor(editor)
        return editor

    def close_script(self, filename: str) -> None:
        if filename in self.editors:
            for i in range(self.tab_widget.count()):
                if self.tab_widget.tabText(i) == filename:
                    self.tab_widget.removeTab(i)
                    break
            self.editors.pop(filename, None)
            self.outline_panel.set_active_editor(self.get_current_editor())

    def rename_script(self, old_name: str, new_name: str) -> None:
        if old_name in self.editors:
            editor = self.editors.pop(old_name)
            self.editors[new_name] = editor
            for i in range(self.tab_widget.count()):
                if self.tab_widget.tabText(i) == old_name:
                    self.tab_widget.setTabText(i, new_name)
                    break

    def _on_tab_close_requested(self, index: int) -> None:
        name = self.tab_widget.tabText(index)
        self.tab_widget.removeTab(index)
        self.editors.pop(name, None)
        self.outline_panel.set_active_editor(self.get_current_editor())

    def get_script_content(self, filename: str) -> str:
        if filename in self.editors:
            return self.editors[filename].toPlainText()
        return ""

    def get_all_scripts(self) -> Dict[str, str]:
        return {fn: ed.toPlainText() for fn, ed in self.editors.items()}

    def append_callback_scaffold(self, filename: str, func_name: str, sig_name: str) -> None:
        editor = self.open_script(filename)
        editor.append_callback_scaffold(func_name, sig_name)
        self.outline_panel.refresh_outline()

    def jump_to_function(self, filename: str, func_name: str) -> None:
        editor = self.open_script(filename)
        code = editor.toPlainText()
        pos = code.find(f"def {func_name}")
        if pos != -1:
            cursor = editor.textCursor()
            cursor.setPosition(pos)
            editor.setTextCursor(cursor)
            editor.centerCursor()
            editor.setFocus()
