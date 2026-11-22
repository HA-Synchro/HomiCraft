"""
HomiCraft Embedded Python Script Editor & Multi-Script Workspace
Provides Godot-style multi-tab script editing with Catppuccin syntax highlighting,
line numbers, closable tabs, auto-indentation on Enter, smart Tab/Backspace,
and drag-and-drop node references from the Scene Tree.
"""

import os
from typing import Dict, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPlainTextEdit,
    QTextEdit, QPushButton, QLabel
)
from PySide6.QtGui import (
    QFont, QTextCursor, QColor, QPainter, QSyntaxHighlighter,
    QTextCharFormat, QKeyEvent, QDragEnterEvent, QDragMoveEvent, QDropEvent
)
from PySide6.QtCore import Qt, QRect, QSize, QRegularExpression

from editor.theme import CATPPUCCIN_PALETTES


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

        self.apply_theme(flavor)
        self.update_line_number_area_width(0)
        self.highlight_current_line()

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

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        cursor = self.textCursor()

        # 1. ENTER / RETURN KEY: Auto-Indentation on Enter!
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
            event.accept()
            return

        # 2. TAB KEY: Insert 4 spaces or indent selection
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

        # 3. BACKTAB (SHIFT+TAB): Un-indent by 4 spaces
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

        # 4. BACKSPACE: Smart delete 4 spaces
        if key == Qt.Key.Key_Backspace and not cursor.hasSelection():
            col = cursor.positionInBlock()
            line_text = cursor.block().text()[:col]
            if len(line_text) >= 4 and line_text.endswith("    ") and not line_text.strip():
                cursor.setPosition(cursor.position() - 4, QTextCursor.MoveMode.KeepAnchor)
                cursor.removeSelectedText()
                event.accept()
                return

        super().keyPressEvent(event)

    # 5. DRAG & DROP NODES FROM SCENE TREE (Godot style!)
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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self._on_tab_close_requested)
        layout.addWidget(self.tab_widget)

        self.editors: Dict[str, ScriptEditorWidget] = {}

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
