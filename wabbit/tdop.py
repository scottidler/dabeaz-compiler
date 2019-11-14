#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import *
from dataclasses import dataclass, field

from wabbit.lexer import Token
from leatherman.dbg import dbg

@dataclass
class Symbol:
    parser: Any
    type: str
    lbp: int = 0
    value: str = None
    fst: Any = None
    snd: Any = None
    trd: Any = None
    nud: Any = None
    led: Any = None
    std: Any = None

class TDOPParser:

    def __init__(self, tokens=None, symbols=None, index=0):
        self.tokens = list(tokens) if tokens != None else []
        self.symbols = symbols if symbols else {}
        self.index = index

    def __repr__(self):
        fields = ', '.join([
            f'tokens={self.tokens}',
            f'symbols={self.symbols}',
            f'index={self.index}',
        ])
        return f'self.__class__.__name__({fields})'

    def look_ahead(self, distance=1):
        assert distance > 0, f'distance={distance} must be > 0'
        index = self.index
        while distance:
            if index >= len(self.tokens):
                eof = Token()
                eof.type = 'EOF'
                eof.value ='eof'
                eof.lineno = -1
                eof.index = -1
                return eof
            token = self.tokens[index]
            distance -= 1
            index += 1
        distance = index - self.index
        return token

    def is_look_ahead(self, expected, distance=1):
        return self.look_ahead(distance) == expected

    def consume(self, *types, distance=1):
        token = self.look_ahead(distance)
        for type in types:
            if type == token.type:
                self.index += distance
                return token
        self.index += distance
        return None

    def symbol(self, key, bp=0):
        try:
            s = self.symbols[key]
        except KeyError:
            parser = self
            def init(self):
                Symbol.__init__(
                    self,
                    parser,
                    key,
                    bp,
                )
            s = type(f'Symbol{key}', (Symbol,), {
                '__init__': init,
            })
            self.symbols[key] = s
        else:
            s.lbp = max(bp, s.lbp)
        return s

    def infix(self, type, bp):
        def led(self, left):
            self.fst = left
            self.snd = self.parser.expression(bp)
            return self
        self.symbol(type, bp).led = led

    def infix_r(self, type, bp):
        def led(self, left):
            self.fst = left
            self.snd = self.parser.expression(bp-1)
            return self
        self.symbol(type, bp).led = led

    def prefix(self, type, bp):
        def nud(self):
            self.fst = self.parser.expression(bp)
            return self
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


