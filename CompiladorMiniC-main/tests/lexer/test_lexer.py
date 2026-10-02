"""Pruebas del analizador léxico de Mini C basadas en la especificación de la skill analizador-lexico-mini-c."""

import pytest

from minic.diagnostics.diagnostic_code import LEX001
from minic.lexer.lexer import Lexer
from minic.lexer.token_type import TokenType
from minic.output.diagnostic_printer import format_diagnostic
from minic.output.token_printer import format_token


def test_section_7_case_1_valid() -> None:
    source = "int2 = 12abc;\nwhilex == -5"
    tokens, diagnostics = Lexer(source).scan()

    assert diagnostics == []

    expected_output = [
        "IDENTIFIER 'int2' 1 1",
        "ASSIGN '=' 1 6",
        "INTEGER_LITERAL '12' 1 8",
        "IDENTIFIER 'abc' 1 10",
        "SEMICOLON ';' 1 13",
        "IDENTIFIER 'whilex' 2 1",
        "EQUAL_EQUAL '==' 2 8",
        "MINUS '-' 2 11",
        "INTEGER_LITERAL '5' 2 12",
        "EOF '' 2 13",
    ]

    actual_output = [format_token(t) for t in tokens]
    assert actual_output == expected_output

    # Verificar literales
    int_12 = tokens[2]
    assert int_12.type == TokenType.INTEGER_LITERAL
    assert int_12.literal == 12

    int_5 = tokens[8]
    assert int_5.type == TokenType.INTEGER_LITERAL
    assert int_5.literal == 5


def test_section_7_case_2_with_errors() -> None:
    source = "int x = @;\nx ! = 0; // fin"
    tokens, diagnostics = Lexer(source).scan()

    expected_tokens = [
        "KW_INT 'int' 1 1",
        "IDENTIFIER 'x' 1 5",
        "ASSIGN '=' 1 7",
        "SEMICOLON ';' 1 10",
        "IDENTIFIER 'x' 2 1",
        "ASSIGN '=' 2 5",
        "INTEGER_LITERAL '0' 2 7",
        "SEMICOLON ';' 2 8",
        "IDENTIFIER 'fin' 2 13",
        "EOF '' 2 16",
    ]
    actual_tokens = [format_token(t) for t in tokens]
    assert actual_tokens == expected_tokens

    expected_diagnostics = [
        "LEX001 error 1:9 Carácter no reconocido: '@'",
        "LEX001 error 2:3 Carácter no reconocido: '!'",
        "LEX001 error 2:10 Carácter no reconocido: '/'",
        "LEX001 error 2:11 Carácter no reconocido: '/'",
    ]
    actual_diagnostics = [format_diagnostic(d) for d in diagnostics]
    assert actual_diagnostics == expected_diagnostics


def test_keywords_and_identifiers() -> None:
    source = "while int whilex int2 _var x_1"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []

    types = [t.type for t in tokens]
    lexemes = [t.lexeme for t in tokens]

    assert types == [
        TokenType.KW_WHILE,
        TokenType.KW_INT,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.EOF,
    ]
    assert lexemes == ["while", "int", "whilex", "int2", "_var", "x_1", ""]


def test_operators_maximal_munch() -> None:
    source = "== = != !"
    tokens, diagnostics = Lexer(source).scan()

    # == es EQUAL_EQUAL, = es ASSIGN, != es NOT_EQUAL, ! es no reconocido
    assert [t.type for t in tokens] == [
        TokenType.EQUAL_EQUAL,
        TokenType.ASSIGN,
        TokenType.NOT_EQUAL,
        TokenType.EOF,
    ]
    assert len(diagnostics) == 1
    assert diagnostics[0].code == LEX001
    assert diagnostics[0].line == 1
    assert diagnostics[0].column == 9
    assert diagnostics[0].message == "Carácter no reconocido: '!'"


def test_integer_literal_parsing() -> None:
    source = "007 0 12345"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []
    assert tokens[0].literal == 7
    assert tokens[0].lexeme == "007"
    assert tokens[1].literal == 0
    assert tokens[1].lexeme == "0"
    assert tokens[2].literal == 12345
    assert tokens[2].lexeme == "12345"


def test_tab_and_carriage_return_positions() -> None:
    # \t cuenta 1 columna, \r cuenta 1 columna sin salto de línea
    source = "\tx\r\ny"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []

    # \t en (1, 1), x en (1, 2), \r en (1, 3), \n salta a (2, 1), y en (2, 1)
    tok_x = tokens[0]
    assert tok_x.lexeme == "x"
    assert tok_x.line == 1
    assert tok_x.column == 2

    tok_y = tokens[1]
    assert tok_y.lexeme == "y"
    assert tok_y.line == 2
    assert tok_y.column == 1


def test_empty_source() -> None:
    tokens, diagnostics = Lexer("").scan()
    assert diagnostics == []
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.EOF
    assert tokens[0].lexeme == ""
    assert tokens[0].line == 1
    assert tokens[0].column == 1
