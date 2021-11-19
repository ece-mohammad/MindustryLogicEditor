#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import math
import sys
from typing import List, Optional, Union

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from base_editor import BaseCodeEditor
from completer import MindustryLogicCompleter
from highlighter import MindustryLogicSyntaxHighlighter
from syntax_file_parser import SyntaxFileParser
from find_replace_widget import FindAndReplaceWidget, SearchFlags


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


class MindustryLogicEditor(BaseCodeEditor):
    """
    Mindustry (game) logic editor

    Features
        - highlight current line
        - current line numbering
        - code line numbering
        - syntax coloring
        - code completion
        - tabs
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

        # ------------------------- Editor components --------------------------

        # line number area
        self.line_number_area: LineNumberArea = LineNumberArea(editor=self, parent=self)
        self.line_number_area.setFont(QFont("Consolas", 14, QFont.ExtraLight))

        # text highlighter
        self.highlighter: MindustryLogicSyntaxHighlighter = MindustryLogicSyntaxHighlighter(self.document())

        # auto completer widget
        self.keywords = SyntaxFileParser("config/syntax.json").get_keywords()
        self.completer: Optional[MindustryLogicCompleter] = MindustryLogicCompleter(self.keywords)
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseSensitive)
        self.completer.activated.connect(self.insert_completion)

        # ------------------------------ Actions -------------------------------

        # add comment toggle action
        self.comment_toggle_action: QAction = QAction(self)
        self.comment_toggle_action.setShortcut(QKeySequence(Qt.Key_Slash | Qt.CTRL))
        self.comment_toggle_action.triggered.connect(self.comment_toggle)
        self.addAction(self.comment_toggle_action)

        # add text completer action
        self.completer_action: QAction = QAction(self)
        self.completer_action.setShortcut(QKeySequence(Qt.Key_Space | Qt.CTRL))
        self.completer_action.triggered.connect(self.auto_complete_action)
        self.addAction(self.completer_action)

        # -------------------------- slots & signals ---------------------------
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)

        # ------------------------------- start --------------------------------
        self.update_line_number_area_width(0)
        self.highlight_current_line()

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
        line_number_area_width: int = self.line_number_area_width()
        # find_and_replace_widget_size: QSize = self.find_and_replace_widget_size()

        # set line number area geometry
        self.line_number_area.setGeometry(
            QRect(
                rect.left(),
                rect.top(),
                line_number_area_width,
                rect.height()
            )
        )

        # # set find dialog geometry
        # self.find_and_replace_widget.setGeometry(
        #     QRect(
        #         rect.left(),
        #         # rect.left() + line_number_area_width,
        #         rect.bottom() - find_and_replace_widget_size.height(),
        #         find_and_replace_widget_size.width(),
        #         find_and_replace_widget_size.height()
        #     )
        # )

    def keyPressEvent(self, event: QKeyEvent) -> None:
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

        event_modifiers = event.modifiers()
        no_modifiers = event_modifiers == Qt.NoModifier
        event_key = event.key()

        # The following keys are forwarded by the completer to the widget
        if self.completer.popup().isVisible() and event_key in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Tab, Qt.Key_Backtab,
                                                                Qt.Key_Escape):
            return event.ignore()  # let the completer do default behavior

        # replace tabs ith spaces
        if no_modifiers:
            if event_key == Qt.Key_Tab:
                event = self.replace_tab_event(event)

        # # comment toggle
        # elif editor_utils.test_modifiers(event_modifiers, Qt.ControlModifier):
        #     if event_key == Qt.Key_Slash:
        #         self.comment_toggle(event)

        super(MindustryLogicEditor, self).keyPressEvent(event)

        if event_key in (Qt.Key_Space, Qt.Key_Tab, Qt.Key_Return):
            text_cursor: QTextCursor = self.textCursor()
            text_cursor.movePosition(QTextCursor.PreviousWord, QTextCursor.KeepAnchor)
            text_cursor.select(QTextCursor.WordUnderCursor)
            text: str = text_cursor.selectedText()
            if text.isalnum():
                self.add_word_to_keyword(text)

        # auto complete suggestions
        self.auto_complete_suggestions(event.text().strip())

    def comment_toggle(self) -> None:
        """
        Toggle comment on current line or selected lines

        :return: None
        :rtype: None
        """

        def is_single_line_selection(cursor: QTextCursor) -> bool:
            """
            Check if current selection is in a single line or spans multiple lines

            :param cursor: current text cursor
            :type cursor: QTextCursor
            :return: True if current selection is in a single line,
                False if the selection spans multiple lines
            :rtype: bool
            """
            document: QTextDocument = self.document()
            selection_start: int = text_cursor.selectionStart()
            selection_end: int = text_cursor.selectionEnd()
            return document.findBlock(selection_start) == document.findBlock(selection_end)

        # text cursor
        text_cursor: QTextCursor = self.textCursor()

        # check if there is a
        if text_cursor.hasSelection() and not is_single_line_selection(text_cursor):
            self.toggle_block_comment(text_cursor)
        else:
            self.toggle_line_comment(text_cursor)

    def toggle_line_comment(self, text_cursor: QTextCursor) -> None:
        """
        Toggle comment for the line where text cursor currently is. If the current
        line is a comment, comment will be removed. Otherise, a comment will be
        inserted at the start of the line

        :param text_cursor: text cursor
        :type text_cursor: QTextCursor
        :return: None
        :rtype: None
        """
        current_line: QTextBlock = text_cursor.block()
        line_text: str = current_line.text()

        if line_text.startswith("#"):
            self.remove_comment(text_cursor)
        else:
            self.comment_line(text_cursor)

    def toggle_block_comment(self, text_cursor: QTextCursor) -> None:
        """
        Toggle comment on current selected lines. If all lines are already commented,
        the comment is removed from all lines. Otherwise, a comment will be inserted
        at the start of each line

        :param text_cursor: current text cursor
        :type text_cursor: QTextCursor
        :return: None
        :rtype: None
        """

        # enlarge selection
        self.enlarge_selection(text_cursor)

        # current selection start & end positions
        selection_start: int = text_cursor.selectionStart()
        selection_end: int = text_cursor.selectionEnd()
        document: QTextDocument = self.document()

        # move to the start of first selected line
        start_block: QTextBlock = document.findBlock(selection_start)

        # move to the end of last selected line
        end_block: QTextBlock = document.findBlock(selection_end)

        # check all lines are commented (selection is a comment block)
        is_comment_block: bool = True
        current_block: QTextBlock = QTextBlock(start_block)
        while is_comment_block and current_block.isValid() and current_block.blockNumber() <= end_block.blockNumber():
            is_comment_block = is_comment_block and current_block.text().startswith("#")
            current_block = current_block.next()

        # loop over blocks to add (or remove) comments
        text_cursor.beginEditBlock()
        text_cursor.setPosition(selection_start, QTextCursor.MoveAnchor)
        current_block: QTextBlock = QTextBlock(start_block)
        while current_block.isValid() and current_block.blockNumber() <= end_block.blockNumber():
            if is_comment_block:
                self.remove_comment(text_cursor)
            else:
                self.comment_line(text_cursor)
            current_block = current_block.next()
            text_cursor.movePosition(QTextCursor.NextBlock, QTextCursor.KeepAnchor)
        text_cursor.endEditBlock()

    def auto_complete_suggestions(self, suggestion_text: str) -> None:
        """
        Show and update auto complete suggestions

        :param suggestion_text: text to show suggestions for
        :type suggestion_text: str
        :return: None
        :rtype: None
        """

        completer_popup = self.completer.popup()

        # get prefix under the cursor
        completion_prefix: str = self.text_under_cursor()

        if len(completion_prefix) == 0 or len(suggestion_text) == 0:
            return completer_popup.hide()

        if completion_prefix == self.completer.currentCompletion():
            return completer_popup.hide()

        if completion_prefix != self.completer.completionPrefix():
            self.completer.setCompletionPrefix(completion_prefix)
            self.completer.popup().setCurrentIndex(
                self.completer.completionModel().index(0, 0)
            )

        cursor_rect: QRect = self.cursorRect()
        rect_offset: int = completer_popup.sizeHintForColumn(0) + completer_popup.verticalScrollBar().sizeHint().width()
        cursor_rect.setX(cursor_rect.x() + self.line_number_area_width())
        cursor_rect.setWidth(rect_offset + self.line_number_area_width())
        self.completer.complete(cursor_rect)

    def auto_complete_action(self) -> None:
        """
        Pop up auto complete suggestion for the current text under the cursor

        :return: None
        :rtype: None
        """
        suggestion_text: str = self.text_under_cursor().strip()
        self.auto_complete_suggestions(suggestion_text)

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
                font: QFont = self.line_number_area.font()
                font.setPointSize(self.font.pointSize())
                painter.setFont(font)
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

                if block_data is None:
                    break

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

    def add_word_to_keyword(self, word: str) -> None:
        """
        Add a word to word list

        :param word: a word (at least 4 characters in length)
        :type word: str
        :return: None
        :rtype: None
        """

        word = word.strip()
        if len(word) < 4:
            return
        keywords = set(self.keywords)
        keywords.add(word)
        keywords = list(keywords)
        self.keywords = keywords
        self.completer.update_model(keywords)

    def insertFromMimeData(self, source: QMimeData) -> None:
        """

        :param source:
        :type source:
        :return:
        :rtype:
        """

        super(MindustryLogicEditor, self).insertFromMimeData(source)

        if source.hasText():
            for line in source.text().splitlines():
                for word in line.split():
                    if word.isalnum():
                        self.add_word_to_keyword(word)

    def hide_find_and_replace_widget(self) -> None:
        """
        Hide find and replce widget

        :return: None
        :rtype: None
        """
        viewport_margins: QMargins = self.viewportMargins()
        viewport_margins.setBottom(0)
        self.setViewportMargins(viewport_margins)

    def _find_string(self, search_expr: str, search_flags: SearchFlags) -> bool:
        """
        A helper function to find a string within the editor's text starting from the cursor's current position

        :param search_expr: search expression to find
        :type search_expr: str
        :param search_flags: search options/flags
        :type search_flags: SearchFlags
        :return: True if search expression was found, False otherwise
        :rtype: bool
        """
        search_options: QTextDocument.FindFlag = 0  # QTextDocument.FindBackward

        if search_flags & SearchFlags.Regex:

            if search_flags & SearchFlags.CaseSensitive:
                regex_expr: QRegExp = QRegExp(search_expr, Qt.CaseSensitive)
            else:
                regex_expr: QRegExp = QRegExp(search_expr)

            if search_flags & SearchFlags.WholeWord:
                search_options |= QTextDocument.FindWholeWords

            if search_options == 0:
                result = self.find(regex_expr)
            else:
                result = self.find(regex_expr, search_options)

        else:
            if search_flags & SearchFlags.CaseSensitive:
                search_options |= QTextDocument.FindCaseSensitively

            if search_flags & SearchFlags.WholeWord:
                search_options |= QTextDocument.FindWholeWords

            if search_options == 0:
                result: bool = self.find(search_expr)
            else:
                result: bool = self.find(search_expr, search_options)

        return result

    def find_string(self, search_expr: str, search_flags: SearchFlags) -> int:
        """
        Find a string in the whole document

        :param search_expr: search expression
        :type search_expr: str
        :param search_flags: search flags
        :type search_flags: SearchFlags
        :return: 1 if search expression was found, 0 otherwise
        :rtype: int
        """
        text_cursor: QTextCursor = self.textCursor()  # current text cursor
        og_position: int = text_cursor.position()  # current text cursor's position

        # find search expr starting from current cursor position
        found: bool = self._find_string(search_expr, search_flags)
        if found:
            return int(found)

        # go to the start of the document and search again (wrap around)
        text_cursor.movePosition(QTextCursor.Start, QTextCursor.MoveAnchor)
        self.setTextCursor(text_cursor)

        found = self._find_string(search_expr, search_flags)
        if found:
            return int(found)

        # set cursor to its original position
        text_cursor.setPosition(og_position, QTextCursor.MoveAnchor)
        self.setTextCursor(text_cursor)
        return int(found)

    def find_all(self, search_expr: str, search_flags: SearchFlags) -> int:
        """
        Find all occurrences of a string

        :param search_expr: search expression
        :type search_expr: str
        :param search_flags: search flags
        :type search_flags: SearchFlags
        :return: Number of search expression occurrences
        :rtype: int
        """
        text_cursor: QTextCursor = self.textCursor()  # current text cursor
        og_position: int = text_cursor.position()  # text cursor position
        extra_selections: List[QTextEdit.ExtraSelection] = self.extraSelections()

        # go to the start of the document
        text_cursor.movePosition(QTextCursor.Start, QTextCursor.MoveAnchor)
        self.setTextCursor(text_cursor)

        # find all occurrences of search_exp
        result_count: int = 0
        while self._find_string(search_expr, search_flags):
            result_count += 1
            selection: QTextEdit.ExtraSelection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor(160, 255, 160).lighter(110))  # light green
            selection.cursor = self.textCursor()
            extra_selections.append(selection)

        # return text cursor to its original position
        text_cursor.setPosition(og_position, QTextCursor.MoveAnchor)
        self.setTextCursor(text_cursor)

        # set extra selections
        self.setExtraSelections(extra_selections)
        return result_count

    def replace_string(self, search_expr: str, replace_expr: str, search_flags: SearchFlags) -> int:
        """
        Replace search expression with replace expression

        :param search_expr: search expression
        :type search_expr: str
        :param replace_expr:
        :type replace_expr: str
        :param search_flags:
        :type search_flags: SearchFlags
        :return: 1 if search expression was found, 0 otherwise
        :rtype: int
        """
        # find search expression
        found: bool = self.find_string(search_expr, search_flags)
        if found:
            text_cursor: QTextCursor = self.textCursor()  # text cursor
            text_cursor.insertText(replace_expr)    # replace search expression

        return int(found)

    def replace_all(self, search_expr: str, replace_expr: str, search_flags: SearchFlags) -> int:
        """
        Replace all occurrences of search expression with replace expression

        :param search_expr: search expression
        :type search_expr: str
        :param replace_expr:
        :type replace_expr: str
        :param search_flags:
        :type search_flags: SearchFlags
        :return: Number of search expression found and replaces
        :rtype: int
        """
        text_cursor: QTextCursor = self.textCursor()  # text cursor

        text_cursor.beginEditBlock()
        replace_count: int = 0
        while self.find_string(search_expr, search_flags):
            replace_count += 1
            text_cursor: QTextCursor = self.textCursor()  # text cursor
            text_cursor.insertText(replace_expr)

        text_cursor.endEditBlock()
        self.setTextCursor(text_cursor)
        return replace_count

    @pyqtSlot()
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

    @pyqtSlot(int)
    def update_line_number_area_width(self, new_block_count: int) -> None:
        """
        Update editor's viewport margins to show line number area

        :param new_block_count: number of lines
        :type new_block_count: int
        :return: None
        :rtype: None
        """
        # update text editor's view port right margin
        left_margin = self.line_number_area_width()
        viewport_margins: QMargins = self.viewportMargins()
        viewport_margins.setLeft(left_margin)
        self.setViewportMargins(viewport_margins)

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

    @pyqtSlot(QRect, int)
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

    @pyqtSlot(str)
    def insert_completion(self, completion: str) -> None:
        """
        Insert selected completion at the current text cursor position

        :param completion: selected completion
        :type completion: str
        :return: None
        :rtype: None
        """

        prefix = self.completer.completionPrefix()

        if completion == prefix:
            return

        text_cursor: QTextCursor = self.textCursor()
        text_cursor.select(QTextCursor.WordUnderCursor)
        text_cursor.insertText(completion)
        self.setTextCursor(text_cursor)

    @staticmethod
    def comment_line(text_cursor: QTextCursor) -> None:
        """
        Add comment (#) to the start of current line where the cursor is

        :param text_cursor:
        :type text_cursor:
        :return:
        :rtype:
        """
        line_text: str = text_cursor.block().text()
        text_cursor.movePosition(QTextCursor.StartOfBlock, QTextCursor.MoveAnchor)
        if line_text.startswith(" "):
            text_cursor.insertText("#")
        else:
            text_cursor.insertText("# ")

    @staticmethod
    def remove_comment(text_cursor: QTextCursor) -> None:
        """
        Removes comment from current line

        :param text_cursor: text cursor
        :type text_cursor: QTextCursor
        :return: None
        :rtype: None
        """
        line_text: str = text_cursor.block().text()
        text_cursor.movePosition(QTextCursor.StartOfBlock, QTextCursor.MoveAnchor)
        if line_text.startswith("# "):
            offset: int = 2
        else:
            offset: int = 1
        text_cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor, offset)
        text_cursor.removeSelectedText()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = QMainWindow()
    editor = MindustryLogicEditor()
    main_win.setCentralWidget(editor)
    main_win.show()
    sys.exit(app.exec_())
