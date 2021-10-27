#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import math
import pathlib
import sys
from typing import List, Optional, Union

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class MindustryLogicCompleter(QCompleter):

    def __init__(self, word_list: List[str], *args, **kwargs):
        super(MindustryLogicCompleter, self).__init__(*args, **kwargs)
        self.model: QStringListModel = QStringListModel()
        self.model.setStringList(word_list)
        self.setModel(self.model)


if __name__ == '__main__':
    pass
