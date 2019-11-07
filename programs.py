#!/usr/bin/env python3

# programs.py
#
# Within the bowels of your compiler, you need to represent programs
# as data structures.   In this file, you will manually encode
# some simple Wabbit programs using the data model you've developed
# in the file wabbit/model.py
#
# The purpose of this exercise is two-fold:
#
#   1. Make sure you understand the data model of your compiler.
#   2. Have some program structures that you can use for later testing
#      and experimentation.
#
# This file is broken into sections. Follow the instructions for
# each part.  Parts of this file might be referenced in later
# parts of the project.  Plan to have a lot of discussion.
#

import sys
from subprocess import check_call

from wabbit.model import *
from wabbit.renderer import WabbitRenderer
from wabbit.checker import TypeChecker
from wabbit.irgenerator import IRGenerator
from wabbit.llvmgenerator import LLVMGenerator

from leatherman.dbg import dbg

def execute(name, source, model):
    print('*'*20)
    print(f'{name} source:')
    print(source)
    print(f'{name}, wabbit:')
    print(model)
    WabbitRenderer.render(model)
    print(f'{name}: type checking...')
    result = TypeChecker.check(model)
    print(f'{name}: generating ircode...')
    irmodule = IRGenerator.generate(model)
    print(irmodule)
    print(irmodule.functions)
    print(f'{name}: generating llvmcode...')
    llvmcode = LLVMGenerator.generate(irmodule)
    print(llvmcode)
    print(f'{name}: writing llvmcode...')
    with open(f'{name}.ll', 'w') as f:
        f.write(str(llvmcode))
    print(f'{name}: compiling llvmcode...')
    check_call(f'clang print.c {name}.ll -o {name}', shell=True)
    print(f'{name}: running llvmcode...')
    check_call(f'./{name}')


# ----------------------------------------------------------------------
# Simple Expression
#
# This one is given to you as an example.

expr_source = "2 + 3 * 4"

expr_model  = BinOp('+', Integer(2),
                         BinOp('*', Integer(3), Integer(4)))

# ----------------------------------------------------------------------
# Program 1: Printing
#
# Encode the following program which tests printing and simple expresions.
#
source1 = """
print 2 + 3 * -4;
print 2.0 - 3.0 / -4.0;
print -2 + 3;
"""

model1 = Prog([
    Print(BinOp(Name("+"), Integer(2), BinOp(Name("*"), Integer(3), Integer(-4)))),
    Print(BinOp(Name("-"), Float(2.0), BinOp(Name("/"), Float(3.0), Float(-4.0)))),
    Print(BinOp(Name("+"), Integer(-2), Integer(3))),
])

execute('example1', source1, model1)

# ----------------------------------------------------------------------
# Program 2: Variable and constant declarations.
#            Expressions and assignment.
#
# Encode the following statements.

source2 = """
const pi = 3.14159;
var tau float;
tau = 2.0 * pi;
print(tau);
"""

model2 = Prog([
    Definition(Name("pi"), Type("float"), Float(3.14159)),
    Definition(Name('tau'), Type("float")),
    Assignment(Name("tau"), BinOp(Name("*"), Float(2.0), Name("pi"))),
    Print(Name("tau")),
])

execute('example2', source2, model2)

# ----------------------------------------------------------------------
# Program 3: Conditionals.  This program prints out the minimum of
# two values.
#
source3 = '''
var a int = 2;
var b int = 3;
if a < b {
    print a;
} else {
    print b;
}
'''

model3 = Prog([
    Definition(Name("a"), Type("int"), Integer(2)),Definition(Name("b"), Type("int"), Integer(3)),
    If(BinOp(Name("<"), Name("a"), Name("b")), Block([Print(Name("a"))]), Block([Print(Name("b"))])),
])

execute('example3', source3, model3)

# ----------------------------------------------------------------------
# Program 4: Loops.  This program prints out the first 10 factorials.
#
source4 = '''
const n = 10;
var x int = 1;
var fact int = 1;

while x < n {
    fact = fact * x;
    print fact;
    x = x + 1;
}
'''

model4 = Prog([
    Definition(Name("n"), Type('undef'), Integer(10), mutable=False),
    Definition(Name("x"), Type('int'), Integer(1)),
    Definition(Name("fact"), Type('int'), Integer(1)),
    While(BinOp(Name("<"), Name("x"), Name("n")), Block([
        Assignment(Name("fact"), BinOp(Name("*"), Name("fact"), Name("x"))),
        Print(Name("fact")),
        Assignment(Name("x"), BinOp(Name("+"), Name("x"), Integer(1))),
    ]))
])

execute('example4', source4, model4)
sys.exit(0)

# ----------------------------------------------------------------------
# Program 5: Functions (simple)
#

source5 = '''
func square(x int) int {
    return x*x;
}

print square(4);
print square(10);
'''

model5 = Prog([
    Func(Name("square"), [Parameter(Name("x"), Type("int"))], Type("int"), Block([
        Return(BinOp(Name("*"), Name("x"), Name("x"))),
    ])),
    Print(Call(Name("square"), [Integer(4)])),
    Print(Call(Name("square"), [Integer(10)])),
])

execute('example5', source5, model5)

# ----------------------------------------------------------------------
# Program 6: Functions (complex)
#

source6 = '''
func fact(n int) int {
    var x int = 1;
    var result int = 1;
    while x < n {
        result = result * x;
        x = x + 1;
    }
    return result;
}

print(fact(10));
'''

model6 = Prog([])

execute('example6', source6, model6)

# ----------------------------------------------------------------------
# Program 7 : Type casting
#

source7 = '''
var pi = 3.14159;
var spam = 42;

print(spam * int(pi));
print(float(spam) * pi);
print(int(spam) * int(pi));
'''

model7 = Prog([])

execute('example7', source7, model7)

# ----------------------------------------------------------------------
# Program 8 : Memory access
#

source8 = '''
var x int = ^8192;        // Grow memory by 8192 bytes
var addr int = 1234;
`addr = 5678;             // Stores 5678 at addr
`(addr + 8) = `addr + 8;
print(`addr + 8);
'''

model8 = Prog([])

execute('example8', source8, model8)
