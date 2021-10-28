#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from typing import List, Optional, Union

from PySide2.QtCore import *
from PySide2.QtWidgets import *


class MindustryLogicCompleter(QCompleter):

    def __init__(self, word_list: List[str], *args, **kwargs):
        super(MindustryLogicCompleter, self).__init__(*args, **kwargs)
        self.model: QStringListModel = QStringListModel()
        self.model.setStringList(word_list)
        self.setModel(self.model)

    def update_model(self, word_list: List[str]) -> None:
        """
        Update completer model

        :param word_list: new list of words
        :type word_list: List[str]
        :return: None
        :rtype: None
        """
        if len(word_list) == 0:
            return

        model = QStringListModel()
        model.setStringList(word_list)
        self.setModel(model)
        self.model = model


if __name__ == '__main__':
    pass
