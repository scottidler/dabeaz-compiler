#!/usr/bin/env python3

import re
import sys

from sly import Lexer
from sly.lex import Token

from leatherman.dbg import dbg

class WabbitToken(Token):
    __slots__ = ('kind')

    def __init__(self, kind, token):
        self.kind = kind
        self.type = token.type
        self.value = token.value
        self.lineno = token.lineno
        self.index = token.index

    def __repr__(self):
        fields = ', '.join([
            f'kind={self.kind}',
            f'type={self.type}',
            f'value={self.value}',
            f'lineno={self.lineno}',
            f'index={self.index}',
        ])
        return f'{self.__class__.__name__}({fields})'

class WabbitLexer(Lexer):

    def tokenize(self, text):
        tokens = list(super().tokenize(text))
        for token in tokens:
            print(token)
        return tokens

#    def tokenize(self, text):
#        tokens = []
#        for token in super().tokenize(text):
#            print(token)
#            token = WabbitToken('NORMAL', token)
#            if token.value in ('const', 'var', 'print', 'return', 'break', 'continue', 'if', 'else', 'while', 'func', 'import', 'true', 'false', 'int', 'float'):
#                token.kind = 'KEYWORD'
#            elif token.type in ('INT', 'FLOAT', 'BOOL'):
#                token.kind = 'LITERAL'
#            tokens += [token]
#        return tokens

    tokens = {

        # Keywords:
        # KEYWORD     ,
        # 'const'
        # 'var'
        # 'print'
        # 'return'
        # 'break'
        # 'continue'
        # 'if'
        # 'else'
        # 'while'
        # 'func'
        # 'import'
        # 'true'
        # 'false'
        # 'int'
        # 'float'
        KW_CONST    ,
        KW_VAR      ,
        KW_PRINT    ,
        KW_RETURN   ,
        KW_BREAK    ,
        KW_CONTINUE ,
        KW_IF       ,
        KW_ELSE     ,
        KW_WHILE    ,
        KW_FUNC     ,
        KW_IMPORT   ,
        KW_TRUE     ,
        KW_FALSE    ,
        KW_INT      ,
        KW_FLOAT    ,
        KW_BOOL     ,

        # OP          ,
        # SYNTAX      ,

        # Identifiers:
        ID          , # Text starting with a letter or '_', followed by any number
                      # number of letters, digits, or underscores.
                      # Examples:  'abc' 'ABC' 'abc123' '_abc' 'a_b_c'

        # Literals:
        LIT_FLOAT   , #  123   (decimal)
        LIT_INT     , # 1.234
        LIT_CHAR    , # 'a'     (a single character - byte)
        LIT_BOOL    , # true|false

        # Operators:
        OP_ASSIGN   , # '='
        OP_ADD      , # '+'
        OP_SUB      , # '-'
        OP_MUL      , # '*'
        OP_DIV      , # '/'
        OP_LT       , # '<'
        OP_LE       , # '<='
        OP_GT       , # '>'
        OP_GE       , # '>='
        OP_EQ       , # '=='
        OP_NE       , # '!='
        OP_LAND     , # '&&'
        OP_LOR      , # '||'
        OP_LNOT     , # '!'
        OP_GROW     , # '^'

        # Miscellaneous Symbols
        SYN_SEMI    , # ';'
        SYN_LPAREN  , # '('
        SYN_RPAREN  , # ')'
        SYN_LBRACE  , # '{'
        SYN_RBRACE  , # '}'
        SYN_COMMA   , # ','
    }
    ignore = ' \t'

    # Identifiers:
    ID              = r'[a-zA-Z_][a-zA-Z0-9_]*'

    # Reserved Keywords:
    ID['const']     = KW_CONST
    ID['var']       = KW_VAR
    ID['print']     = KW_PRINT
    ID['return']    = KW_RETURN
    ID['break']     = KW_BREAK
    ID['continue']  = KW_CONTINUE
    ID['if']        = KW_IF
    ID['else']      = KW_ELSE
    ID['while']     = KW_WHILE
    ID['func']      = KW_FUNC
    ID['import']    = KW_IMPORT
    ID['int']       = KW_INT
    ID['float']     = KW_FLOAT
    ID['bool']      = KW_BOOL

    # Literals
    ID['true']      = LIT_BOOL
    ID['false']     = LIT_BOOL
    LIT_FLOAT       = r'\d+\.\d*|\.\d+'
    LIT_INT         = r'\d+'
    LIT_CHAR        = r'[A-Za-z0-9]'

    # Operators:
    OP_ASSIGN       = r'='
    OP_ADD          = r'\+'
    OP_SUB          = r'-'
    OP_MUL          = r'\*'
    OP_DIV          = r'/'
    OP_LT           = r'<'
    OP_LE           = r'<='
    OP_GT           = r'>'
    OP_GE           = r'>='
    OP_EQ           = r'=='
    OP_NE           = r'!='
    OP_LAND         = r'&&'
    OP_LOR          = r'\|\|'
    OP_LNOT         = r'!'
    OP_GROW         = r'\^'

    # OP              = r'=|\+|-|\*|/|<|<=|>|>=|==|!=|&&|\|\||!|\^'

    # Miscellaneous Symbols
    SYN_SEMI        = r';'
    SYN_LPAREN      = r'\('
    SYN_RPAREN      = r'\)'
    SYN_LBRACE      = r'{'
    SYN_RBRACE      = r'}'
    SYN_COMMA       = r','

    # SYNTAX          = r';|\(|\)|{|}|,|`'

    # Ignored pattern
    ignore_newline = r'\n+'

    # Extra action for newlines
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1

def main(args):
    '''
const float pi = 3.14
var bool b = true;
var int x = 3;
if x < 4 {
    var y int = x + 2;
    print y;
}
else {
    var z float = x * 4 + 3 - 2;
    print z;
}
    '''

    print(main.__doc__)
    lexer = WabbitLexer()
    tokens = lexer.tokenize(main.__doc__)
    for token in tokens:
        print(token)

if __name__ == '__main__':
    main(sys.argv[1:])
