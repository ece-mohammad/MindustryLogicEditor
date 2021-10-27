#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pathlib
import json
from typing import Dict, List


class SyntaxFileParser(object):

    def __init__(self, file_path: str):
        self.file_path: pathlib.Path = pathlib.Path(file_path)
        self.syntax = self.parse_syntax_file(self.file_path)

    @staticmethod
    def parse_syntax_file(file_path: pathlib.Path) -> Dict[str, List[str]]:
        """
        Parse syntax file and get builtin_functions, params, special_variables

        :return: dictionary containing syntax
        :rtype: Dict[str, List[str]]
        """
        syntax = {
            "builtin_functions": [],
            "params":            [],
            "special_variables": [],
        }

        with open(file_path, "r") as syntax_file:
            raw_syntax = json.load(syntax_file)

        syntax["special_variables"] = raw_syntax.get("special_variables", [])

        builtin_functions = raw_syntax.get("builtin_functions", [])
        for function in builtin_functions:
            for func_name, func_params in function.items():
                syntax["builtin_functions"].append(func_name)
                for param in func_params:
                    for param_name in param.values():
                        syntax["params"].extend(param_name)

        return syntax

    def get_keywords(self) -> List[str]:
        """
        Get a list of all syntax keywords

        :return: list of all syntax kywords
        :rtype: List[str]
        """
        return [kw for cat in self.syntax.values() for kw in cat]


if __name__ == '__main__':
    t = SyntaxFileParser("config/syntax.json")
    print(t.syntax)
    print(t.get_keywords())
