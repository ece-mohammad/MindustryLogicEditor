#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
import os
import pathlib
import sys
from typing import List, Optional, Union

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class LineNumberArea(QWidget):
    """Mindustry Logic Editor line number area"""

    def __init__(self, editor, *args, **kwarg):
        super(LineNumberArea, self).__init__(*args, **kwarg)
        self.editor: Union[QTextEdit, MindustryLogicEditor] = editor

    def sizeHint(self) -> QSize:
        return QSize(self.editor.get_line_number_area_width(), 0)

    def paintEvent(self, event: QPaintEvent) -> None:
        self.editor.line_number_area_paint_event(event)


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
        """Initialize mindustry logic editor instance"""
        super(MindustryLogicEditor, self).__init__(*args, **kwargs)

        # ----------------------------------------------------------------------
        # ------------------------- Editor components --------------------------
        # ----------------------------------------------------------------------

        # line number area
        self.line_number_area: LineNumberArea = LineNumberArea(editor=self, parent=self)

        # current file path
        self.path: Optional[pathlib.Path] = None

        # ----------------------------------------------------------------------
        # ---------------------- configure GUI components ----------------------
        # ----------------------------------------------------------------------

        # set editor font
        self.font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.font.setPointSize(14)
        self.setFont(self.font)

        # ----------------------- connect editor signals -----------------------
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        # ------------------------------- start --------------------------------
        self.update_line_number_area_width(0)
        self.highlight_current_line()

    def create_new_file(self) -> None:
        """create new file"""
        self.clear()
        self.path = None

    def open_file(self) -> None:
        """Open an existing file"""
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
        """Save current file"""
        if self.path is None:
            return self.save_file_as()
        self._save_file(self.path)

    def save_file_as(self) -> None:
        """Save current file as"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File As",
            str(pathlib.Path.cwd()),
            "Mindustry Logic (*.mlog);;Text Files (*.txt);;All Files (*.*)",
        )

        if file_path is not None and len(file_path) > 0:
            self._save_file(pathlib.Path(file_path))

    def _save_file(self, file_path: pathlib.Path) -> None:
        """Private method to save files"""
        current_text = self.toPlainText()

        try:
            with open(file_path, "w") as file_handle:
                file_handle.write(current_text)

        except Exception as exc:
            self.show_error(str(exc))

        else:
            self.path = file_path

    def resizeEvent(self, event: QResizeEvent) -> None:
        """resize editor"""
        super(MindustryLogicEditor, self).resizeEvent(event)
        rect: QRect = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(
                rect.left(),
                rect.top(),
                self.get_line_number_area_width(),
                rect.height()
            )
        )

    def get_line_number_area_width(self) -> int:
        """calculate the width of the LineNumberArea widget"""
        block_count = max(1, self.blockCount())
        width_in_digits = math.floor(math.log10(block_count)) + 1
        width_in_pixels = 3 + self.fontMetrics().horizontalAdvance("9") * width_in_digits
        return width_in_pixels

    def line_number_area_paint_event(self, event: QPaintEvent) -> None:
        """paint line number area"""
        painter: QPainter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), Qt.lightGray)

        text_block: QTextBlock = self.firstVisibleBlock()
        block_number: int = text_block.blockNumber()
        top: int = round(self.blockBoundingGeometry(text_block).translated(self.contentOffset()).top())
        bottom: int = top + round(self.blockBoundingRect(text_block).height())

        while text_block.isValid() and top <= event.rect().bottom():
            if text_block.isVisible() and bottom >= event.rect().top():
                number: str = str(block_number + 1)
                painter.setPen(Qt.black)
                painter.drawText(
                    0,
                    top,
                    self.line_number_area.width(),
                    self.fontMetrics().height(),
                    Qt.AlignRight,
                    number
                )

            text_block = text_block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(text_block).height())
            block_number += 1

    @Slot(int)
    def update_line_number_area_width(self, new_block_count: int):
        """ update the width of the line number area"""
        self.setViewportMargins(self.get_line_number_area_width(), 0, 0, 0)

    @Slot(QRect, int)
    def update_line_number_area(self, rect: QRect, dy: int) -> None:
        """called when editors viewport has been scrolled"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    @Slot()
    def highlight_current_line(self):
        """Highlight current line"""
        extra_selections: List[QTextEdit.ExtraSelection] = list()

        if self.isReadOnly():
            return

        selection: QTextEdit.ExtraSelection = QTextEdit.ExtraSelection()
        line_color = QColor(Qt.yellow).lighter(160)
        selection.format.setBackground(line_color)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        extra_selections.append(selection)

        self.setExtraSelections(extra_selections)


class MainWindow(QMainWindow):
    """Mindustry Logic Editor main window"""

    def __init__(self, *args, **kwargs):
        """Initialize Mindustry editor instance"""

        super(MainWindow, self).__init__(*args, **kwargs)

        # ----------------------------------------------------------------------
        # --------------------------- GUI components ---------------------------
        # ----------------------------------------------------------------------

        self.editor: MindustryLogicEditor = MindustryLogicEditor()  # editor
        self.vert_layout: QVBoxLayout = QVBoxLayout()  # layout
        self.container: QWidget = QWidget()  # container
        self.status_bar: QStatusBar = QStatusBar()  # status bar
        self.file_menu: QMenu = QMenu("&File")  # file menu
        self.edit_menu: QMenu = QMenu("&Edit")  # edit menu
        self.file_toolbar = QToolBar("File")  # file toolbar
        self.edit_toolbar = QToolBar("Edit")  # edit toolbar

        # add editor to container
        self.vert_layout.addWidget(self.editor)
        self.container.setLayout(self.vert_layout)

        # set container as central widget
        self.setCentralWidget(self.container)

        # ----------------------------------------------------------------------
        # ---------------------- configure GUI components ----------------------
        # ----------------------------------------------------------------------

        # # configure toolbars icon size
        self.file_toolbar.setIconSize(QSize(30, 30))
        self.edit_toolbar.setIconSize(QSize(30, 30))

        # add menu bars
        self.menuBar().addMenu(self.file_menu)
        self.menuBar().addMenu(self.edit_menu)

        # # add toolbars
        self.addToolBar(self.file_toolbar)
        self.addToolBar(self.edit_toolbar)

        # ------------------------- file menu actions --------------------------
        # new file
        new_file_action = QAction(
            QIcon(os.path.join("images", "new-file.png")),
            "Create new file...",
            self
        )
        new_file_action.setStatusTip("New File")
        new_file_action.triggered.connect(self.create_new_file)
        new_file_shortcut = QKeySequence(Qt.CTRL + Qt.Key_N)
        new_file_action.setShortcut(new_file_shortcut)
        self.file_menu.addAction(new_file_action)
        self.file_toolbar.addAction(new_file_action)

        # open file
        open_file_action = QAction(
            QIcon(os.path.join("images", "open-file.png")),
            "Open file...",
            self
        )
        open_file_action.setStatusTip("Open File")
        open_file_action.triggered.connect(self.open_file)
        open_file_shortcut = QKeySequence(Qt.CTRL + Qt.Key_O)
        open_file_action.setShortcut(open_file_shortcut)
        self.file_menu.addAction(open_file_action)
        self.file_toolbar.addAction(open_file_action)

        # save file
        save_file_action = QAction(
            QIcon(os.path.join("images", "save-file.png")),
            "Save file...",
            self
        )
        save_file_action.setStatusTip("Save File")
        save_file_action.triggered.connect(self.save_file)
        save_file_shortcut = QKeySequence(Qt.CTRL + Qt.Key_S)
        save_file_action.setShortcut(save_file_shortcut)
        self.file_menu.addAction(save_file_action)
        self.file_toolbar.addAction(save_file_action)

        # save file as
        save_file_as_action = QAction(
            QIcon(os.path.join("images", "save-file-as.png")),
            "Save file as...",
            self
        )
        save_file_as_action.setStatusTip("Save File As")
        save_file_as_action.triggered.connect(self.save_file_as)
        save_file_as_shortcut = QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_S)
        save_file_as_action.setShortcut(save_file_as_shortcut)
        self.file_menu.addAction(save_file_as_action)
        self.file_toolbar.addAction(save_file_as_action)

        # add separator
        self.file_menu.addSeparator()

        # exit
        exit_action = QAction("Exit", self)
        exit_action.setStatusTip("Exit editor")
        exit_action.triggered.connect(self.close)
        exit_shortcut = QKeySequence(Qt.CTRL + Qt.Key_Q)
        exit_action.setShortcut(exit_shortcut)
        self.file_menu.addAction(exit_action)

        # ------------------------- edit menu actions --------------------------

        # select all
        select_all_action = QAction(
            QIcon(os.path.join("images", "select-all.png")),
            "Select all text...",
            self
        )
        select_all_action.triggered.connect(self.editor.selectAll)
        select_all_shortcut = QKeySequence(Qt.CTRL + Qt.Key_A)
        select_all_action.setShortcut(select_all_shortcut)
        self.edit_menu.addAction(select_all_action)
        self.edit_toolbar.addAction(select_all_action)

        # cut (shortcut already implemented)
        cut_action = QAction(
            QIcon(os.path.join("images", "cut-text.png")),
            "Cut selected text...",
            self
        )
        cut_action.triggered.connect(self.editor.cut)
        self.edit_menu.addAction(cut_action)
        self.edit_toolbar.addAction(cut_action)

        # copy (shortcut already implemented)
        copy_action = QAction(
            QIcon(os.path.join("images", "copy-text.png")),
            "Copy selected text...",
            self
        )
        copy_action.triggered.connect(self.editor.copy)
        self.edit_menu.addAction(copy_action)
        self.edit_toolbar.addAction(copy_action)

        # paste (shortcut already implemented)
        paste_action = QAction(
            QIcon(os.path.join("images", "paste-text.png")),
            "Paste text from clipboard...",
            self
        )
        paste_action.triggered.connect(self.editor.paste)
        self.edit_menu.addAction(paste_action)
        self.edit_toolbar.addAction(paste_action)

        # add separator
        self.edit_toolbar.addSeparator()
        self.edit_menu.addSeparator()

        # undo (shortcut already implemented)
        undo_action = QAction(
            QIcon(os.path.join("images", "undo.png")),
            "Undo last change...",
            self
        )
        undo_action.triggered.connect(self.editor.undo)
        self.edit_menu.addAction(undo_action)
        self.edit_toolbar.addAction(undo_action)

        # redo (shortcut already implemented)
        redo_action = QAction(
            QIcon(os.path.join("images", "redo.png")),
            "Redo last change...",
            self
        )
        redo_action.triggered.connect(self.editor.redo)
        self.edit_menu.addAction(redo_action)
        self.edit_toolbar.addAction(redo_action)

        # add separator
        self.edit_toolbar.addSeparator()
        self.edit_menu.addSeparator()

        # enable undo & redo
        self.editor.setUndoRedoEnabled(True)

        # ----------------------------- Status bar -----------------------------
        # add status bar
        self.setStatusBar(self.status_bar)

        # ----------------------------------------------------------------------
        # -------------------------- show main window --------------------------
        # ----------------------------------------------------------------------
        # show main window
        self.update_title()
        self.show()

    def show_error(self, message: str) -> None:
        """Show error in a message box to user"""
        error = QMessageBox(parent=self)
        error.setText(message)
        error.setIcon(QMessageBox.Critical)
        error.show()

    def update_title(self) -> None:
        """Update editor window title"""
        editor_title: str = "Mindustry Logic IDE"
        editor_path: pathlib.Path = self.editor.path

        if editor_path is None:
            editor_title = f"new file* | {editor_title}"
        else:
            editor_title = f"{str(editor_path)} | {editor_title}"

        self.setWindowTitle(editor_title)

    def create_new_file(self) -> None:
        """new editor file"""
        self.editor.create_new_file()
        self.update_title()

    def open_file(self) -> None:
        """Open an existing file"""
        self.editor.open_file()
        self.update_title()

    def save_file(self) -> None:
        """Save current open file"""
        self.editor.save_file()
        self.update_title()

    def save_file_as(self) -> None:
        """Save current file as another file"""
        self.editor.save_file_as()
        self.update_title()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
