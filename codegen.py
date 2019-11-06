#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
sys.dont_write_bytecode = True

REAL_FILE = os.path.abspath(__file__)
REAL_NAME = os.path.basename(REAL_FILE)
REAL_PATH = os.path.dirname(REAL_FILE)
if os.path.islink(__file__):
    LINK_FILE = REAL_FILE; REAL_FILE = os.path.abspath(os.readlink(__file__))
    LINK_NAME = REAL_NAME; REAL_NAME = os.path.basename(REAL_FILE)
    LINK_PATH = REAL_PATH; REAL_PATH = os.path.dirname(REAL_FILE)

'''
var x int = 4;
var y int = 5;
var d int = x * x + y * y;
print d;
'''

code = [
   ('GLOBALI', 'x'),
   ('CONSTI', 4),
   ('STORE', 'x'),
   ('GLOBALI', 'y'),
   ('CONSTI', 5),
   ('STORE', 'y'),
   ('GLOBALI', 'd'),
   ('LOAD', 'x'),
   ('LOAD', 'x'),
   ('MULI',),
   ('LOAD', 'y'),
   ('LOAD', 'y'),
   ('MULI',),
   ('ADDI',),
   ('STORE', 'd'),
   ('LOAD', 'd'),
   ('PRINTI',)
]

class Interpreter:
    def __init__(self):
        self.stack = []
        self.store = {}

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        return self.stack.pop()

    def run(self, code):
        self.pc = 0
        while self.pc < len(code):
            op, *opargs = code[self.pc]
            getattr(self, f'run_{op}')(*opargs)
            self.pc += 1

    def run_GLOBALI(self, name):
        self.store[name] = None

    def run_CONSTI(self, value):
        self.push(value)

    def run_STORE(self, name):
        self.store[name] = self.pop()

    def run_LOAD(self, name):
        self.push(self.store[name])

    def run_ADDI(self):
        self.push(self.pop() + self.pop())

    def run_MULI(self):
        self.push(self.pop() * self.pop())

    def run_PRINTI(self):
        print(self.pop())


interpreter = Interpreter()
interpreter.run(code)




class Transpiler:
    def __init__(self):
        self.stack = []
        self.code = ''

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        return self.stack.pop()

    def transpile(self, code):
        self.pc = 0
        while self.pc < len(code):
            op, *opargs = code[self.pc]
            getattr(self, f'x_{op}')(*opargs)
            self.pc += 1
        return self.code

    def x_GLOBALI(self, name):
        self.code += f'{name} = None\n'

    def x_CONSTI(self, value):
        self.push(repr(value))

    def x_STORE(self, name):
        self.code += f'{name} = {self.pop()}\n'

    def x_LOAD(self, name):
        self.push(name)

    def x_ADDI(self):
        right = self.pop()
        left = self.pop()
        self.push(f'{left} + {right}')

    def x_MULI(self):
        right = self.pop()
        left = self.pop()
        self.push(f'{left} * {right}')

    def x_PRINTI(self):
        self.code += f'print({self.pop()})\n'

transpiler = Transpiler()
src = transpiler.transpile(code)
print(src)
