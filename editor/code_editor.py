"""
HomiCraft Embedded Python Script Editor & Syntax Highlighter
Provides in-engine code editing with line numbers, Python syntax coloring,
and automated callback scaffolding.
"""

import re
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QTextEdit,
    QPushButton, QLabel
)
from PySide6.QtGui import (
    QFont, QTextCursor, QColor, QPainter, QSyntaxHighlighter,
    QTextCharFormat
)
from PySide6.QtCore import Qt, QRect, QSize, QRegularExpression


class PythonSyntaxHighlighter(QSyntaxHighlighter):
    """Rich syntax highlighter for Python code in HomiCraft."""

    def __init__(self, document):
        super().__init__(document)
        self.rules = []

        # Keyword format (blue/cyan)
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#4ecdc4"))
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

        # Built-ins and constants (purple/pink)
        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor("#ff79c6"))
        builtin_format.setFontWeight(QFont.Weight.Bold)
        builtins = ["True", "False", "None", "self", "app", "print", "len", "range", "int", "str", "float", "bool", "dict", "list"]
        for b in builtins:
            pattern = QRegularExpression(rf"\b{b}\b")
            self.rules.append((pattern, builtin_format))

        # Function definitions (yellow/orange)
        func_format = QTextCharFormat()
        func_format.setForeground(QColor("#ffd166"))
        self.rules.append((QRegularExpression(r"\bdef\s+([A-Za-z_][A-Za-z0-9_]*)"), func_format))

        # Numbers (light green)
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#06d6a0"))
        self.rules.append((QRegularExpression(r"\b[0-9]+(\.[0-9]+)?\b"), number_format))

        # Strings (greenish / peach)
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#f4a261"))
        self.rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), self.string_format))
        self.rules.append((QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), self.string_format))

        # Comments (grey/muted italic)
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#78909c"))
        self.comment_format.setFontItalic(True)
        self.rules.append((QRegularExpression(r"#.*"), self.comment_format))

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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)

        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        self.setTabStopDistance(32)

        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1a1a22;
                color: #e0e0e0;
                border: 1px solid #333340;
                selection-background-color: #2e4a46;
            }
        """)

        # Attach Syntax Highlighter
        self.highlighter = PythonSyntaxHighlighter(self.document())

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.update_line_number_area_width(0)
        self.highlight_current_line()

    def line_number_area_width(self):
        digits = 1
        max_b = max(1, self.blockCount())
        while max_b >= 10:
            max_b //= 10
            digits += 1
        space = 12 + self.fontMetrics().horizontalAdvance('9') * digits
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
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(26, 26, 34))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor(100, 110, 125))
                painter.drawText(0, top, self.line_number_area.width() - 6, self.fontMetrics().height(),
                                 Qt.AlignmentFlag.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def highlight_current_line(self):
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor(32, 32, 44))
            selection.format.setProperty(0x100000, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

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

        scaffold = f"\n\ndef {func_name}(app):\n    # TODO: Handle '{sig_name}' event\n    print('{func_name} fired!')\n"
        if not code.endswith("\n"):
            scaffold = "\n" + scaffold

        self.appendPlainText(scaffold)
        self.moveCursor(QTextCursor.MoveOperation.End)
        self.setFocus()


class ScriptEditorTab(QWidget):
    """The Script view container with top toolbar (status, save) and code editor."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.top_bar = QHBoxLayout()
        self.lbl_file = QLabel("📄 main.py (Python Script)")
        self.lbl_file.setStyleSheet("color: #4ecdc4; font-weight: bold; padding: 6px;")
        self.top_bar.addWidget(self.lbl_file)
        self.top_bar.addStretch()

        layout.addLayout(self.top_bar)

        self.editor = ScriptEditorWidget(self)
        layout.addWidget(self.editor)

    def load_code(self, code_text: str) -> None:
        self.editor.setPlainText(code_text)

    def get_code(self) -> str:
        return self.editor.toPlainText()
