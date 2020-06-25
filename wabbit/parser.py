#!/usr/bin/env python3
# parse.py
#
# Wabbit parser.  The parser needs to construct the data model or an
# abstract syntax tree from text input.  The Grammar here is specified
# as a PEG (Parsing Expression Grammar)
#
# PEG Syntax:
#
#    'quoted'   : Literal text
#    ( ... )    : Grouping
#      e?       : Optional (0 or 1 matches of e)
#      e*       : Repetition (0 or more matches of e)
#      e+       : Repetition (1 or more matches)
#     e1 e2     : Match e1 then match e2 (sequence)
#    e1 / e2    : Try to match e1. On failure, try to match e2.
#
# Names in all-caps are assumed to be tokens from the tokenize.py file.
# EOF is "End of File".
#
# program <- statement* EOF
#
# statement <- assignment
#           /  vardecl
#           /  funcdel
#           /  if_stmt
#           /  while_stmt
#           /  break_stmt
#           /  continue_stmt
#           /  return_stmt
#           /  print_stmt
#
# assignment <- location '=' expression ';'
#
# vardecl <- ('var'/'const') ID type? ('=' expression)? ';'
#
# funcdecl <- 'import'? 'func' ID '(' parameters ')' type '{' statement* '}'
#
# if_stmt <- 'if' expression '{' statement* '}'
#         /  'if' expression '{' statement* '}' else '{' statement* '}'
#
# while_stmt <- 'while' expression '{' statement* '}'
#
# break_stmt <- 'break' ';'
#
# continue_stmt <- 'continue' ';'
#
# return_stmt <- 'return' expression ';'
#
# print_stmt <- 'print' expression ';'
#
# parameters <- ID type (',' ID type)*
#            /  empty
#
# type <- 'int' / 'float' / 'char' / 'bool'
#
# location <- ID
#          /  '`' expression
#
# expression <- orterm ('||' orterm)*
#
# orterm <- andterm ('&&' andterm)*
#
# andterm <- relterm (('<' / '>' / '<=' / '>=' / '==' / '!=') reltime)*
#
# relterm <- addterm (('+' / '-') addterm)*
#
# addterm <- factor (('*' / '/') factor)*
#
# factor <- literal
#        / ('+' / '-' / '^') expression
#        / '(' expression ')'
#        / type '(' expression ')'
#        / ID '(' arguments ')'
#        / location
#
# arguments <- expression (',' expression)*
#          / empty
#
# literal <- INTEGER / FLOAT / CHAR / bool
#
# bool <- 'true' / 'false'

# see http://effbot.org/zone/simple-top-down-parsing.htm

import re
import sys

from multimethod import multimeta

from wabbit.symbol import Symbol
from wabbit.model import *
from leatherman.dbg import dbg

#class WabbitParser(metaclass=multimeta):
class WabbitParser:

    def symbolize(self, tokens):
        for token in tokens:
            symbol_class = Symbol.Table[token]
            s = symbol_class(self, token)
            yield s

    def parse(self, tokens=None):
        self.symbols = list(self.symbolize(list(tokens) if tokens else self.tokens))
        for symbol in self.symbols:
            print(symbol)
        return self.program()

#    def __repr__(self):
#        fields = ', '.join([
#            f'tokens={self.tokens}',
#            f'index={self.index}',
#        ])
#        return f'{self.__class__.__name__}({fields})'

    def __init__(self, tokens=None):
        self.tokens = list(tokens) if tokens else []
        self.symbols = []
        self.index = 0

        symbol = self.symbol
        infix = self.infix
        infix_r = self.infix_r
        prefix = self.prefix
        method = self.method
        constant = self.constant

        symbol('const')
        symbol('var')
        symbol('int')
        symbol('float')

        # python expression syntax
        symbol('print', 10)

        #symbol("lambda", 20)
        symbol("if", 20); symbol("else") # ternary form
        symbol('while', 20)

        #infix_r("or", 30); infix_r("and", 40); prefix("not", 50)

        #infix("in", 60); infix("not", 60) # not in
        #infix("is", 60);
        infix("<", 60); infix("<=", 60)
        infix(">", 60); infix(">=", 60)
        infix("<>", 60); infix("!=", 60); infix("==", 60)

        infix("|", 70); infix("^", 80); infix("&", 90)

        infix("<<", 100); infix(">>", 100)

        infix("+", 110); infix("-", 110)

        infix("*", 120); infix("/", 120); infix("//", 120)
        infix("%", 120)

        prefix("-", 130); prefix("+", 130); prefix("~", 130)

        infix_r("**", 140)

        symbol(".", 150); symbol("[", 150); symbol("(", 150)

        symbol(';')

        # additional behaviour

        #symbol("(name)").nud = lambda self: self
        #symbol("(literal)").nud = lambda self: self
        symbol('ID').nud = lambda self: Name(self.value)
        symbol('LIT_INT').nud = lambda self: Integer(self.value)
        symbol('LIT_BOOL').nud = lambda self: Boolean(self.value)
        symbol('LIT_FLOAT').nud = lambda self: Float(self.value)

        @method(symbol('LIT'))
        def nud(self):
            if self.token.type == 'LIT_INT':
                return Integer(self.token.value)
            elif self.token.type == 'LIT_BOOL':
                return Boolean(self.token.value)
            elif self.token.type == 'LIT_FLOAT':
                return Float(self.token.value)
            raise SyntaxError('unknown literal')

        #symbol("(end)")
        symbol('EOF')

        symbol(")")

        @method(symbol("("))
        def nud(self):
            # parenthesized form; replaced by tuple former below
            expr = self.parser.expression()
            #advance(")")
            self.parser.consume(')')
            return expr

        symbol("else")

        @method(symbol("if"))
        def led(self, left):
            self.fst = left
            self.snd = self.parser.expression()
            #advance("else")
            self.parser.consume('else')
            self.trd = self.parser.expression()
            return self

        @method(symbol("."))
        def led(self, left):
            #if token.id != "(name)":
            curr = self.parser.look_ahead()
            if curr.type != 'ID':
                SyntaxError("Expected an attribute ID.")
            self.fst = left
            self.snd = curr
            #advance()
            self.parser.consume()
            return self

        symbol("]")

        @method(symbol("["))
        def led(self, left):
            self.fst = left
            self.snd = self.parser.expression()
            self.parser.consume(']')
            return self

        symbol(")"); symbol(",")

        @method(symbol("("))
        def led(self, left):
            self.fst = left
            self.snd = []
            #if token.id != ")":
            if not self.parser.is_look_ahead(')'):
                while 1:
                    self.snd.append(self.parser.expression())
                    #if token.id != ",":
                    if not self.parser.is_look_ahead(','):
                        break
                    #advance(",")
                    self.parser.consume(',')
            #advance(")")
            self.parser.consume(')')
            return self

        symbol(":"); symbol("=")

        # constants

        constant("None")
        constant("True")
        constant("False")

        # multitoken operators

        @method(symbol("not"))
        def led(self, left):
            #if token.id != "in":
            if not self.parser.is_look_ahead('in'):
                raise SyntaxError("Invalid syntax")
            #advance()
            self.parser.consume()
            self.type = "not in"
            self.fst = left
            self.snd = self.parser.expression(60)
            return self

        @method(symbol("is"))
        def led(self, left):
            if self.parser.look_ahead() == 'not':
                #advance()
                self.parser.consume()
                self.type = "is not"
            self.fst = left
            self.snd = self.parser.expression(60)
            return self

        # displays

        @method(symbol("("))
        def nud(self):
            self.fst = []
            comma = False
            #if token.id != ")":
            if not self.parser.is_look_ahead(')'):
                while 1:
                    #if token.id == ")":
                    if self.parser.look_ahead(')'):
                        break
                    self.fst.append(self.parser.expression())
                    #if token.id != ",":
                    if not self.parser.look_ahead(','):
                        break
                    comma = True
                    #advance(",")
                    self.parser.consume(',')
            #advance(")")
            self.parser.consume(')')
            if not self.fst or comma:
                return self # tuple
            else:
                return self.fst[0]

        symbol("]")

        @method(symbol("["))
        def nud(self):
            self.fst = []
            #if token.id != "]":
            if not self.parser.is_look_ahead(']'):
                while 1:
                    #if token.id == "]":
                    if self.parser.is_look_ahead(']'):
                        break
                    self.fst.append(self.parser.expression())
                    #if token.id != ",":
                    if not self.parser.is_look_ahead(','):
                        break
                    #advance(",")
                    self.parser.consume(',')
            #advance("]")
            self.parser.consume(']')
            return self

        symbol("}")

        @method(symbol("{"))
        def nud(self):
            self.fst = []
            #if token.id != "}":
            if not self.parser.is_look_ahead('}'):
                while 1:
                    #if token.id == "}":
                    if self.parser.is_look_ahead('}'):
                        break
                    self.fst.append(self.parser.expression())
                    #advance(":")
                    self.parser.conume(':')
                    self.fst.append(self.parser.expression())
                    #if token.id != ",":
                    if not self.parser.is_look_ahead(','):
                        break
                    #advance(",")
                    self.parser.consume(',')
            #advance("}")
            self.parser.consume('}')
            return self

#    def look_ahead(self, *types, distance=1):
#        assert distance > 0, f'distance={distance} must be > 0'
#        index = self.index
#        token =  None
#        while distance:
#            token = self.tokens[index]
#            distance -= 1
#            index += 1
#        distance = index - self.index
#        if types:
#            if Symbol.Table.make_key(token) in types:
#                return True
#            return False
#        return token

    def look_ahead(self, *types, distance=1):
        assert distance > 0, f'distance={distance} must be > 0'
        index = self.index
        symbol = None
        while distance:
            symbol = self.symbols[index]
            distance -= 1
            index += 1
        distance = index - self.index
        if types:
            if symbol.type in types:
                return True
            return False
        return symbol

    def consume(self, *types, distance=1):
        result = self.look_ahead(*types, distance)
        dbg(index=self.index)
        assert result, f'cannot consume! types={types}, distance={distance}'
        self.index += distance
        return self.symbols[self.index-1]

    def symbol(self, key, bp=0):
        try:
            symbol_class = Symbol.Table[key]
        except KeyError:
            parser = self
            def __init__(self):
                Symbol.__init__(
                    self,
                    parser,
                    token,
                )
            symbol_class = type(f'Symbol {key}', (Symbol,), {
                #'__init__': lambda self, parser, token: Symbol.__init__(self, parser, token)
            })
            Symbol.Table[key] = symbol_class
            symbol_class.lbp = bp
        else:
            symbol_class.lbp = max(bp, symbol_class.lbp)
        return symbol_class

    def infix(self, type, bp):
        def led(self, left):
            return BinOp(type, left, self.parse.expression(bp))
        self.symbol(type, bp).led = led

    def infix_r(self, type, bp):
        def led(self, left):
            return BinOp(type, left, self.parser.expression(bp-1))
        self.symbol(type, bp).led = led

    def prefix(self, type, bp):
        def nud(self):
            return UnOp(type, self.parser.expression(bp))
        self.symbol(type).nud = nud

    def method(self, s):
        assert issubclass(s, Symbol)
        def bind(func):
            setattr(s, func.__name__, func)
        return bind

    def constant(self, type):
        @self.method(self.symbol(type))
        def nud(self):
            self.type = 'LITERAL'
            self.value = type
            return self

    def expression(self, rbp=0):
        curr_symbol = self.consume()
        if curr_symbol.nud:
            self.index -= 1
            return None
        left = curr_symbol.nud(curr_symbol.type)
        next_symbol = self.look_ahead()
        while rbp < next_symbol.lbp:
            curr_symbol = self.consume()
            if curr_symbol.led:
                self.index -= 1
                return None
            left = curr_symbol.led(left, curr_symbol.type)
            next_symbol = self.look_ahead()
        return left

    def statement(self):
        next_symbol = self.look_ahead()
        if next_symbol.std != None:
            self.consume()
            return next_symbol.std()
        return self.expression()

    def statements(self):
        statements = []
        statement = self.statement()
        while statement:
            statements += [statement]
            statement = self.statement() if self.consume('EOF') else None
        return statements

    def program(self):
        stms = self.statements()
        return Prog(stmts)

def main(args):
    dbg(args)

if __name__ == '__main__':
    main(sys.argv[1:])
