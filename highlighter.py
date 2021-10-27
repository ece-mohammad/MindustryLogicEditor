#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import pathlib
import sys
from typing import Dict, List

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from syntax_file_parser import SyntaxFileParser


class MindustryLogicSyntaxHighlighter(QSyntaxHighlighter):
    """
    Class for highlighting Mindustry Logic code

    Highlighting rules:
        - builtin functions: magenta, bold
        - function_operands: purple, normal
        - digits: blue, normal
        - strings: orange, normal
        - special_variables: purple, italic
        - comments: dark green, normal
    """

    class HighlightingRule(object):
        """Highlighting rules for MindustryLogicSyntaxHighlighter class"""

        __slots__ = ["pattern", "format"]

        def __init__(self, pattern: QRegularExpression, rule_format: QTextCharFormat):
            """Initialize highlighting rule instance"""
            self.pattern: QRegularExpression = pattern
            self.format: QTextCharFormat = rule_format

    def __init__(self, text_document: QTextDocument):
        super(MindustryLogicSyntaxHighlighter, self).__init__(text_document)
        self.text_document: QTextDocument = text_document
        self.syntax_file: pathlib.Path = pathlib.Path("config").joinpath("syntax.json")
        self.highlighting_rules: List[MindustryLogicSyntaxHighlighter.HighlightingRule] = list()

        # get syntax
        self.syntax: Dict[str, ...] = SyntaxFileParser.parse_syntax_file(self.syntax_file)
        syntax_regex: Dict[str, list[str]] = self.generate_regex_syntax(self.syntax)

        # ----------------------------------------------------------------------
        # ------------------------- highlighting rules -------------------------
        # ----------------------------------------------------------------------

        # ------------------------- builtin functions --------------------------
        function_format: QTextCharFormat = QTextCharFormat()  # magenta, bold
        function_format.setForeground(QBrush(QColor(200, 25, 130)))
        function_format.setFontWeight(QFont.DemiBold)
        function_patterns: List[str] = syntax_regex.get("functions", list())
        for pattern in function_patterns:
            self.highlighting_rules.append(
                MindustryLogicSyntaxHighlighter.HighlightingRule(
                    pattern=QRegularExpression(pattern),
                    rule_format=function_format
                )
            )

        # ------------------------ functions parameters ------------------------
        function_params_format: QTextCharFormat = QTextCharFormat()  # purple, normal
        function_params_format.setForeground(QBrush(QColor(190, 30, 170)))
        function_params_patterns = syntax_regex.get("params")
        for pattern in function_params_patterns:
            self.highlighting_rules.append(
                MindustryLogicSyntaxHighlighter.HighlightingRule(
                    pattern=QRegularExpression(pattern),
                    rule_format=function_params_format
                )
            )

        # ------------------------------- digits -------------------------------
        digit_format: QTextCharFormat = QTextCharFormat()  # blue, normal
        digit_format.setForeground(QBrush(QColor(30, 80, 210)))
        self.highlighting_rules.append(
            MindustryLogicSyntaxHighlighter.HighlightingRule(
                pattern=QRegularExpression("[0-9]"),
                rule_format=digit_format
            )
        )

        # --------------------------- string literals --------------------------
        string_literal_format: QTextCharFormat = QTextCharFormat()  # orange, normal
        string_literal_format.setForeground(QBrush(QColor(250, 130, 60)))
        self.highlighting_rules.append(
            MindustryLogicSyntaxHighlighter.HighlightingRule(
                pattern=QRegularExpression("\"\\w*\"|\'\\w*\'"),
                rule_format=string_literal_format
            )
        )

        # -------------------------- special variables -------------------------
        special_variable_format: QTextCharFormat = QTextCharFormat()  # blue, italic
        special_variable_format.setForeground(QBrush(QColor(25, 90, 230)))
        for pattern in syntax_regex.get("special_variables"):
            self.highlighting_rules.append(
                MindustryLogicSyntaxHighlighter.HighlightingRule(
                    pattern=QRegularExpression(pattern),
                    rule_format=special_variable_format
                )
            )

        self.highlighting_rules.append(
            MindustryLogicSyntaxHighlighter.HighlightingRule(
                pattern=QRegularExpression("\\B@\\w+\\b"),
                rule_format=special_variable_format
            )
        )

        # ------------------------------ comments ------------------------------
        comment_format = QTextCharFormat()  # dark green, normal
        comment_format.setForeground(QBrush(QColor(90, 170, 35)))
        self.highlighting_rules.append(
            MindustryLogicSyntaxHighlighter.HighlightingRule(
                pattern=QRegularExpression("#.*$"),
                rule_format=comment_format
            )
        )

    @staticmethod
    def generate_regex_syntax(syntax: dict) -> dict:
        """


        :param syntax:
        :type syntax:
        :return:
        :rtype:
        """
        regex_patterns = {k: [] for k in syntax.keys()}

        # special_variables
        for pattern in syntax.get("special_variables", list()):
            regex_patterns["special_variables"].append(f"\\B{pattern}\\b")

        # functions
        for pattern in syntax.get("functions", list()):
            regex_patterns["functions"].append(f"^\\s*?{pattern}\\b")

        # params
        for pattern in syntax.get("params", list()):
            regex_patterns["params"].append(f"\\b{pattern}\\b")

        return regex_patterns

    def highlightBlock(self, text: str) -> None:
        """Highlight a text block in text document"""
        for rule in self.highlighting_rules:
            match_iterator = rule.pattern.globalMatch(text)
            while match_iterator.hasNext():
                match: QRegularExpressionMatch = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), rule.format)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = QPlainTextEdit()
    t = MindustryLogicSyntaxHighlighter(editor.document())
    editor.show()
    sys.exit(app.exec_())
