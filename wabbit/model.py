# model.py
#
# This file defines a data model for Wabbit programs.  Basically, the
# data model is a large data structure that represents the contents of
# a program as objects, not text.  Sometimes this structure is known
# as an "abstract syntax tree" or AST.  However, the model is not
# necessarily directly tied to the actual syntax of the language.  So,
# we'll prefer to think of it as a more generic data model instead.
#
# To do this, you need to identify the different "elements" that make 
# up a program and encode them into classes.  To do this, it may be
# useful to "underthink" the problem. To illustrate, suppose you
# wanted to encode the idea of "assigning a value."   Assignment involves
# a location (the left hand side) and a value like this:
#
#         location = expression;
#
# To represent this idea, make a class with just those parts:
#
#     class Assignment:
#         def __init__(self, location, expression):
#             self.location = location
#             self.expression = expression
#
# Now, what are "location" and "expression"?  Does it matter? Maybe
# not. All you know is that an assignment operator requires both of
# those parts.  DON'T OVERTHINK IT.  Further details will be filled in
# as the project evolves.
# 
# This file is broken up into sections that describe part of the
# Wabbit language specification in comments.   You'll need to adapt
# this to actual code.  To help guide you, look at the file "programs.py"
# in the top-level directory.
#
# Starting out, I'd advise against making this file too fancy. Just
# use basic Python class definitions.  You can add usability improvements
# later.

# ----------------------------------------------------------------------
# Part 1. Statements.
#
# Wabbit programs consist of statements.  Statements are related to
# things like assignment, I/O (printing), control-flow, and other operations.
#
# 1.1 Assignment
#
#     location = expression ;
#

class Assignment:
    def __init__(self, location, expression):
        self.location = location
        self.expression = expression

    def __repr__(self):
        return f'Assignment({self.location}, {self.expression})'

#
# 1.2 Printing
#
#     print expression ;
#
# 1.3 Conditional
#
#     if test { consequence} else { alternative }
#
# 1.4 While Loop
#
#  while test { body }
#
# 1.5 Break and Continue
#
#   while test {
#       ...
#       break;   // continue
#   }
#
# 1.6 Return a value
#
#  return expression ; 
#

# ----------------------------------------------------------------------
# Part 2. Definitions/Declarations
#
# Wabbit requires all variables and functions to be declared in 
# advance.  All definitions have a name that identifies it.  These names
# are defined within an environment that forms a so-called "scope."  
# For example, global scope or local scope. 
#
# 2.1 Variables.  Variables can be declared in a few different forms.
#
#    const name = value;
#    const name [type] = value;
#    var name type [= value];
#    var name [type] = value;
#
# Constants are immutable.  If a value is present, the type can be
# ommitted and inferred from the type of the value.
#
# 2.2 Function definitions.
#
#    func name(parameters) return_type { statements }
#
# An external functions can be imported from using the special statement:
#
#    import func name(parameters) return_type;
#
#
# 2.3 Function Parameters
#
#       func square(x int) int { return x*x; }
#
# A function parameter (e.g., "x int") is a special kind of
# variable. It has a name and type like a variable, but it is declared
# as part of the function definition itself, not as a separate "var"
# declaration.

# ----------------------------------------------------------------------
# Part 3: Expressions.
#
# Expressions represent things that evaluate to a concrete value.
#
# Wabbit defines the following expressions and operators
#
# 3.1 Literals
#        23            (Integer literal)
#        4.5           (Float literal)
#        true,false    (Bool literal)
#        'c'           (Character literal - A single character)
#
# 3.2 Binary Operators
#        left + right        (Addition)
#        left - right        (Subtraction)
#        left * right        (Multiplication)
#        left / right        (Division)
#        left < right        (Less than)
#        left <= right       (Less than or equal)
#        left > right        (Greater than)
#        left >= right       (Greater than or equal)
#        left == right       (Equal to)
#        left != right       (Not equal)
#        left && right       (Logical and)
#        left || right       (Logical or)
#
# 3.3 Unary Operators
#        +operand       (Positive)
#        -operand       (Negation)
#        !operand       (logical not)
#        ^operand       (Grow memory)
#
# 3.4 Reading from a location  (see below)
#        location       
#
# 3.5 Type-casts
#         int(expr)  
#         float(expr)
#
# 3.6 Function/Procedure Call
#        func(arg1, arg2, ..., argn)
#  

# ----------------------------------------------------------------------
# Part 4 : Locations
#
# A location represents a place where a value is stored.  The tricky
# thing about locations is that they are used in two different ways.
# First, a location could appear on the left-hand-side of an assignment
# like this:
#
#      location = expression;     // Stores a value into location
#
# However, a location could also appear as part of an expression:
#
#      print location + 10;       // Reads a value from location
#
# A location is not necessarily a simple variable name.  For example,
# consider the following example in Python:
#
#       >>> a = [1,2,3,4]
#       >>> a[2] = 10            # Store in location "a[2]"
#       >>> print(a[2])          # Read from location "a[2]"
#
# Wabbit has two types of locations:
#
# 4.1 Primitive.  A bare variable name such as "abc"
#
#       abc = 123;
#       print abc;
#
#     Any name used must refer to an existing definition of
#     a variable.  For example, "abc" in this example must have
#     a corresponding declaration such as 
#
#           var abc int;
#
# 4.2 Memory Addresses. An integer prefixed by backtick (`)
#
#       `address = 123;          
#       print `address + 10; 
#
# Note: Historically, understanding the nature of locations has been
# one of the most difficult parts of the compiler project.  Expect
# much further discussion around this topic.  I strongly suggest
# deferring work on addresses until much later in the project.