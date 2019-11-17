#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wabbit.lexer import Token

from leatherman.dbg import dbg

class SymbolTable(dict):
    @staticmethod
    def make_key(obj):
        if isinstance(obj, Token):
            if obj.type in ('KEYWORD', 'SYNTAX', 'OP'):
                return obj.value
            elif obj.type in ('INT', 'FLOAT', 'BOOL'):
                return 'LITERAL'
        return obj

    def __getitem__(self, obj):
        key = SymbolTable.make_key(obj)
        return super().__getitem__(key)

    def __setitem__(self, obj, value):
        key = SymbolTable.make_key(obj)
        super().__setitem__(key, value)

class Symbol:
    lbp = 0
    Table = SymbolTable()

    def __init__(self, parser, token):
        self.parser = parser
        self.token = token

    @property
    def type(self):
        if self.token.type in ('SYNTAX',):
            return self.token.value
        return self.token.type

    @property
    def value(self):
        if self.token.type in ('INT', 'FLOAT', 'BOOL'):
            return self.token.value
        return None

    def __repr__(self):
        fields = ', '.join([
            f'parser={"yes" if self.parser else "no"}',
            f'token={self.token}',
            f'lbp={self.__class__.lbp}',
            f'type={self.type}',
            f'value={self.value}',
        ])
        return f'{self.__class__.__name__}({fields})'
