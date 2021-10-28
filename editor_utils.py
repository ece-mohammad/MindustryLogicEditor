#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from PySide2.QtGui import *


def test_modifiers(value: Qt.KeyboardModifiers, flag: Qt.KeyboardModifier):
    """
    Test a modifier (or a group of modifiers) flag is set

    :param value: Modifiers value as returned by QKeyEvent.modifiers()
    :type value: QKeyboardModifiers
    :param flag: keyboard modifier (QControlModifier, QShiftModifier, etc)
    :type flag: QKeyModifier
    :return: True if modifier is in value, False otherwise
    :rtype: bool
    """
    return (value & flag) == flag


if __name__ == '__main__':
    pass
