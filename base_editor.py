#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pathlib
import sys
from typing import List, Optional

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class BaseCodeEditor(QPlainTextEdit):
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
        super(BaseCodeEditor, self).__init__(*args, **kwargs)

        # current open file path
        self.path: Optional[pathlib.Path] = None

        # ----------------------------------------------------------------------
        # ---------------------- configure GUI components ----------------------
        # ----------------------------------------------------------------------

        # set editor font
        self.font: QFont = QFont("Consolas", 14, QFont.Normal)
        self.setFont(self.font)

        # set tab to 4 spaces
        self.tab_width: int = 4
        self.setTabStopWidth(self.fontMetrics().horizontalAdvance(" ") * self.tab_width)

        # add comment toggle action
        self.comment_toggle_action: QAction = QAction(self)
        self.comment_toggle_action.setShortcut(QKeySequence(Qt.Key_Slash | Qt.CTRL))
        self.comment_toggle_action.triggered.connect(self.comment_toggle)
        self.addAction(self.comment_toggle_action)

        # remove current line action
        self.remove_lines_action: QAction = QAction(self)
        self.remove_lines_action.setShortcut(QKeySequence(Qt.Key_D | Qt.CTRL))
        self.remove_lines_action.triggered.connect(self.remove_lines)
        self.addAction(self.remove_lines_action)

        # duplicate lines action down
        self.duplicate_lines_down_action: QAction = QAction(self)
        self.duplicate_lines_down_action.setShortcut(QKeySequence(Qt.CTRL | Qt.ALT | Qt.Key_Down))
        self.duplicate_lines_down_action.triggered.connect(self.duplicate_lines_down)
        self.addAction(self.duplicate_lines_down_action)

        # duplicate lines action up
        self.duplicate_lines_up_action: QAction = QAction(self)
        self.duplicate_lines_up_action.setShortcut(QKeySequence(Qt.CTRL | Qt.ALT | Qt.Key_Up))
        self.duplicate_lines_up_action.triggered.connect(self.duplicate_lines_up)
        self.addAction(self.duplicate_lines_up_action)

        # move line up action
        self.move_lines_up_action: QAction = QAction(self)
        self.move_lines_up_action.setShortcut(QKeySequence(Qt.ALT | Qt.Key_Up))
        self.move_lines_up_action.triggered.connect(self.move_lines_up)
        self.addAction(self.move_lines_up_action)

        # move line down action
        self.move_lines_down_action: QAction = QAction(self)
        self.move_lines_down_action.setShortcut(QKeySequence(Qt.ALT | Qt.Key_Down))
        self.move_lines_down_action.triggered.connect(self.move_lines_down)
        self.addAction(self.move_lines_down_action)

        # zoom in action
        self.zoom_in_action: QAction = QAction(self)
        self.zoom_in_action.setShortcut(QKeySequence(Qt.Key_Plus | Qt.CTRL))
        self.zoom_in_action.triggered.connect(self.zoomIn)
        self.addAction(self.zoom_in_action)

        # zoom out action
        self.zoom_out_action: QAction = QAction(self)
        self.zoom_out_action.setShortcut(QKeySequence(Qt.Key_Minus | Qt.CTRL))
        self.zoom_out_action.triggered.connect(self.zoomOut)
        self.addAction(self.zoom_out_action)

        # ------------------------------- start --------------------------------
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.highlight_current_line()

    def is_modified(self) -> True:
        """
        Return true if the editor's document was modified

        :return: True if editor's document was modified, False otherwise
        :rtype: bool
        """
        return self.document().isModified()

    def get_open_file_name(self) -> str:
        """
        Get opened file name

        :return: opened file name
        :rtype: str
        """
        return self.path.name if self.path is not None else "new file"

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

    def auto_save(self):
        """
        Called by auto save timer to save current open file if it was modified

        :return: None
        :rtype: None
        """

        if self.path is None:
            return

        self.save_file()

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
            self.document().setModified(False)

    def keyPressEvent(self, event: QKeyEvent):
        """
        Handle key press events within editor
        1. replace tabs with at most 4 spaces till the nearest tab stop

        :param event: pressed key event
        :type event: QKeyEvent
        :return: None
        :rtype: None
        """

        event_modifiers = event.modifiers()
        no_modifiers = event_modifiers == Qt.NoModifier
        event_key = event.key()

        # replace tabs ith spaces
        if no_modifiers:
            if event_key == Qt.Key_Tab:
                event = self.replace_tab_event(event)

        super(BaseCodeEditor, self).keyPressEvent(event)

    def replace_tab_event(self, event: QKeyEvent) -> QKeyEvent:
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

        return event

    def comment_toggle(self) -> None:
        """
        Toggle comment on current line or selected lines

        :param event: key event that triggered comment toggle
        :type event: QKeyEvent
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
            # get current selection start & end positions
            selection_start: int = cursor.selectionStart()
            selection_end: int = cursor.selectionEnd()

            # move to selection start
            cursor.setPosition(selection_start, QTextCursor.MoveAnchor)
            start_block: int = cursor.blockNumber()

            # move to selection end
            cursor.setPosition(selection_end, QTextCursor.KeepAnchor)
            end_block: int = cursor.blockNumber()

            return start_block == end_block

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

        # current selection start & end positions
        select_start: int = text_cursor.selectionStart()
        select_end: int = text_cursor.selectionEnd()

        # move to the end of last selected line
        text_cursor.setPosition(select_end, QTextCursor.MoveAnchor)
        text_cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
        end_block: QTextBlock = text_cursor.block()

        # move to the start of first selected line
        text_cursor.setPosition(select_start, QTextCursor.KeepAnchor)
        text_cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
        start_block: QTextBlock = text_cursor.block()

        # check all lines are commented (selection is a comment block)
        is_comment_block: bool = True
        current_block: QTextBlock = QTextBlock(start_block)
        while is_comment_block is True and current_block.isValid() and current_block.blockNumber() <= end_block.blockNumber():
            is_comment_block = is_comment_block and current_block.text().startswith("#")
            current_block = current_block.next()

        # loop over blocks to add (or remove) comments
        text_cursor.beginEditBlock()
        current_block: QTextBlock = QTextBlock(start_block)
        while current_block.isValid() and current_block.blockNumber() <= end_block.blockNumber():
            if is_comment_block:
                self.remove_comment(text_cursor)
            else:
                self.comment_line(text_cursor)
            current_block = current_block.next()
            text_cursor.movePosition(QTextCursor.NextBlock, QTextCursor.KeepAnchor)
        text_cursor.endEditBlock()

    def remove_lines(self) -> None:
        """
        Remove current line where the cursor is, or all selected lines

        :return:
        :rtype:
        """

        text_cursor: QTextCursor = self.textCursor()
        if text_cursor.hasSelection():
            self.remove_selected_lines(text_cursor)
        else:
            self.remove_current_line(text_cursor)

    def remove_current_line(self, text_cursor: QTextCursor) -> None:
        """
        Remove current line

        :param text_cursor:
        :type text_cursor:
        :return:
        :rtype:
        """
        text_cursor: QTextCursor = self.textCursor()
        has_text: bool = len(text_cursor.block().text()) > 0
        if has_text:
            text_cursor.select(QTextCursor.BlockUnderCursor)
            text_cursor.removeSelectedText()
            text_cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
        else:
            text_cursor.deletePreviousChar()

    def remove_selected_lines(self, text_cursor: QTextCursor):
        """
        Remove selected lines

        :param text_cursor:
        :type text_cursor:
        :return:
        :rtype:
        """

        self.enlarge_selection(text_cursor)
        text_cursor.removeSelectedText()

    def duplicate_lines_up(self) -> None:
        """

        :return:
        :rtype:
        """
        text_cursor: QTextCursor = self.textCursor()
        self.enlarge_selection(text_cursor)

        selection_start: int = text_cursor.selectionStart()
        selection_end: int = text_cursor.selectionEnd()
        selected_text: str = text_cursor.selectedText()

        if selected_text in ("\u2029", "\u2028", "\u000A", "\u000C", "\u000D", ""):
            return

        self.duplicate_selection(text_cursor)

        text_cursor.setPosition(selection_start, QTextCursor.MoveAnchor)
        text_cursor.setPosition(selection_end, QTextCursor.KeepAnchor)
        self.setTextCursor(text_cursor)

    def duplicate_lines_down(self) -> None:
        """
        duplicate current line or current selected lines

        :return: None
        :rtype: None
        """
        text_cursor: QTextCursor = self.textCursor()

        selection_length: int = self.enlarge_selection(text_cursor)
        selected_text: str = text_cursor.selectedText()

        if selected_text in ("\u2029", "\u2028", "\u000A", "\u000C", "\u000D", ""):
            return

        offset: int = 1 if selected_text[-1] in ("\u2029", "\u2028", "\u000A", "\u000C", "\u000D") else 0

        self.duplicate_selection(text_cursor)

        current_position: int = text_cursor.position()

        text_cursor.setPosition(current_position - selection_length, QTextCursor.MoveAnchor)
        text_cursor.setPosition(current_position + offset, QTextCursor.KeepAnchor)
        self.setTextCursor(text_cursor)

    def move_lines_up(self) -> None:
        """
        Move current line (or selected lines) up by one line

        :return: None
        :rtype: None
        """
        text_cursor: QTextCursor = self.textCursor()

        # check if previous line exists
        if not text_cursor.block().previous().isValid():
            return

        if text_cursor.hasSelection():
            self.move_selected_lines_up(text_cursor)
        else:
            self.move_current_line_up(text_cursor)

    def move_current_line_up(self, text_cursor: QTextCursor) -> None:
        """
        Move current line (where cursor is) up by one line

        :param text_cursor: text cursor
        :type text_cursor: QTextCursor
        :return: None
        :rtype: None
        """

        current_line: QTextBlock = text_cursor.block()  # current line
        previous_line: QTextBlock = current_line.previous()  # previous line
        position_in_block: int = text_cursor.positionInBlock()  # cursor position in current line

        text_cursor.beginEditBlock()  # start edit group

        # select current line & previous line
        text_cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
        text_cursor.movePosition(QTextCursor.Up, QTextCursor.KeepAnchor)
        text_cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)

        # insert current line then previous line text
        text_cursor.insertText(f"{current_line.text()}\n{previous_line.text()}")

        # move cursor to previous line
        text_cursor.movePosition(QTextCursor.Up, QTextCursor.MoveAnchor)

        # return cursor to it's original relative position in the current line
        current_position = text_cursor.position()
        text_cursor.setPosition(current_position + position_in_block - text_cursor.positionInBlock())

        text_cursor.endEditBlock()  # end edit group

        self.setTextCursor(text_cursor)

    def move_selected_lines_up(self, text_cursor: QTextCursor) -> None:
        """
        Move selected lines up by one line

        :param text_cursor: text cursor
        :type text_cursor: QTextCursor
        :return: None
        :rtype: None
        """

        selection_start: int = text_cursor.selectionStart()  # current selection start position
        selection_end: int = text_cursor.selectionEnd()  # current selection edn position
        selection_length: int = selection_end - selection_start  # current selection length

        text_cursor.setPosition(selection_end, QTextCursor.MoveAnchor)  # go to selection end

        text_cursor.setPosition(selection_start, QTextCursor.KeepAnchor)  # go to selection start
        relative_start: int = text_cursor.positionInBlock()  # selection start position within line

        self.enlarge_selection(text_cursor)  # enlarge selection

        document: QTextDocument = self.document()
        previous_line: QTextBlock = document.findBlock(text_cursor.selectionStart()).previous()  # previous line
        previous_line_start: int = previous_line.position()  # previous line start position

        if not previous_line.isValid():
            return

        text_cursor.beginEditBlock()  # start edit group

        selection_text: str = text_cursor.selectedText()  # selected lines tex

        text_cursor.removeSelectedText()  # remove lines
        text_cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)  # select previous line
        text_cursor.movePosition(QTextCursor.Up, QTextCursor.KeepAnchor)
        text_cursor.insertText(f"{selection_text}\n{previous_line.text()}")  # insert text

        # return cursor to its position in the line & retore selection
        text_cursor.setPosition(previous_line_start + relative_start, QTextCursor.MoveAnchor)
        text_cursor.setPosition(text_cursor.position() + selection_length, QTextCursor.KeepAnchor)

        text_cursor.endEditBlock()  # end edit group
        self.setTextCursor(text_cursor)

    def move_lines_down(self) -> None:
        """
        Move current line (or selected lines) down by one line

        :return: None
        :rtype: None
        """
        text_cursor: QTextCursor = self.textCursor()

        # check if next line exists
        if not text_cursor.block().next().isValid():
            return

        if text_cursor.hasSelection():
            self.move_selected_lines_down(text_cursor)
        else:
            self.move_current_line_down(text_cursor)

    def move_current_line_down(self, text_cursor: QTextCursor) -> None:
        """
        Move current line (where cursor is) down by one line

        :param text_cursor: text cursor
        :type text_cursor: QTextCursor
        :return: None
        :rtype: None
        """
        current_line: QTextBlock = text_cursor.block()  # current line
        next_line: QTextBlock = current_line.next()  # next line
        position_in_block: int = text_cursor.positionInBlock()  # cursor position in current line

        text_cursor.beginEditBlock()  # start edit group

        # select current line & previous line
        text_cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
        text_cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor)
        text_cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)

        # insert current line then previous line text
        text_cursor.insertText(f"{next_line.text()}\n{current_line.text()}")

        # return cursor to it's original relative position in the current line
        current_position = text_cursor.position()
        text_cursor.setPosition(current_position + position_in_block - text_cursor.positionInBlock())

        text_cursor.endEditBlock()  # end edit group

        self.setTextCursor(text_cursor)

    def move_selected_lines_down(self, text_cursor: QTextCursor) -> None:
        """
        Move selected lines up by one line

        :param text_cursor: text cursor
        :type text_cursor: QTextCursor
        :return: None
        :rtype: None
        """

        selection_start: int = text_cursor.selectionStart()  # selection start
        selection_end: int = text_cursor.selectionEnd()  # selection end
        old_selection_length: int = selection_end - selection_start  # old selection length

        text_cursor.setPosition(selection_start, QTextCursor.MoveAnchor)  # move to selection start position
        relative_start_position: int = text_cursor.positionInBlock()  # cursor position within the line

        text_cursor.setPosition(selection_end, QTextCursor.KeepAnchor)

        self.enlarge_selection(text_cursor)  # enlarge selection
        selection_length: int = text_cursor.selectionEnd() - text_cursor.selectionStart()

        document: QTextDocument = self.document()
        next_line: QTextBlock = document.findBlock(text_cursor.selectionEnd()).next()  # next line
        next_line_text: str = next_line.text()  # next line text

        if not next_line.isValid():
            return

        text_cursor.beginEditBlock()  # start edit group

        selection_text: str = text_cursor.selectedText()  # selected lines tex

        text_cursor.removeSelectedText()  # remove lines
        text_cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor)  # select next line
        text_cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        text_cursor.insertText(f"{next_line_text}\n{selection_text}")  # insert text

        # reposition cursor & restore selection
        text_cursor.setPosition(text_cursor.position() - selection_length + relative_start_position,
                                QTextCursor.MoveAnchor)
        text_cursor.setPosition(text_cursor.position() + old_selection_length, QTextCursor.KeepAnchor)

        text_cursor.endEditBlock()  # end edit group
        self.setTextCursor(text_cursor)

    def zoomIn(self, range: int = ...) -> None:
        """
        Zoom in

        :param range:
        :type range:
        :return:
        :rtype:
        """
        font_size = self.font.pointSize()
        self.font.setPointSize(font_size + 1)
        self.setFont(self.font)

    def zoomOut(self, range: int = ...) -> None:
        """
        Zoom out

        :param range:
        :type range:
        :return:
        :rtype:
        """

        font_size = self.font.pointSize()
        self.font.setPointSize(font_size - 1)
        self.setFont(self.font)

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
        text_cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
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
        text_cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
        if line_text.startswith("# "):
            offset: int = 2
        else:
            offset: int = 1
        text_cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor, offset)
        text_cursor.removeSelectedText()

    @staticmethod
    def enlarge_selection(text_cursor: QTextCursor) -> int:
        """
        Enlarge current selection from the start of the first line
        to the end of the last line

        :param text_cursor: current text cursor
        :type text_cursor: QTextCursor
        :return: length of the selection
        :rtype: int
        """
        selection_start: int = text_cursor.selectionStart()
        selection_end: int = text_cursor.selectionEnd()

        if selection_start == selection_end:
            text_cursor.movePosition(QTextCursor.StartOfBlock, QTextCursor.MoveAnchor)
            text_cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)

        else:
            # move to the start of the first selected line
            text_cursor.setPosition(selection_start, QTextCursor.MoveAnchor)
            text_cursor.movePosition(QTextCursor.StartOfBlock, QTextCursor.MoveAnchor)

            # move to the end of the last selected line
            text_cursor.setPosition(selection_end, QTextCursor.KeepAnchor)

            if text_cursor.positionInBlock() == 0:
                text_cursor.movePosition(QTextCursor.PreviousBlock, QTextCursor.KeepAnchor)

            text_cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)

        return text_cursor.selectionEnd() - text_cursor.selectionStart()

    @staticmethod
    def duplicate_selection(text_cursor: QTextCursor) -> None:
        """
        Duplicates current selected text

        :param text_cursor: text cursor
        :type text_cursor: QTextCursor
        :return: None
        :rtype: None
        """

        selection_text: str = text_cursor.selectedText()

        text_cursor.insertText(f"{selection_text}\u2029{selection_text}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = QMainWindow()
    t = BaseCodeEditor()
    main_win.setCentralWidget(t)
    main_win.show()
    sys.exit(app.exec_())
