#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import enum
import os
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class SearchFlags(enum.IntFlag):
    """
    Find and replace flags

    Members
        - NoFlags: search has no special flags
        - CaseSensitive: case sensitive search
        - WholeWord: match whole word only
        - Regex: treat search expression as a regular expression and return all occurrences that fulfill it
        - AllOccurrences: apply to all occurrences that match search expression
    """
    NoFlags = 0
    CaseSensitive = enum.auto()
    WholeWord = enum.auto()
    Regex = enum.auto()
    AllOccurrences = enum.auto()


class FindAndReplaceWidget(QWidget):
    """
    Non modal find and replace widget for QTextEdit

    pyqtSignals:
        - SearchQuery(str, SearchFlags): emitted when find or find all buttons are clicked
        - ReplaceQuery(str, str, SearchFlags): emitted when replace or replace all buttons are clicked
    """
    SearchQuery: pyqtSignal = pyqtSignal(str, SearchFlags)
    ReplaceQuery: pyqtSignal = pyqtSignal(str, str, SearchFlags)

    class StyleProxy(QProxyStyle):

        def sizeFromContents(self, type: QStyle.ContentsType, option: QStyleOption, size: QSize,
                             widget: QWidget) -> QSize:
            """
            Get widget size from its contents, overridden to increase push button width by 20

            :param type: content type
            :type type: QStyle.ContentsType
            :param option: style option
            :type option: QStyleOption
            :param size: contents size
            :type size: QSize
            :param widget: widget
            :type widget: QWidget
            :return: widget size from its contents
            :rtype: QSize
            """
            widget_size: QSize = super(FindAndReplaceWidget.StyleProxy, self).sizeFromContents(
                type,
                option,
                size,
                widget
            )

            if type == QStyle.ContentsType.CT_PushButton:
                widget_size.setWidth(widget_size.width() + 20)

            return widget_size

    def __init__(self, editor: QWidget, *args: Tuple[Any], **kwargs: Dict[str, Any]) -> None:
        """
        Initialize a find and replace widget

        :param editor: text editor instance
        :type editor: QTextEdit
        :param args: arguments list
        :type args: Tuple[Any]
        :param kwargs: keyword arguments
        :type kwargs: Dict[Any, Any]
        """
        super(FindAndReplaceWidget, self).__init__(*args, **kwargs)

        # container
        self.container: QWidget = editor

        # set minimum height
        self.setMinimumHeight(120)

        # set font size
        font = self.font()
        font.setPointSize(12)
        self.setFont(font)

        # layout
        self.widget_layout: QGridLayout = QGridLayout(self)
        self.setLayout(self.widget_layout)

        # ----------------------------------------------------------------------
        # -------------------------------- Find --------------------------------
        # ----------------------------------------------------------------------

        # find label
        self.find_label: QLabel = QLabel()
        self.find_label.setText("Find")

        # find text field (line edit)
        self.search_text: QLineEdit = QLineEdit(self)
        size_policy: QSizePolicy = self.search_text.sizePolicy()
        size_policy.setHorizontalPolicy(QSizePolicy.Expanding)
        self.search_text.setSizePolicy(size_policy)
        self.search_text.setToolTip("Find What?")

        # find next button
        self.find_next_button: QPushButton = QPushButton()
        self.find_next_button.setText("Find Next")
        self.find_next_button.setToolTip("Find Next")
        self.find_next_button.setStyle(FindAndReplaceWidget.StyleProxy())

        # find prev button
        self.mark_all_button: QPushButton = QPushButton()
        self.mark_all_button.setText("Mark All")
        self.mark_all_button.setToolTip("MarK All")
        self.mark_all_button.setStyle(FindAndReplaceWidget.StyleProxy())

        # close/hide button
        self.close_button: QPushButton = QPushButton()
        self.close_button.setIcon(QIcon(os.path.join("images", "close.png")))
        self.close_button.setFlat(True)
        self.close_button.setFlat(True)
        self.close_button.setToolTip("Close")
        self.close_button.clicked.connect(self.close)

        # case sensitive button
        self.case_sensitive_button: QPushButton = QPushButton()
        self.case_sensitive_button.setIcon(QIcon(os.path.join("images", "match-case.png")))
        self.case_sensitive_button.setFlat(True)
        self.case_sensitive_button.setCheckable(True)
        self.case_sensitive_button.setToolTip("Match Case")
        self.case_sensitive_button.setIconSize(QSize(20, 20))

        # whole word button
        self.whole_word_button: QPushButton = QPushButton()
        self.whole_word_button.setIcon(QIcon(os.path.join("images", "whole-word.png")))
        self.whole_word_button.setFlat(True)
        self.whole_word_button.setCheckable(True)
        self.whole_word_button.setToolTip("Match Whole Word")
        self.whole_word_button.setIconSize(QSize(20, 20))

        # regex button
        self.regex_button: QPushButton = QPushButton()
        self.regex_button.setIcon(QIcon(os.path.join("images", "regex.png")))
        self.regex_button.setFlat(True)
        self.regex_button.setCheckable(True)
        self.regex_button.setToolTip("Regular Expression")
        self.regex_button.setIconSize(QSize(20, 20))

        # ----------------------------------------------------------------------
        # ------------------------------ Replace -------------------------------
        # ----------------------------------------------------------------------

        # replace label
        self.replace_label: QLabel = QLabel()
        self.replace_label.setText("Replace")

        # replace text field (line edit)
        self.replace_text: QLineEdit = QLineEdit()
        size_policy: QSizePolicy = self.replace_text.sizePolicy()
        size_policy.setHorizontalPolicy(QSizePolicy.Expanding)
        self.replace_text.setSizePolicy(size_policy)
        self.replace_text.setToolTip("Replace With What?")

        # replace next button
        self.replace_next_button: QPushButton = QPushButton()
        self.replace_next_button.setText("Replace")
        self.replace_next_button.setToolTip("Replace Next")
        self.replace_next_button.setStyle(FindAndReplaceWidget.StyleProxy())

        # replace all button
        self.replace_all_button: QPushButton = QPushButton()
        self.replace_all_button.setText("Replace All")
        self.replace_all_button.setToolTip("Replace All")
        self.replace_all_button.setStyle(FindAndReplaceWidget.StyleProxy())

        # ----------------------------------------------------------------------
        # ---------------------------- Place items -----------------------------
        # ----------------------------------------------------------------------

        # add find buttons & labels
        self.widget_layout.addWidget(self.case_sensitive_button, 0, 0)
        self.widget_layout.addWidget(self.whole_word_button, 0, 1)
        self.widget_layout.addWidget(self.regex_button, 0, 2)
        self.widget_layout.addWidget(self.find_label, 0, 3)
        self.widget_layout.addWidget(self.search_text, 0, 4)
        self.widget_layout.addWidget(self.find_next_button, 0, 5)
        self.widget_layout.addWidget(self.mark_all_button, 0, 6)
        self.widget_layout.addWidget(self.close_button, 0, 76)

        # add replace buttons & labels
        self.widget_layout.addWidget(self.replace_label, 1, 3)
        self.widget_layout.addWidget(self.replace_text, 1, 4)
        self.widget_layout.addWidget(self.replace_next_button, 1, 5)
        self.widget_layout.addWidget(self.replace_all_button, 1, 6)

        # ----------------------------------------------------------------------
        # -------------------------- Connect Signals ---------------------------
        # ----------------------------------------------------------------------

        # find buttons
        self.find_next_button.clicked.connect(self.find_next_clicked)
        self.mark_all_button.clicked.connect(self.mark_all_button_clicked)

        # replace buttons
        self.replace_next_button.clicked.connect(self.replace_next_button_clicked)
        self.replace_all_button.clicked.connect(self.replace_all_button_clicked)

    def get_search_flags(self) -> SearchFlags:
        """
        Get current search criteria

        :return: search flags
        :rtype: SearchFlags
        """
        search_flags: SearchFlags = SearchFlags.NoFlags

        if self.case_sensitive_button.isChecked():
            search_flags |= SearchFlags.CaseSensitive

        if self.whole_word_button.isChecked():
            search_flags |= SearchFlags.WholeWord

        if self.regex_button.isChecked():
            search_flags |= SearchFlags.Regex

        return search_flags

    @pyqtSlot(bool)
    def find_next_clicked(self, checked: bool) -> None:
        search_criteria: SearchFlags = self.get_search_flags()
        search_expr: str = self.search_text.text()
        if not search_expr:
            return
        self.SearchQuery.emit(search_expr, search_criteria)

    @pyqtSlot(bool)
    def mark_all_button_clicked(self, checked: bool) -> None:
        search_criteria: SearchFlags = self.get_search_flags()
        search_criteria |= SearchFlags.AllOccurrences
        search_expr: str = self.search_text.text()
        if not search_expr:
            return
        self.SearchQuery.emit(search_expr, search_criteria)

    @pyqtSlot(bool)
    def replace_next_button_clicked(self, checked: bool) -> None:
        search_criteria: SearchFlags = self.get_search_flags()
        search_expr: str = self.search_text.text()
        if not search_expr:
            return
        replace_expr: str = self.replace_text.text()
        self.ReplaceQuery.emit(search_expr, replace_expr, search_criteria)

    @pyqtSlot(bool)
    def replace_all_button_clicked(self, checked: bool) -> None:
        search_criteria: SearchFlags = self.get_search_flags()
        search_criteria |= SearchFlags.AllOccurrences
        search_expr: str = self.search_text.text()
        if not search_expr:
            return
        replace_expr: str = self.replace_text.text()
        self.ReplaceQuery.emit(search_expr, replace_expr, search_criteria)


if __name__ == "__main__":
    from mindustry_editor import MindustryLogicEditor

    app = QApplication(sys.argv)
    main = QMainWindow()

    edit = MindustryLogicEditor(main)
    main.setCentralWidget(edit)

    main.show()
    sys.exit(app.exec_())
