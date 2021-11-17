#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from typing import List, Optional, Union

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class MindustryLogicCompleter(QCompleter):

    def __init__(self, word_list: List[str], *args, **kwargs):
        super(MindustryLogicCompleter, self).__init__(*args, **kwargs)
        self.model: QStringListModel = QStringListModel(word_list)
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

        self.model.setStringList(word_list)
        self.setModel(self.model)


if __name__ == '__main__':
    pass
