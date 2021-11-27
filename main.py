#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pathlib
import sys
import logging as log
import inspect

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from mindustry_editor import MindustryLogicEditor
from find_replace_widget import FindAndReplaceWidget, SearchFlags


class MainWindow(QMainWindow):
    """Mindustry Logic Editor main window"""

    def __init__(self, *args, **kwargs):
        """Initialize Mindustry editor instance"""

        super(MainWindow, self).__init__(*args, **kwargs)

        # auo save interval
        self.auto_save_interval: int = 6000 * 1000

        # auto save timer (id: 1)
        self.startTimer(self.auto_save_interval, Qt.VeryCoarseTimer)

        self.logger: log.Logger = log.getLogger(self.__class__.__name__)

        # --------------------------- GUI components ---------------------------

        self.container: QWidget = QWidget(parent=self)  # container

        self.tab_widget: QTabWidget = QTabWidget()  # tab widget

        self.find_and_replace_widget: FindAndReplaceWidget = FindAndReplaceWidget(self)
        self.find_and_replace_widget.setHidden(True)

        self.status_bar: QStatusBar = QStatusBar()  # status bar
        self.file_menu: QMenu = QMenu("&File")  # file menu
        self.edit_menu: QMenu = QMenu("&Edit")  # edit menu
        self.file_toolbar = QToolBar("File")  # file toolbar
        self.edit_toolbar = QToolBar("Edit")  # edit toolbar

        # configure container (tab widget)
        self.tab_widget.setTabsClosable(True)  # set tabs closable
        self.tab_widget.setMovable(True)  # set tabs movable
        self.tab_widget.setDocumentMode(True)  # set document mode
        self.tab_widget.tabCloseRequested.connect(self.close_tab)  # connect tab close request signal
        self.tab_widget.currentChanged.connect(self.current_tab_changed)  # connect current tab changed

        # ------------------------------- Layout -------------------------------

        layout: QVBoxLayout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        layout.addWidget(self.find_and_replace_widget)
        self.container.setLayout(layout)

        # set container as central widget
        self.setCentralWidget(self.container)

        # ---------------------- configure GUI components ----------------------

        # configure toolbars icon size
        self.file_toolbar.setIconSize(QSize(30, 30))
        self.edit_toolbar.setIconSize(QSize(30, 30))

        # add menu bars
        self.menuBar().addMenu(self.file_menu)
        self.menuBar().addMenu(self.edit_menu)

        # add toolbars
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
        new_file_shortcut = QKeySequence(Qt.CTRL | Qt.Key_N)
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
        open_file_shortcut = QKeySequence(Qt.CTRL | Qt.Key_O)
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
        save_file_shortcut = QKeySequence(Qt.CTRL | Qt.Key_S)
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
        save_file_as_shortcut = QKeySequence(Qt.CTRL | Qt.SHIFT | Qt.Key_S)
        save_file_as_action.setShortcut(save_file_as_shortcut)
        self.file_menu.addAction(save_file_as_action)
        self.file_toolbar.addAction(save_file_as_action)

        # add separator
        self.file_menu.addSeparator()

        # close tab action
        switch_tab_action = QAction("Switch current tab", self)
        switch_tab_action.setStatusTip("Switch current tab")
        switch_tab_action.triggered.connect(self.switch_tab)
        switch_tab_shortcut = QKeySequence(Qt.CTRL | Qt.Key_Tab)
        switch_tab_action.setShortcut(switch_tab_shortcut)

        # close tab action
        close_tab_action = QAction("Close current tab", self)
        close_tab_action.setStatusTip("Close current tab")
        close_tab_action.triggered.connect(self.close_current_tab)
        close_tab_shortcut = QKeySequence(Qt.CTRL | Qt.Key_W)
        close_tab_action.setShortcut(close_tab_shortcut)
        self.file_menu.addAction(close_tab_action)

        # add separator
        self.file_menu.addSeparator()

        # exit
        exit_action = QAction("Exit", self)
        exit_action.setStatusTip("Exit editor")
        exit_action.triggered.connect(self.close_editor)
        exit_shortcut = QKeySequence(Qt.CTRL | Qt.Key_Q)
        exit_action.setShortcut(exit_shortcut)
        self.file_menu.addAction(exit_action)

        # ------------------------- edit menu actions --------------------------

        # select all
        self.select_all_action = QAction(
            QIcon(os.path.join("images", "select-all.png")),
            "Select all text...",
            self
        )

        select_all_shortcut = QKeySequence(Qt.CTRL | Qt.Key_A)
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

        # Find and replace
        find_and_replace_action = QAction(
            QIcon(os.path.join("images", "search.png")),
            "Find and replace",
            self
        )
        find_and_replace_shortcut = QKeySequence(Qt.CTRL | Qt.Key_F)
        find_and_replace_action.setShortcut(find_and_replace_shortcut)
        find_and_replace_action.triggered.connect(self.pop_find_and_replace_widget)

        self.edit_menu.addAction(find_and_replace_action)
        self.edit_toolbar.addAction(find_and_replace_action)

        # ----------------------------- Status bar -----------------------------

        # add status bar
        self.setStatusBar(self.status_bar)

        # -------------------------- Signals & Slots ---------------------------
        self.find_and_replace_widget.SearchQuery.connect(self.editor_find_string)
        self.find_and_replace_widget.ReplaceQuery.connect(self.editor_replace_string)

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

    def bind_editor_shortcuts(self, editor: MindustryLogicEditor) -> None:
        """
        Bind window shortcuts (select, copy, paste, undo, redo) to editor instance

        :param editor: editor instance
        :type editor: MindustryLogicEditor
        :return: None
        :rtype: None
        """
        self.select_all_action.triggered.connect(editor.selectAll)
        self.cut_action.triggered.connect(editor.cut)
        self.copy_action.triggered.connect(editor.copy)
        self.paste_action.triggered.connect(editor.paste)
        self.undo_action.triggered.connect(editor.undo)
        self.redo_action.triggered.connect(editor.redo)
        editor.modificationChanged.connect(self.editor_content_changed)

    def update_title(self) -> None:
        """Update editor window title"""

        editor_title: str = "Mindustry Logic IDE"
        current_editor: MindustryLogicEditor = self.get_current_editor()

        if current_editor is None:
            return

        if not isinstance(current_editor, MindustryLogicEditor):
            self.logger.error("Not instance!!")
            return

        editor_path: pathlib.Path = current_editor.path
        open_file_name: str = current_editor.get_open_file_name()

        if current_editor.is_modified():
            open_file_name = f"{open_file_name} *"

        if editor_path is None:
            editor_title = f"new file * | {editor_title}"
            open_file_name = "new file *"
            self.tab_widget.tabBar().setTabTextColor(self.tab_widget.currentIndex(), Qt.red)
        elif current_editor.is_modified():
            editor_title = f"{str(editor_path)} * | {editor_title}"
            self.tab_widget.tabBar().setTabTextColor(self.tab_widget.currentIndex(), Qt.red)
        else:
            editor_title = f"{str(editor_path)} | {editor_title}"
            self.tab_widget.tabBar().setTabTextColor(self.tab_widget.currentIndex(), Qt.black)

        self.setWindowTitle(editor_title)
        self.tab_widget.setTabText(self.tab_widget.currentIndex(), open_file_name)

        self.logger.debug(f"Updating title for {open_file_name=}")

    def create_new_file(self) -> None:
        """new editor file"""
        self.add_editor_tab()
        editor: MindustryLogicEditor = self.get_current_editor()
        editor.setObjectName(f"tab#{self.tab_widget.currentIndex()}")
        editor.create_new_file()
        editor.setFocus()
        self.update_title()
        self.logger.debug(f"New file created in tab: {self.tab_widget.currentIndex()}")

    def open_file(self) -> None:
        """Open an existing file"""
        self.logger.debug(f"Opening a file")

        update_enable: bool = self.tab_widget.updatesEnabled()
        self.tab_widget.setUpdatesEnabled(False)

        current_editor: MindustryLogicEditor = self.get_current_editor()

        # check if there is an open file (not a new file)
        new_tab: bool = False
        if current_editor.path is not None:
            self.add_editor_tab()
            new_tab: bool = True
            current_editor: MindustryLogicEditor = self.get_current_editor()

        # disable current editor GUI updates
        current_editor.setUpdatesEnabled(False)

        # open file
        current_editor.open_file()

        # open was canceled
        if current_editor.path is None:
            self.logger.debug(f"Open file as cancelled")
            if new_tab:
                self.close_current_tab()
            return

        # get current file name & tab index
        file_name: str = current_editor.get_open_file_name()
        current_tab: int = self.tab_widget.currentIndex()

        # check if there is a file already opened with the same name
        for tab_index in range(self.tab_widget.count()):

            # skip current tab
            if tab_index == current_tab:
                continue

            tab_editor: MindustryLogicEditor = self.tab_widget.widget(tab_index)  # editor in the tab

            # skip new files
            if tab_editor.path is None:
                continue

            tab_file_name: str = tab_editor.get_open_file_name()  # file open in the tab
            if tab_file_name == file_name:
                self.logger.debug(f"file {file_name} is already open in tab: {tab_index}")
                self.tab_widget.setCurrentIndex(tab_index)
                other_editor: MindustryLogicEditor = self.get_current_editor()  # get other file's editor
                other_editor.create_new_file()
                self.update_title()
                break

        self.tab_widget.setCurrentIndex(current_tab)
        current_editor.setUpdatesEnabled(True)
        current_editor.setFocus()  # set focus on current tab editor

        self.tab_widget.setUpdatesEnabled(update_enable)
        self.update_title()  # update window title

        self.logger.debug(f"File opened: {file_name} in tab {current_tab}")

    def save_file(self) -> None:
        """Save current open file"""
        self.get_current_editor().save_file()
        self.update_title()
        self.logger.debug(f"File saved")

    def save_file_as(self) -> None:
        """Save current file as another file"""
        self.get_current_editor().save_file_as()
        self.update_title()
        self.logger.debug(f"File save as")

    def add_editor_tab(self) -> None:
        """
        Add an editor in a new tab

        :return: None
        :rtype: None
        """
        # disable GUI updates for current editor, if it exists
        current_editor: MindustryLogicEditor = self.get_current_editor()
        if current_editor is not None:
            current_editor.setUpdatesEnabled(False)

        # create a new editor instance
        editor: MindustryLogicEditor = MindustryLogicEditor()
        editor.setAttribute(Qt.WA_DeleteOnClose, True)
        self.bind_editor_shortcuts(editor)

        # add new tab
        self.tab_widget.setUpdatesEnabled(False)
        tab_index: int = self.tab_widget.addTab(
            editor,
            QIcon(os.path.join("images", "file.png")),
            editor.get_open_file_name()
        )
        self.tab_widget.setCurrentIndex(tab_index)
        self.tab_widget.setUpdatesEnabled(True)
        self.logger.debug(f"Added a new editor in tab: {tab_index}")

    def get_current_editor(self) -> MindustryLogicEditor:
        """
        Get current active text editor

        :return: active text edit
        :rtype: MindustryLogicEditor
        """
        return self.tab_widget.currentWidget()

    def close_current_tab(self) -> None:
        """
        Close current open tab

        :return: None
        :rtype: None
        """

        current_editor: MindustryLogicEditor = self.get_current_editor()
        current_file_name: str = current_editor.get_open_file_name()

        self.logger.debug(f"Closing current tab {self.tab_widget.currentIndex()}: {current_file_name}")

        if current_editor.is_modified():
            confirm_save: int = self.confirm_message(f"Save file {current_file_name} before closing?")
            if confirm_save == QMessageBox.Cancel:
                return
            elif confirm_save == QMessageBox.Yes:
                self.save_file()
            else:  # QMessageBox.No
                pass

        self.close_tab(self.tab_widget.currentIndex())

    def close_editor(self) -> None:
        """
        Close editor window

        :return: None
        :rtype: None
        """
        self.close()

    def switch_tab(self) -> None:
        """
        switch current tab

        :return: None
        :rtype: None
        """
        current_tab_index: int = self.tab_widget.currentIndex()
        new_tab_index: int = (current_tab_index + 1) % self.tab_widget.count()
        self.tab_widget.setCurrentIndex(new_tab_index)
        self.logger.debug(f"Switching tabs from {current_tab_index} to {new_tab_index}")

    def closeEvent(self, event: QCloseEvent) -> None:
        close_confirm: int = self.confirm_message(f"Any unsaved files will be discarded. Confirm closing the editor?")

        if close_confirm in (QMessageBox.Cancel, QMessageBox.No):
            return

        for tab_index in range(self.tab_widget.count()):
            tab_editor: MindustryLogicEditor = self.tab_widget.widget(tab_index)
            tab_editor.close()
            tab_editor.deleteLater()

        self.logger.debug(f"Closing the editor")

        super(MainWindow, self).closeEvent(event)

    def timerEvent(self, event: QTimerEvent):
        """
        Handle timer event

        :param event: Timer event
        :type event: QTimerEvent
        :return: None
        :rtype: None
        """
        super(MainWindow, self).timerEvent(event)
        current_editor: MindustryLogicEditor = self.get_current_editor()
        current_editor.auto_save()
        self.update_title()
        self.logger.debug(f"Timer event: auto save")

    def pop_find_and_replace_widget(self) -> None:
        """
        show find and replace widget

        :return:
        :rtype:
        """
        if self.find_and_replace_widget.isHidden():
            self.find_and_replace_widget.setHidden(False)

    @pyqtSlot(int)
    def close_tab(self, tab_index: int) -> None:
        """
        Close current open tab

        :param tab_index: current tab index
        :type tab_index: int
        :return: None
        :rtype: None
        """
        editor: MindustryLogicEditor = self.tab_widget.widget(tab_index)
        editor.close()
        self.tab_widget.removeTab(tab_index)
        if self.tab_widget.count() < 1:
            self.create_new_file()

    @pyqtSlot(bool)
    def editor_content_changed(self, changed: bool):
        if changed:
            self.update_title()

    @pyqtSlot(int)
    def current_tab_changed(self, new_tab_index: int) -> None:
        """Current tab was changed"""
        if new_tab_index > -1:

            for tab_index in range(self.tab_widget.count()):
                self.tab_widget.widget(tab_index).setUpdatesEnabled(False)

            self.tab_widget.widget(new_tab_index).setUpdatesEnabled(True)
            self.update_title()

    @pyqtSlot(str, SearchFlags)
    def editor_find_string(self, search_expr: str, search_flags: SearchFlags) -> None:
        """
        Search open document for a given string

        :param search_expr:
        :type search_expr:
        :param search_flags:
        :type search_flags:
        :return:
        :rtype:
        """
        editor: MindustryLogicEditor = self.get_current_editor()
        if search_flags & SearchFlags.AllOccurrences:
            result = editor.find_all(search_expr, search_flags)
        else:
            result = editor.find_string(search_expr, search_flags)

        self.status_bar.showMessage(f"Found {result} results")

    @pyqtSlot(str, str, SearchFlags)
    def editor_replace_string(self, search_expr: str, replace_expr: str, search_flags: SearchFlags) -> None:
        """
        Replace a string with a given replacement

        :param search_expr:
        :type search_expr:
        :param replace_expr:
        :type replace_expr:
        :param search_flags:
        :type search_flags:
        :return:
        :rtype:
        """
        editor: MindustryLogicEditor = self.get_current_editor()
        result: int = 0
        if search_flags & SearchFlags.AllOccurrences:
            result = editor.replace_all(search_expr, replace_expr, search_flags)
        else:
            result = editor.replace_string(search_expr, replace_expr, search_flags)

        self.status_bar.showMessage(f"Replaced {result} occurrences")


if __name__ == "__main__":
    log.basicConfig(
        stream=sys.stdout,
        level=log.DEBUG,
        format="[%(name)s] %(funcName)s:%(lineno)d %(message)s"
    )

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("images\\icon.ico"))
    win = MainWindow()
    win.setWindowIcon(QIcon("images\\icon.ico"))
    win.showMaximized()
    sys.exit(app.exec_())
