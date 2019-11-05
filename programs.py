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

from wabbit.model import *

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
    Print(BinOp(Name("+"), Integer(2), BinOp(Name("*"), Integer(3), Float(-4.0)))),
    Print(BinOp(Name("-"), Float(2.0), BinOp(Name("/"), Float(3.0), Float(-4.0)))),
    Print(BinOp(Name("+"), Integer(-2), Integer(3))),
])
print("source:")
print(source1)
print("render:")
print(model1.to_code())
print()

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
    Definition(Name("tau"), Type("float")),
    Assignment(Name("tau"), BinOp(Name("*"), Float(2.0), Name("pi"))),
    Print(Name("tau")),
])

print("source:")
print(source2)
print("render:")
print(model2.to_code())
print()

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

print("source:")
print(source3)
print("render:")
print(model3.to_code())
print()

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
    Definition(Name("n"), Integer(10), mutable=False),
    Definition(Name("x"), Integer(1), Type("int")),
    Definition(Name("fact"), Integer(1), Type("int")),
    While(BinOp(Name("<"), Name("x"), Name("n")), Block([
        Assignment(Name("fact"), BinOp(Name("*"), Name("fact"), Name("x"))),
        Print(Name("fact")),
        Assignment(Name("x"), BinOp(Name("+"), Name("x"), Integer(1))),
    ]))
])

print("source:")
print(source4)
print("render:")
print(model4.to_code())
print()
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

print("source:")
print(source5)
print("render:")
print(model5.to_code())
print()
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

model6 = None

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

model7 = None

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

model8 = None
