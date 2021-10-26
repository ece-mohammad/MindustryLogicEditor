#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import pathlib
import sys

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from editor import MindustryLogicEditor
from highlighter import MindustryLogicSyntaxHighlighter


class MainWindow(QMainWindow):
    """Mindustry Logic Editor main window"""

    def __init__(self, *args, **kwargs):
        """Initialize Mindustry editor instance"""

        super(MainWindow, self).__init__(*args, **kwargs)

        # ----------------------------------------------------------------------
        # --------------------------- GUI components ---------------------------
        # ----------------------------------------------------------------------

        self.editor: MindustryLogicEditor = MindustryLogicEditor()  # editor
        self.highlighter = MindustryLogicSyntaxHighlighter(self.editor.document())
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
