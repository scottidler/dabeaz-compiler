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

import sys
import re

from wabbit.tdop import TDOPParser
from leatherman.dbg import dbg

class WabbitParser(TDOPParser):

    def symbolize(self, tokens):
        for token in tokens:
            if token.type in ('int', 'float', 'char'):
                symbol = self.symbols[token.type]
                s = symbol()
                s.value = token.value
            else:
                symbol = self.symbols.get(token.value)
                if symbol:
                    s = symbol()
                elif token.type == 'ID':
                    symbol = self.symbols[token.type]
                    s = symbol()
                    s.value = token.value
                elif token.type == 'NL':
                    continue
                else:
                    raise SyntaxError('')
            yield s

    def __init__(self, tokens=None):
        super().__init__(tokens=tokens, symbols=None, index=0)


        symbol = self.symbol
        infix = self.infix
        infix_r = self.infix_r
        prefix = self.prefix
        method = self.method
        constant = self.constant

        # python expression syntax

        #symbol("lambda", 20)
        symbol("if", 20); symbol("else") # ternary form

        #infix_r("or", 30); infix_r("and", 40); prefix("not", 50)

        #infix("in", 60); infix("not", 60) # not in
        infix("is", 60);
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

        # additional behaviour

        #symbol("(name)").nud = lambda self: self
        #symbol("(literal)").nud = lambda self: self
        symbol('ID').nud = lambda self: self
        symbol('INT').nud = lambda self: self
        symbol('FLOAT').nud = lambda self: self

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
