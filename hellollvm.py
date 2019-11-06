#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
sys.dont_write_bytecode = True

from llvmlite.ir import Module, Function, FunctionType, IntType, IRBuilder, Constant

module = Module('hellollvm')
func = Function(module, FunctionType(IntType(32), []), name = 'hellollvm')
block = func.append_basic_block('entry')
builder = IRBuilder(block)
builder.ret(Constant(IntType(32), 37))
print(module)
