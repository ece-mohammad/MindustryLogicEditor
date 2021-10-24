#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import pathlib
import sys
from typing import Optional

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class MindustryLogicEdit(QMainWindow):
    """
    Mindustry (game) logic editor

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
        """Initialize Mindustry editor instance"""

        super(MindustryLogicEdit, self).__init__(*args, **kwargs)

        # ----------------------------------------------------------------------
        # --------------------------- GUI components ---------------------------
        # ----------------------------------------------------------------------

        self.editor: QTextEdit = QTextEdit()  # editor
        self.vert_layout: QVBoxLayout = QVBoxLayout()  # layout
        self.container: QWidget = QWidget()  # container
        self.status_bar: QStatusBar = QStatusBar()  # status bar
        self.file_menu: QMenu = QMenu("&File")  # file menu
        self.edit_menu: QMenu = QMenu("&Edit")  # edit menu
        self.file_toolbar = QToolBar("File")  # file toolbar
        self.edit_toolbar = QToolBar("Edit")  # edit toolbar

        # current file path
        self.path: Optional[pathlib.Path] = None

        # add editor to container
        self.vert_layout.addWidget(self.editor)
        self.container.setLayout(self.vert_layout)

        # set container as central widget
        self.setCentralWidget(self.container)

        # ----------------------------------------------------------------------
        # ---------------------- configure GUI components ----------------------
        # ----------------------------------------------------------------------

        # accept rich text (for coloring)
        self.editor.setAcceptRichText(True)

        # set editor font
        self.font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.font.setPointSize(14)
        self.editor.setFont(self.font)

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

        # cut
        cut_action = QAction(
            QIcon(os.path.join("images", "cut-text.png")),
            "Cut selected text...",
            self
        )
        cut_action.triggered.connect(self.editor.cut)
        cut_shortcut = QKeySequence(Qt.CTRL + Qt.Key_X)
        cut_action.setShortcut(cut_shortcut)
        self.edit_menu.addAction(cut_action)
        self.edit_toolbar.addAction(cut_action)

        # copy
        copy_action = QAction(
            QIcon(os.path.join("images", "copy-text.png")),
            "Copy selected text...",
            self
        )
        copy_action.triggered.connect(self.editor.copy)
        copy_shortcut = QKeySequence(Qt.CTRL + Qt.Key_C)
        copy_action.setShortcut(copy_shortcut)
        self.edit_menu.addAction(copy_action)
        self.edit_toolbar.addAction(copy_action)

        # paste
        paste_action = QAction(
            QIcon(os.path.join("images", "paste-text.png")),
            "Paste text from clipboard...",
            self
        )
        paste_action.triggered.connect(self.editor.paste)
        paste_shortcut = QKeySequence(Qt.CTRL + Qt.Key_V)
        paste_action.setShortcut(paste_shortcut)
        self.edit_menu.addAction(paste_action)
        self.edit_toolbar.addAction(paste_action)

        # add separator
        self.edit_toolbar.addSeparator()
        self.edit_menu.addSeparator()

        # undo
        undo_action = QAction(
            QIcon(os.path.join("images", "undo.png")),
            "Undo last change...",
            self
        )
        undo_action.triggered.connect(self.editor.undo)
        undo_shortcut = QKeySequence(Qt.CTRL + Qt.Key_Z)
        undo_action.setShortcut(undo_shortcut)
        self.edit_menu.addAction(undo_action)
        self.edit_toolbar.addAction(undo_action)

        # redo
        redo_action = QAction(
            QIcon(os.path.join("images", "redo.png")),
            "Redo last change...",
            self
        )
        redo_action.triggered.connect(self.editor.redo)
        redo_shortcut = QKeySequence(Qt.CTRL + Qt.Key_Y)
        redo_action.setShortcut(redo_shortcut)
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
        editor_title = "Mindustry Logic IDE"
        if self.path is None:
            editor_title = f"new file* | {editor_title}"
        else:
            editor_title = f"{str(self.path)} | {editor_title}"
        self.setWindowTitle(editor_title)

    def create_new_file(self) -> None:
        """new editor file"""
        self.editor.clear()
        self.path = None
        self.update_title()

    def open_file(self) -> None:
        """Open an existing file"""
        new_file, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            str(pathlib.Path.cwd()),
            "mindustry logic (*.mlog); text files (*.txt), All files (*.*)",
        )

        if new_file:
            try:
                with open(new_file, "r") as file_handle:
                    file_content = file_handle.read()
            except Exception as exc:
                self.show_error(str(exc))

            else:
                self.path = pathlib.Path(new_file)
                self.editor.setPlainText(file_content)
                self.update_title()

    def save_file(self) -> None:
        """Save current open file"""
        if self.path is None:
            return self.save_file_as()
        self._save_file(self.path)

    def save_file_as(self) -> None:
        """Save current file as another file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File As",
            str(pathlib.Path.cwd()),
            "mindustry logic (*.mlog); text files (*.txt), All files (*.*)"
        )

        if file_path is not None and len(file_path) > 0:
            self._save_file(pathlib.Path(file_path))

    def _save_file(self, file_path: pathlib.Path) -> None:
        """Private method to save files"""
        current_text = self.editor.toPlainText()

        try:
            with open(file_path, "w") as file_handle:
                file_handle.write(current_text)

        except Exception as exc:
            self.show_error(str(exc))

        else:
            self.path = file_path
            self.update_title()

    def select_all_text(self):
        """Select all text in editor"""
        self.editor.selectAll()

    def copy_selected_text(self):
        """Copy selected text"""
        ...

    def cut_selected_text(self):
        """Cut selected text"""
        ...

    def paste_text_from_clipboard(self) -> None:
        """Paste text from clipboard into editor"""
        ...


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MindustryLogicEdit()
    win.show()
    sys.exit(app.exec_())
