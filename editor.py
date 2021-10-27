#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import math
import pathlib
import sys
from typing import List, Optional, Union

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from completer import MindustryLogicCompleter
from highlighter import MindustryLogicSyntaxHighlighter
from syntax_file_parser import SyntaxFileParser


class LineNumberArea(QWidget):
    """Mindustry Logic Editor line number area"""

    def __init__(self, editor, *args, **kwarg):
        super(LineNumberArea, self).__init__(*args, **kwarg)
        self.editor: Union[QTextEdit, MindustryLogicEditor] = editor

    def sizeHint(self) -> QSize:
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event: QPaintEvent) -> None:
        self.editor.line_number_area_paint_event(event)


class CodeLineNumber(QTextBlockUserData):

    def __init__(self, number: Optional[int] = None, is_code: bool = False):
        super(CodeLineNumber, self).__init__()
        self.number: Optional[int] = number
        self.is_code: bool = is_code

    def __repr__(self):
        return f"{self.number=} {self.is_code=}"


class MindustryLogicEditor(QPlainTextEdit):
    """Mindustry (game) logic editor

    Features
        - highlight current line
        - current line numbering
        - comment toggle
        - code line numbering
        - syntax coloring
        - code completion
        - code snippets
        - linter (errors & warnings)
        - auto-wrap
        - dark mode
        - tabs
        - split view
        - themes
        """

    def __init__(self, *args, **kwargs):
        """
        Initialize mindustry logic editor instance

        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        """
        super(MindustryLogicEditor, self).__init__(*args, **kwargs)

        # current open file path
        self.path: Optional[pathlib.Path] = None

        # text highlighter
        self.highlighter: MindustryLogicSyntaxHighlighter = MindustryLogicSyntaxHighlighter(self.document())

        # text completer setup
        keywords = SyntaxFileParser("config/syntax.json").get_keywords()
        self.completer: Optional[MindustryLogicCompleter] = MindustryLogicCompleter(keywords)
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.activated.connect(self.insert_completion)

        # add text completer action
        # completer_action: QAction = QAction(self)
        # completer_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_Space))
        # completer_action.triggered.connect(self.popup_completer)
        # self.addAction(completer_action)

        # ----------------------------------------------------------------------
        # ------------------------- Editor components --------------------------
        # ----------------------------------------------------------------------

        # line number area
        self.line_number_area: LineNumberArea = LineNumberArea(editor=self, parent=self)
        self.line_number_area.setFont(QFont("Consolas", 14, QFont.ExtraLight))

        # ----------------------------------------------------------------------
        # ---------------------- configure GUI components ----------------------
        # ----------------------------------------------------------------------

        # set editor font
        self.font: QFont = QFont("Consolas", 14, QFont.Normal)
        self.setFont(self.font)

        # set tab to 4 spaces
        self.tab_width: int = 4
        self.setTabStopWidth(self.fontMetrics().horizontalAdvance(" ") * self.tab_width)

        # ----------------------- connect editor signals -----------------------
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        # ------------------------------- start --------------------------------
        self.update_line_number_area_width(0)
        self.highlight_current_line()

    def create_new_file(self) -> None:
        """
        create new file

        :return: None
        :rtype: None
        """
        self.clear()
        self.path = None

    def open_file(self) -> None:
        """
        Open an existing file

        :return: None
        :rtype: None
        """
        new_file, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            str(pathlib.Path.cwd()),
            "Mindustry Logic (*.mlog);;Text Files (*.txt);;All Files (*.*)",
        )

        if new_file:
            try:
                with open(new_file, "r") as file_handle:
                    file_content = file_handle.read()
            except Exception as exc:
                self.show_error(str(exc))

            else:
                self.path = pathlib.Path(new_file)
                self.setPlainText(file_content)

    def save_file(self) -> None:
        """
        Save current file

        :return: None
        :rtype: None
        """
        if self.path is None:
            return self.save_file_as()
        self._save_file(self.path)

    def save_file_as(self) -> None:
        """
        Save current file as

        :return: None
        :rtype: None
        """
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File As",
            str(pathlib.Path.cwd()),
            "Mindustry Logic (*.mlog);;Text Files (*.txt);;All Files (*.*)",
        )

        if file_path is not None and len(file_path) > 0:
            self._save_file(pathlib.Path(file_path))

    def _save_file(self, file_path: pathlib.Path) -> None:
        """
        Private method to save files

        :param file_path: path to save file into
        :type file_path: pathlib.Path
        :return: None
        :rtype: None
        """
        current_text = self.toPlainText()

        try:
            with open(file_path, "w") as file_handle:
                file_handle.write(current_text)

        except Exception as exc:
            self.show_error(str(exc))

        else:
            self.path = file_path

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        resize editor instance

        :param event: resize event
        :type event: QResizeEvent
        :return: None
        :rtype: None
        """
        super(MindustryLogicEditor, self).resizeEvent(event)
        rect: QRect = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(
                rect.left(),
                rect.top(),
                self.line_number_area_width(),
                rect.height()
            )
        )

    def keyPressEvent(self, event: QKeyEvent):
        """
        Handle key press events within editor
        1. replace tabs with at most 4 spaces till the nearest tab stop
        2. pop up auto complete suggestions when CTRL+SPACE are pressed
        3. comment current code line when CTRL+/ are pressed
        4. remove current code line when CTRL+D are pressed
        5. duplicate current code line down when ALT+CTRL+DOWN_KEY are pressed
        6. duplicate current code line up when ALT+CTRL+UP_KEY are pressed
        7. move current code line up when CTRL+UP_KEY are pressed
        8. move current code line down when CTRL+DOWN_KEY are pressed

        :param event: pressed key event
        :type event: QKeyEvent
        :return: None
        :rtype: None
        """

        def test_modifier(flag: Qt.KeyboardModifier, value: Qt.KeyboardModifiers):
            return flag & value == flag

        event_modifiers = event.modifiers()
        ctrl_modifier = test_modifier(Qt.ControlModifier, event_modifiers)
        shift_modifier = test_modifier(Qt.ShiftModifier, event_modifiers)
        alt_modifier = test_modifier(Qt.AltModifier, event_modifiers)
        no_modifiers = event_modifiers == Qt.NoModifier
        event_key = event.key()
        event_text = event.text()

        # replace tabs
        if no_modifiers and event_key == Qt.Key_Tab:
            return self.replace_tabs_event(event)

        # pop up auto-complete suggestions
        if ctrl_modifier and event_key == Qt.Key_Space and self.completer is not None:
            return self.popup_completer_event(event)

        super(MindustryLogicEditor, self).keyPressEvent(event)

    def replace_tabs_event(self, event: QKeyEvent):
        """
        Replace tabs with spaces

        :param event: Tab key pressed event
        :type event: QKeyEvent
        :return: None
        :rtype: None
        """

        # override event key (tab) with a new key event (space) with at most 4 spaces as text
        cursor_position = self.textCursor().positionInBlock()
        tabs_to_insert = self.tab_width - (cursor_position % self.tab_width)
        event = QKeyEvent(
            QEvent.KeyPress,
            Qt.Key_Space,
            Qt.KeyboardModifiers(),
            (" " * tabs_to_insert),
            False,
            1
        )

        super(MindustryLogicEditor, self).keyPressEvent(event)

    def popup_completer_event(self, event: QKeyEvent) -> None:
        """
        Pop up suggestions pop up

        :param event: pressed key event
        :type event: QKeyEvent
        :return: None
        :rtype: None
        """
        if self.completer is None:
            return super(MindustryLogicEditor, self).keyPressEvent(event)

        # ignore these keys (enter, tab, escape, backtab) when completer pop up is visible
        if self.completer.popup().isVisible() and event.key() in (
            Qt.Key_Tab, Qt.Key_Escape, Qt.Key_Enter, Qt.Key_Backtab):
            return event.ignore()

        completer_prefix: str = self.text_under_cursor()

        if len(completer_prefix) == 0:
            return

        if completer_prefix != self.completer.completionPrefix():
            self.completer.setCompletionPrefix(completer_prefix)
            self.completer.popup().setCurrentIndex(
                self.completer.completionModel().index(0, 0)
            )

        cursor_rect: QRect = self.cursorRect()
        popup = self.completer.popup()

        cursor_rect.setWidth(
            popup.sizeHintForColumn(0) + popup.verticalScrollBar().sizeHint().width()
        )

        cursor_rect.moveLeft(
            popup.sizeHintForColumn(0) + popup.verticalScrollBar().sizeHint().width()
        )

        self.completer.complete(cursor_rect)

    def focusInEvent(self, event: QFocusEvent) -> None:
        """

        :param event:
        :type event: QFocusEvent
        :return: None
        :rtype: None
        """
        if self.completer is not None:
            self.completer.setWidget(self)
        super(MindustryLogicEditor, self).focusInEvent(event)

    def line_number_area_width(self) -> int:
        """
        calculate the width of the LineNumberArea widget

        :return:
        :rtype:
        """
        line_count = max(1, self.blockCount())
        width_in_digits = max(math.floor(math.log10(line_count)) + 2, 4)
        width_in_pixels = 3 + self.fontMetrics().horizontalAdvance("9") * width_in_digits
        return width_in_pixels * 2

    def line_number_area_paint_event(self, event: QPaintEvent) -> None:
        """
        paint line number area

        :param event: paint event
        :type event: QPaintEvent
        :return: None
        :rtype: None
        """
        # color background
        painter: QPainter = QPainter(self.line_number_area)

        code_line_number_area_offset: int = math.floor(self.line_number_area.width() / 2)

        # paint line number area background
        line_number_rect = event.rect()
        line_number_rect.setX(0)
        line_number_rect.setWidth(code_line_number_area_offset)
        painter.fillRect(line_number_rect, QColor(200, 200, 200))  # light gray

        # paint code line number area background
        code_line_number_rect = event.rect()
        code_line_number_rect.setX(code_line_number_area_offset)
        code_line_number_rect.setWidth(code_line_number_area_offset)
        painter.fillRect(code_line_number_rect, QColor(200, 200, 200).lighter(120))  # light gray

        # write line number and code line number
        text_block: QTextBlock = self.firstVisibleBlock()
        block_number: int = text_block.blockNumber()
        top: int = round(self.blockBoundingGeometry(text_block).translated(self.contentOffset()).top())
        bottom: int = top + round(self.blockBoundingRect(text_block).height())

        while text_block.isValid() and top <= event.rect().bottom():
            if text_block.isVisible() and bottom >= event.rect().top():
                # line number
                number: str = str(block_number + 1)
                painter.setPen(Qt.black)
                painter.drawText(
                    0,
                    top,
                    self.line_number_area.width(),
                    self.fontMetrics().height(),
                    Qt.AlignLeft,
                    number
                )

                # code line number
                block_data: CodeLineNumber = text_block.userData()
                painter.setPen(Qt.darkCyan)
                painter.drawText(
                    code_line_number_area_offset,
                    top,
                    self.line_number_area.width(),
                    self.fontMetrics().height(),
                    Qt.AlignLeft,
                    str(block_data.number) if (block_data.number >= 0 and block_data.is_code) else ""
                )

            text_block = text_block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(text_block).height())
            block_number += 1

    def text_under_cursor(self) -> str:
        """
        Get current text under cursor

        :return: string under cursor
        :rtype: string
        """
        text_cursor: QTextCursor = self.textCursor()
        text_cursor.select(QTextCursor.WordUnderCursor)
        return text_cursor.selectedText()

    @Slot(int)
    def update_line_number_area_width(self, new_block_count: int):
        """
        Update editor's viewport margins to show line number area

        :param new_block_count: number of lines
        :type new_block_count: int
        :return: None
        :rtype: None
        """
        # update text editor's view port right margin
        right_margin = self.line_number_area_width()
        self.setViewportMargins(
            right_margin,
            0,
            0,
            0
        )

        # get first visible text block
        text_block: QTextBlock = self.firstVisibleBlock()
        block_bottom: int = self.blockBoundingGeometry(text_block).translated(self.contentOffset()).bottom()

        # iterate over text blocks
        while text_block.isValid() and block_bottom <= self.geometry().bottom():

            prev_block: QTextBlock = text_block.previous()  # prev block
            prev_block_data: CodeLineNumber = prev_block.userData()  # prev block data

            current_block_text: str = text_block.text().strip()  # current block text
            is_code: bool = len(current_block_text) > 0 and not current_block_text.startswith("#")
            current_block_data = CodeLineNumber(is_code=is_code)  # current block data

            if is_code:
                if prev_block.isValid():
                    current_block_data.number = prev_block_data.number + 1
                else:
                    current_block_data.number = 0

            else:
                if prev_block.isValid():
                    current_block_data.number = prev_block_data.number
                else:
                    current_block_data.number = -1

            text_block.setUserData(current_block_data)
            text_block = text_block.next()

    @Slot(QRect, int)
    def update_line_number_area(self, rect: QRect, dy: int) -> None:
        """
        Update editor's viewport margins after scrolling

        :param rect: new visible area of editor after scrolling
        :type rect: QRect
        :param dy: change in Y co-ordinates after scrolling
        :type dy: int
        :return: None
        :rtype: None
        """
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(
                0,
                rect.y(),
                self.line_number_area.width(),
                rect.height()
            )

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    @Slot()
    def highlight_current_line(self) -> None:
        """
        Highlight current line

        :return: None
        :rtype: None
        """
        extra_selections: List[QTextEdit.ExtraSelection] = list()

        if self.isReadOnly():
            return

        selection: QTextEdit.ExtraSelection = QTextEdit.ExtraSelection()
        line_color = QColor(255, 215, 0).lighter(180)  # light gold
        selection.format.setBackground(line_color)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        extra_selections.append(selection)

        self.setExtraSelections(extra_selections)

    @Slot(str)
    def insert_completion(self, string: str) -> None:
        """

        :param string:
        :type string:
        :return:
        :rtype:
        """
        # check if completer is connected to the editor

        if string == self.completer.completionPrefix():
            return

        text_cursor: QTextCursor = self.textCursor()
        extra: int = len(string) - len(self.completer.completionPrefix())
        text_cursor.movePosition(QTextCursor.Left)
        text_cursor.movePosition(QTextCursor.EndOfWord)
        text_cursor.insertText(string[0-extra:])
        self.setTextCursor(text_cursor)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    t = MindustryLogicEditor()
    t.show()
    sys.exit(app.exec_())
