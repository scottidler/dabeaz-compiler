#!/usr/bin/env python3

import re
import sys

from sly import Lexer
from sly.lex import Token

class WabbitLexer(Lexer):

    tokens = {

        # Keywords:
        KEYWORD     ,
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

        OP          ,
        SYNTAX      ,

        # Identifiers:
        ID          , # Text starting with a letter or '_', followed by any number
                      # number of letters, digits, or underscores.
                      # Examples:  'abc' 'ABC' 'abc123' '_abc' 'a_b_c'

        # Literals:
        FLOAT       , #  123   (decimal)
        INT         , # 1.234
        CHAR        , # 'a'     (a single character - byte)
        BOOL        , # true|false

        # Operators:
        PLUS        , # '+'
        MINUS       , # '-'
        STAR        , # '*'
        SLASH       , # '/'
        LT          , # '<'
        LE          , # '<='
        GT          , # '>'
        GE          , # '>='
        EQ          , # '=='
        NE          , # '!='
        LAND        , # '&&'
        LOR         , # '||'
        LNOT        , # '!'
        GROW        , # '^'

        # Miscellaneous Symbols
        EQUALS      , # '='
        SEMI        , # ';'
        LPAREN      , # '('
        RPAREN      , # ')'
        LBRACE      , # '{'
        RBRACE      , # '}'
        COMMA       , # ','
        DEREF       , # '`'    (Backtick)
    }
    ignore = ' \t'

    # Identifiers:
    ID              = r'[a-zA-Z_][a-zA-Z0-9_]*'

    # Reserved Keywords:
    ID['const']     = KEYWORD
    ID['var']       = KEYWORD
    ID['print']     = KEYWORD
    ID['return']    = KEYWORD
    ID['break']     = KEYWORD
    ID['continue']  = KEYWORD
    ID['if']        = KEYWORD
    ID['else']      = KEYWORD
    ID['while']     = KEYWORD
    ID['func']      = KEYWORD
    ID['import']    = KEYWORD
    ID['true']      = KEYWORD
    ID['false']     = KEYWORD
    ID['int']       = KEYWORD
    ID['float']     = KEYWORD

    # Literals
    FLOAT           = r'\d+\.\d*|\.\d+'
    INT             = r'\d+'
    CHAR            = r'[A-Za-z0-9]'

    # Operators:
    #PLUS            = r'\+'
    #MINUS           = r'-'
    #STAR            = r'\*'
    #SLASH           = r'/'
    #LT              = r'<'
    #LE              = r'<='
    #GT              = r'>'
    #GE              = r'>='
    #EQ              = r'=='
    #NE              = r'!='
    #LAND            = r'&&'
    #LOR             = r'\|\|'
    #LNOT            = r'!'
    #GROW            = r'\^'

    OP              = r'=|\+|-|\*|/|<|<=|>|>=|==|!=|&&|\|\||!|\^'

    # Miscellaneous Symbols
    #EQUALS          = r'='
    #SEMI            = r';'
    #LPAREN          = r'\('
    #RPAREN          = r'\)'
    #LBRACE          = r'{'
    #RBRACE          = r'}'
    #COMMA           = r','
    #DEREF           = r'`'

    SYNTAX          = r';|\(|\)|{|}|,|`'

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
