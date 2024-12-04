from functools import reduce
from pathlib import Path

import datasets

import tree_sitter_python as tspython
from tree_sitter import Language, Parser
import tree_sitter_go as tsgo

from funccraft.myField import *

detect_query = {
    'python': """
        (function_definition
            name: (identifier) @name
            body: (block) @body
        )
        
        (expression_statement
            (string) @block_comment
        )
        
        (comment) @line_comment
    """,

    'go': """
        (function_declaration 
            (identifier) @name
            (block) @body
        )
        
        (method_declaration
            (field_identifier) @name
            (block) @body
        )
        
        (comment) @line_comment
    """
}

detect_language = {
    'python': Language(tspython.language()),
    'go': Language(tsgo.language())
}


def prepare(dataset, language_str: str) -> datasets.Dataset:
    global detect_query
    language = detect_language[language_str]
    parser = Parser(language)

    code = dataset[original_function]
    ast = parser.parse(bytes(code, "utf-8"))
    query = language.query(detect_query[language_str])
    captures = query.captures(ast.root_node)

    comments = []
    name = func_body = ''
    for node, capture_name in captures:
        text = code[node.start_byte:node.end_byte]
        if capture_name == "name":
            name = text
        elif capture_name == "body":
            func_body = text
        elif "comment" in capture_name:
            comments.append(text)

    dataset[NEWFunc_name] = name
    dataset[NEWFunc_body] = func_body
    dataset[NEWFunc_body_without_comments] = func_body if not comments else reduce(lambda body, comment:
                                                                                   body.replace(comment, ""),
                                                                                   comments, func_body)

    return dataset


def load_dataset(path: Path) -> datasets.Dataset:
    return datasets.load_from_disk(str(path))


def save_dataset(dataset: datasets.Dataset, path: Path) -> None:
    dataset.save_to_disk(str(path))
