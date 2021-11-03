#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import pathlib
import sys
from typing import Dict, Optional

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from editor import MindustryLogicEditor


class MainWindow(QMainWindow):
    """Mindustry Logic Editor main window"""

    def __init__(self, *args, **kwargs):
        """Initialize Mindustry editor instance"""

        super(MainWindow, self).__init__(*args, **kwargs)

        # ----------------------------------------------------------------------
        # --------------------------- GUI components ---------------------------
        # ----------------------------------------------------------------------

        # text editor
        self.container: QTabWidget = QTabWidget()  # container (tab widget)

        self.status_bar: QStatusBar = QStatusBar()  # status bar
        self.file_menu: QMenu = QMenu("&File")  # file menu
        self.edit_menu: QMenu = QMenu("&Edit")  # edit menu
        self.file_toolbar = QToolBar("File")  # file toolbar
        self.edit_toolbar = QToolBar("Edit")  # edit toolbar

        # title update interval
        self.title_update_interval: int = 0  # as soon as no QEvents are queued
        self.startTimer(self.title_update_interval)

        # configure container (tab widget)
        self.container.setTabsClosable(True)  # set tabs closable
        self.container.setMovable(True)  # set tabs movable
        self.container.setDocumentMode(True)  # set document mode
        self.container.tabCloseRequested.connect(self.close_current_tab)  # connect tab close request signal

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

        # close tab action
        switch_tab_action = QAction("Switch current tab", self)
        switch_tab_action.setStatusTip("Switch current tab")
        switch_tab_action.triggered.connect(self.switch_tab)
        switch_tab_shortcut = QKeySequence(Qt.CTRL + Qt.Key_Tab)
        switch_tab_action.setShortcut(switch_tab_shortcut)

        # close tab action
        close_tab_action = QAction("Close current tab", self)
        close_tab_action.setStatusTip("Close current tab")
        close_tab_action.triggered.connect(self.close_tab)
        close_tab_shortcut = QKeySequence(Qt.CTRL + Qt.Key_W)
        close_tab_action.setShortcut(close_tab_shortcut)
        self.file_menu.addAction(close_tab_action)

        # add separator
        self.file_menu.addSeparator()

        # exit
        exit_action = QAction("Exit", self)
        exit_action.setStatusTip("Exit editor")
        exit_action.triggered.connect(self.close_editor)
        exit_shortcut = QKeySequence(Qt.CTRL + Qt.Key_Q)
        exit_action.setShortcut(exit_shortcut)
        self.file_menu.addAction(exit_action)

        # ------------------------- edit menu actions --------------------------

        # select all
        self.select_all_action = QAction(
            QIcon(os.path.join("images", "select-all.png")),
            "Select all text...",
            self
        )

        select_all_shortcut = QKeySequence(Qt.CTRL + Qt.Key_A)
        self.select_all_action.setShortcut(select_all_shortcut)
        self.edit_menu.addAction(self.select_all_action)
        self.edit_toolbar.addAction(self.select_all_action)

        # cut (shortcut already implemented)
        self.cut_action = QAction(
            QIcon(os.path.join("images", "cut-text.png")),
            "Cut selected text...",
            self
        )
        self.edit_menu.addAction(self.cut_action)
        self.edit_toolbar.addAction(self.cut_action)

        # copy (shortcut already implemented)
        self.copy_action = QAction(
            QIcon(os.path.join("images", "copy-text.png")),
            "Copy selected text...",
            self
        )
        self.edit_menu.addAction(self.copy_action)
        self.edit_toolbar.addAction(self.copy_action)

        # paste (shortcut already implemented)
        self.paste_action = QAction(
            QIcon(os.path.join("images", "paste-text.png")),
            "Paste text from clipboard...",
            self
        )
        self.edit_menu.addAction(self.paste_action)
        self.edit_toolbar.addAction(self.paste_action)

        # add separator
        self.edit_toolbar.addSeparator()
        self.edit_menu.addSeparator()

        # undo (shortcut already implemented)
        self.undo_action = QAction(
            QIcon(os.path.join("images", "undo.png")),
            "Undo last change...",
            self
        )
        self.edit_menu.addAction(self.undo_action)
        self.edit_toolbar.addAction(self.undo_action)

        # redo (shortcut already implemented)
        self.redo_action = QAction(
            QIcon(os.path.join("images", "redo.png")),
            "Redo last change...",
            self
        )
        self.edit_menu.addAction(self.redo_action)
        self.edit_toolbar.addAction(self.redo_action)

        # add separator
        self.edit_toolbar.addSeparator()
        self.edit_menu.addSeparator()

        # ----------------------------- Status bar -----------------------------
        # add status bar
        self.setStatusBar(self.status_bar)

        # ----------------------------------------------------------------------
        # -------------------------- show main window --------------------------
        # ----------------------------------------------------------------------
        # show main window
        self.update_title()

        # create new file
        self.create_new_file()

    def show_error(self, message: str) -> None:
        """Show error in a message box to user"""
        error: QMessageBox = QMessageBox(parent=self)
        error.setText(message)
        error.setIcon(QMessageBox.Critical)
        error.exec_()

    def confirm_message(self, message_text: str) -> int:
        """
        Confirm message, sho message to user with 'OK' and 'Cancel' options

        :param message_text: message to show to the user
        :type message_text: str
        :return: QMessageBox.Save, QMessageBox.Discard, QMessageBox.Cancel
        :rtype: QMessageBox.StandardButton (int)
        """
        message: QMessageBox = QMessageBox(parent=self)
        message.setText(message_text)
        message.setIcon(QMessageBox.Warning)
        message.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        return message.exec_()

    def bind_editor_shortcuts(self, editor: QTextEdit) -> None:
        """
        Bind window shortcuts (select, copy, paste, undo, redo) to editor instance

        :param editor: editor instance
        :type editor: QTextEdit
        :return: None
        :rtype: None
        """
        self.select_all_action.triggered.connect(editor.selectAll)
        self.cut_action.triggered.connect(editor.cut)
        self.copy_action.triggered.connect(editor.copy)
        self.paste_action.triggered.connect(editor.paste)
        self.undo_action.triggered.connect(editor.undo)
        self.redo_action.triggered.connect(editor.redo)

    def timerEvent(self, event: QTimerEvent) -> None:
        """
        Handle Timer event

        :param event: Timer event
        :type event: QTimerEvent
        :return: None
        :rtype: None
        """
        super(MainWindow, self).timerEvent(event)
        self.update_title()

    def update_title(self) -> None:
        """Update editor window title"""

        editor_title: str = "Mindustry Logic IDE"
        current_editor: MindustryLogicEditor = self.get_current_editor()

        if current_editor is None:
            return

        editor_path: pathlib.Path = current_editor.path
        open_file_name: str = current_editor.get_open_file_name()
        if current_editor.is_modified():
            open_file_name = f"{open_file_name} *"

        if editor_path is None:
            editor_title = f"new file * | {editor_title}"
        elif current_editor.is_modified():
            editor_title = f"{str(editor_path)} * | {editor_title}"
        else:
            editor_title = f"{str(editor_path)} | {editor_title}"

        self.setWindowTitle(editor_title)
        self.container.setTabText(self.container.currentIndex(), open_file_name)

    def create_new_file(self) -> None:
        """new editor file"""
        self.add_editor()
        self.get_current_editor().create_new_file()
        self.update_title()

    def open_file(self) -> None:
        """Open an existing file"""
        current_editor: MindustryLogicEditor = self.get_current_editor()
        if current_editor.path is not None:
            self.add_editor()
        self.get_current_editor().open_file()
        self.update_title()

    def save_file(self) -> None:
        """Save current open file"""
        self.get_current_editor().save_file()
        self.update_title()

    def save_file_as(self) -> None:
        """Save current file as another file"""
        self.get_current_editor().save_file_as()
        self.update_title()

    def add_editor(self) -> None:
        """
        Add an editor in a new tab

        :return: None
        :rtype: None
        """

        # create a new editor instance
        editor = MindustryLogicEditor()

        # add new tab
        tab_index: int = self.container.addTab(
            editor,
            QIcon(os.path.join("images", "file.png")),
            editor.get_open_file_name()
        )

        # add editor to open editors
        self.bind_editor_shortcuts(editor)
        self.container.setCurrentIndex(tab_index)
        editor.setFocus()

    def get_current_editor(self) -> MindustryLogicEditor:
        """
        Get current active text editor

        :return: active text edit
        :rtype: QTextEdit
        """
        return self.container.currentWidget()

    def close_tab(self) -> None:
        """
        Close current open tab

        :return: None
        :rtype: None
        """
        current_editor: MindustryLogicEditor = self.get_current_editor()
        if current_editor.is_modified():
            confirm_save: int = self.confirm_message(f"Save file {current_editor.get_open_file_name()} before closing?")
            if confirm_save == QMessageBox.Cancel:
                return
            elif confirm_save == QMessageBox.Yes:
                self.save_file()
            else:  # QMessageBox.No
                pass  # don't save file

        self.close_current_tab(self.container.currentIndex())

    def close_editor(self) -> None:
        """
        Close editor window

        :return: None
        :rtype: None
        """

        close_confirm: int = self.confirm_message(f"Any unsaved files will be discarded. Confirm closing the editor?")

        if close_confirm in (QMessageBox.Cancel, QMessageBox.No):
            return

        for tab_index in range(self.container.count()):
            tab_editor: MindustryLogicEditor = self.container.widget(tab_index)
            tab_editor.close()

        self.close()

    def switch_tab(self) -> None:
        """
        switch current tab

        :return: None
        :rtype: None
        """
        current_tab_index: int = self.container.currentIndex()
        new_tab_index: int = (current_tab_index + 1) % self.container.count()
        self.container.setCurrentIndex(new_tab_index)

    @Slot(int)
    def close_current_tab(self, tab_index: int) -> None:
        """
        Close current open tab

        :param tab_index: current tab index
        :type tab_index: int
        :return: None
        :rtype: None
        """
        self.get_current_editor().close()
        self.container.removeTab(tab_index)

        if self.container.count() < 1:
            self.add_editor()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("images\\icon.ico"))
    win = MainWindow()
    win.setWindowIcon(QIcon("images\\icon.ico"))
    win.showMaximized()
    sys.exit(app.exec_())
