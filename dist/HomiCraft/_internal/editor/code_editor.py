"""
HomiCraft Embedded Python Script Editor & Multi-Script Workspace
Provides Godot-style multi-tab script editing with Catppuccin syntax highlighting,
line numbers, closable tabs, auto-indentation on Enter, smart Tab/Backspace,
drag-and-drop node references from the Scene Tree, and rich IDE code autocompletion.
"""

import os
import re
from typing import Dict, List, Optional, Tuple

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPlainTextEdit,
    QTextEdit, QPushButton, QLabel, QCompleter, QListView, QAbstractItemView
)
from PySide6.QtGui import (
    QFont, QTextCursor, QColor, QPainter, QSyntaxHighlighter,
    QTextCharFormat, QKeyEvent, QDragEnterEvent, QDragMoveEvent, QDropEvent,
    QStandardItemModel, QStandardItem, QIcon, QPixmap
)
from PySide6.QtCore import Qt, QRect, QSize, QRegularExpression

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

    # 7. DRAG & DROP NODES FROM SCENE TREE (Godot style!)
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


class ScriptEditorTab(QWidget):
    def __init__(self, parent=None, flavor: str = "Mocha"):
        super().__init__(parent)
        self.flavor = flavor
        self.known_nodes: List[str] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self._on_tab_close_requested)
        layout.addWidget(self.tab_widget)

        self.editors: Dict[str, ScriptEditorWidget] = {}

    def set_known_nodes(self, node_ids: List[str]):
        """Propagates known node IDs to all active editor tabs."""
        self.known_nodes = list(node_ids)
        for ed in self.editors.values():
            ed.set_known_nodes(self.known_nodes)

    def apply_theme(self, flavor: str):
        self.flavor = flavor
        for ed in self.editors.values():
            ed.apply_theme(flavor)

    def open_script(self, filename: str, content: Optional[str] = None) -> ScriptEditorWidget:
        if filename in self.editors:
            for i in range(self.tab_widget.count()):
                if self.tab_widget.tabText(i) == filename:
                    self.tab_widget.setCurrentIndex(i)
                    break
            return self.editors[filename]

        editor = ScriptEditorWidget(self, self.flavor)
        editor.set_known_nodes(self.known_nodes)
        if content is not None:
            editor.setPlainText(content)
        self.editors[filename] = editor
        self.tab_widget.addTab(editor, filename)
        self.tab_widget.setCurrentWidget(editor)
        return editor

    def close_script(self, filename: str) -> None:
        if filename in self.editors:
            for i in range(self.tab_widget.count()):
                if self.tab_widget.tabText(i) == filename:
                    self.tab_widget.removeTab(i)
                    break
            self.editors.pop(filename, None)

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

    def get_script_content(self, filename: str) -> str:
        if filename in self.editors:
            return self.editors[filename].toPlainText()
        return ""

    def get_all_scripts(self) -> Dict[str, str]:
        return {fn: ed.toPlainText() for fn, ed in self.editors.items()}

    def append_callback_scaffold(self, filename: str, func_name: str, sig_name: str) -> None:
        editor = self.open_script(filename)
        editor.append_callback_scaffold(func_name, sig_name)

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
