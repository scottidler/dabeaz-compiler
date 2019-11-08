#!/usr/bin/env python3

import re

from sly import Lexer

class WabbitLexer(Lexer):

    tokens = {

        # Reserved Keywords:
        CONST       , # 'const'
        VAR         , # 'var'
        PRINT       , # 'print'
        RETURN      , # 'return'
        BREAK       , # 'break'
        CONTINUE    , # 'continue'
        IF          , # 'if'
        ELSE        , # 'else'
        WHILE       , # 'while'
        FUNC        , # 'func'
        IMPORT      , # 'import'
        TRUE        , # 'true'
        FALSE       , # 'false'

        # Identifiers:
        ID          , # Text starting with a letter or '_', followed by any number
                      # number of letters, digits, or underscores.
                      # Examples:  'abc' 'ABC' 'abc123' '_abc' 'a_b_c'

        # Literals:
        INT         , #  123   (decimal)
        FLOAT       , # 1.234
        CHAR        , # 'a'     (a single character - byte)

        # Operators:
        PLUS         , # '+'
        MINUS        , # '-'
        STAR         , # '*'
        SLASH        , # '/'
        LT           , # '<'
        LE           , # '<='
        GT           , # '>'
        GE           , # '>='
        EQ           , # '=='
        NE           , # '!='
        LAND         , # '&&'
        LOR          , # '||'
        LNOT         , # '!'
        GROW         , # '^'

        # Miscellaneous Symbols
        ASSIGN       , # '='
        SEMI         , # ';'
        LPAREN       , # '('
        RPAREN       , # ')'
        LBRACE       , # '{'
        RBRACE       , # '}'
        COMMA        , # ','
        DEREF        , # '`'    (Backtick)
    }
    ignore = ' \t'

    # Reserved Keywords:
    CONST       = 'const'
    VAR         = 'var'
    PRINT       = 'print'
    RETURN      = 'return'
    BREAK       = 'break'
    CONTINUE    = 'continue'
    IF          = 'if'
    ELSE        = 'else'
    WHILE       = 'while'
    FUNC        = 'func'
    IMPORT      = 'import'
    TRUE        = 'true'
    FALSE       = 'false'

    # Identifiers:
    ID          = r'[a-zA-Z_][a-zA-Z0-9_]*'

    # Literals
    FLOAT       = r'\d+\.\d*|\.\d+'
    INT         = r'\d+'
    CHAR        = r'[A-Za-z0-9]'

    # Operators:
    PLUS        = r'\+'
    MINUS       = r'-'
    STAR        = r'\*'
    SLASH       = r'/'
    LT          = r'<'
    LE          = r'<='
    GT          = r'>'
    GE          = r'>='
    EQ          = r'=='
    NE          = r'!='
    LAND        = r'&&'
    LOR         = r'\|\|'
    LNOT        = r'!'
    GROW        = r'\^'

    # Miscellaneous Symbols
    ASSIGN      = r'='
    SEMI        = r';'
    LPAREN      = r'\('
    RPAREN      = r'\)'
    LBRACE      = r'{'
    RBRACE      = r'}'
    COMMA       = r','
    DEREF       = r'`'

    # Ignored pattern
    ignore_newline = r'\n+'

    # Extra action for newlines
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1
