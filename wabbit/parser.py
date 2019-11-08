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

from leatherman.dbg import dbg

# symbol (token type) registry

symbol_table = {}

class symbol_base(object):

    id = None
    value = None
    first = second = third = None

    def nud(self):
        raise SyntaxError("Syntax error (%r)." % self.id)

    def led(self, left):
        raise SyntaxError("Unknown operator (%r)." % self.id)

    def __repr__(self):
        if self.id == "(name)" or self.id == "(literal)":
            return "(%s %s)" % (self.id[1:-1], self.value)
        out = [self.id, self.first, self.second, self.third]
        out = list(map(str, [_f for _f in out if _f]))
        return "(" + " ".join(out) + ")"

def symbol(id, bp=0):
    try:
        s = symbol_table[id]
    except KeyError:
        class s(symbol_base):
            pass
        s.__name__ = "symbol-" + id # for debugging
        s.id = id
        s.value = None
        s.lbp = bp
        symbol_table[id] = s
    else:
        s.lbp = max(bp, s.lbp)
    return s

# helpers

def infix(id, bp):
    def led(self, left):
        self.first = left
        self.second = expression(bp)
        return self
    symbol(id, bp).led = led

def infix_r(id, bp):
    def led(self, left):
        self.first = left
        self.second = expression(bp-1)
        return self
    symbol(id, bp).led = led

def prefix(id, bp):
    def nud(self):
        self.first = expression(bp)
        return self
    symbol(id).nud = nud

def advance(id=None):
    global token
    if id and token.id != id:
        raise SyntaxError("Expected %r" % id)
    token = next_()

def method(s):
    # decorator
    assert issubclass(s, symbol_base)
    def bind(fn):
        setattr(s, fn.__name__, fn)
    return bind

# python expression syntax

symbol("lambda", 20)
symbol("if", 20); symbol("else") # ternary form

infix_r("or", 30); infix_r("and", 40); prefix("not", 50)

infix("in", 60); infix("not", 60) # not in
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

symbol("(name)").nud = lambda self: self
symbol("(literal)").nud = lambda self: self

symbol("(end)")

symbol(")")

@method(symbol("("))
def nud(self):
    # parenthesized form; replaced by tuple former below
    expr = expression()
    advance(")")
    return expr

symbol("else")

@method(symbol("if"))
def led(self, left):
    self.first = left
    self.second = expression()
    advance("else")
    self.third = expression()
    return self

@method(symbol("."))
def led(self, left):
    if token.id != "(name)":
        SyntaxError("Expected an attribute name.")
    self.first = left
    self.second = token
    advance()
    return self

symbol("]")

@method(symbol("["))
def led(self, left):
    self.first = left
    self.second = expression()
    advance("]")
    return self

symbol(")"); symbol(",")

@method(symbol("("))
def led(self, left):
    self.first = left
    self.second = []
    if token.id != ")":
        while 1:
            self.second.append(expression())
            if token.id != ",":
                break
            advance(",")
    advance(")")
    return self

symbol(":"); symbol("=")

@method(symbol("lambda"))
def nud(self):
    self.first = []
    if token.id != ":":
        argument_list(self.first)
    advance(":")
    self.second = expression()
    return self

def argument_list(list):
    while 1:
        if token.id != "(name)":
            SyntaxError("Expected an argument name.")
        list.append(token)
        advance()
        if token.id == "=":
            advance()
            list.append(expression())
        else:
            list.append(None)
        if token.id != ",":
            break
        advance(",")

# constants

def constant(id):
    @method(symbol(id))
    def nud(self):
        self.id = "(literal)"
        self.value = id
        return self

constant("None")
constant("True")
constant("False")

# multitoken operators

@method(symbol("not"))
def led(self, left):
    if token.id != "in":
        raise SyntaxError("Invalid syntax")
    advance()
    self.id = "not in"
    self.first = left
    self.second = expression(60)
    return self

@method(symbol("is"))
def led(self, left):
    if token.id == "not":
        advance()
        self.id = "is not"
    self.first = left
    self.second = expression(60)
    return self

# displays

@method(symbol("("))
def nud(self):
    self.first = []
    comma = False
    if token.id != ")":
        while 1:
            if token.id == ")":
                break
            self.first.append(expression())
            if token.id != ",":
                break
            comma = True
            advance(",")
    advance(")")
    if not self.first or comma:
        return self # tuple
    else:
        return self.first[0]

symbol("]")

@method(symbol("["))
def nud(self):
    self.first = []
    if token.id != "]":
        while 1:
            if token.id == "]":
                break
            self.first.append(expression())
            if token.id != ",":
                break
            advance(",")
    advance("]")
    return self

symbol("}")

@method(symbol("{"))
def nud(self):
    self.first = []
    if token.id != "}":
        while 1:
            if token.id == "}":
                break
            self.first.append(expression())
            advance(":")
            self.first.append(expression())
            if token.id != ",":
                break
            advance(",")
    advance("}")
    return self

# python tokenizer

def tokenize_python(program):
    import tokenize
    from io import StringIO
    type_map = {
        tokenize.NUMBER: "(literal)",
        tokenize.STRING: "(literal)",
        tokenize.OP: "(operator)",
        tokenize.NAME: "(name)",
        tokenize.NEWLINE: "(newline)"
        }
    for t in tokenize.generate_tokens(StringIO(program).__next__):
        try:
            yield type_map[t[0]], t[1]
        except KeyError:
            if t[0] == tokenize.NL:
                continue
            if t[0] == tokenize.ENDMARKER:
                break
            else:
                raise SyntaxError("Syntax error")
    yield "(end)", "(end)"

def tokenize(program):
    if isinstance(program, list):
        source = program
    else:
        source = tokenize_python(program)
    for id, value in source:
        if id == "(literal)":
            symbol = symbol_table[id]
            s = symbol()
            s.value = value
        else:
            # name or operator
            symbol = symbol_table.get(value)
            if symbol:
                s = symbol()
            elif id == "(name)":
                symbol = symbol_table[id]
                s = symbol()
                s.value = value
            elif id == "(newline)":
                pass
            else:
                raise SyntaxError("Unknown operator (%r)" % id)
        yield s

# parser engine

def expression(rbp=0):
    global token
    t = token
    token = next_()
    left = t.nud()
    while rbp < token.lbp:
        t = token
        token = next_()
        left = t.led(left)
    return left

def parse(program):
    global token, next_
    next_ = tokenize(program).__next__
    token = next_()
    return expression()

def test(program):
    print(">>>", program)
    print(parse(program))

# samples
test("1")
test("+1")
test("-1")
test("1+2")
test("1+2+3")
test("1+2*3")
test("(1+2)*3")
test("()")
test("(1)")
test("(1,)")
test("(1, 2)")
test("[1, 2, 3]")
test("{}")
test("{1: 'one', 2: 'two'}")
test("1.0*2+3")
test("'hello'+'world'")
test("2**3**4")
test("1 and 2")
test("foo.bar")
test("1 + hello")
test("1 if 2 else 3")
test("'hello'[0]")
test("hello()")
test("hello(1,2,3)")
test("lambda: 1")
test("lambda a, b, c: a+b+c")
test("True")
test("True or False")
test("1 in 2")
test("1 not in 2")
test("1 is 2")
test("1 is not 2")
test("1 is (not 2)")

print()
print(list(tokenize("1 not in 2")))
