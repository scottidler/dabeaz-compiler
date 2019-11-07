# ircode.py
'''
A Intermediate "Virtual" Machine
================================
An actual CPU typically consists of registers and a small set of basic
opcodes for performing mathematical calculations, loading/storing
values from memory, and basic control flow (branches, jumps, etc.).
Although you can make a compiler generate instructions directly for a
CPU, it is often simpler to target a higher-level of abstraction
instead.  One such abstraction is that of a stack machine.

For example, suppose you want to evaluate an operation like this:

    a = 2 + 3 * 4 - 5

To evaluate the above expression, you could generate
pseudo-instructions like this instead:

    CONSTI 2      ; stack = [2]
    CONSTI 3      ; stack = [2, 3]
    CONSTI 4      ; stack = [2, 3, 4]
    MULI          ; stack = [2, 12]
    ADDI          ; stack = [14]
    CONSTI 5      ; stack = [14, 5]
    SUBI          ; stack = [9]
    LOCAL_SET "a" ; stack = []

Notice how there are no details about CPU registers or anything like
that here. It's much simpler (a lower-level module can figure out the
hardware mapping later if it needs to).

CPUs usually have a small set of code datatypes such as integers and
floats.  There are dedicated instructions for each type.  The IR code
will follow the same principle by supporting integer and floating
point operations. For example:

    ADDI   ; Integer add
    ADDF   ; Float add

Although the input language might have other types such as 'bool' and
'char', those types need to be mapped down to integers or floats. For
example, a bool can be represented by an integer with values {0, 1}. A
char can be represented by an integer whose value is the same as
the character code value (i.e., an ASCII code or a Unicode code-point).

With that in mind, here is a basic instruction set for our IR Code:

    ; Integer operations
    CONSTI  value            ; Push a integer literal on the stack
    ADDI                     ; Add top two items on stack
    SUBI                     ; Substract top two items on stack
    MULI                     ; Multiply top two items on stack
    DIVI                     ; Divide top two items on stack
    ANDI                     ; Bitwise AND
    ORI                      ; Bitwise OR
    LTI                      : <
    LEI                      : <=
    GTI                      : >
    GEI                      : >=
    EQI                      : ==
    NEI                      : !=
    PRINTI                   ; Print top item on stack
    PEEKI                    ; Get integer from memory (address on stack)
    POKEI                    ; Put integer in memory (value, address) on stack.
    ITOF                     ; Convert integer to float

    ; Floating point operations
    CONSTF value             ; Push a float literal
    ADDF                     ; Add top two items on stack
    SUBF                     ; Substract top two items on stack
    MULF                     ; Multiply top two items on stack
    DIVF                     ; Divide top two items on stack
    LTF                      : <
    LEF                      : <=
    GTF                      : >
    GEF                      : >=
    EQF                      : ==
    NEF                      : !=
    PRINTF                   ; Print top item on stack
    PEEKF                    ; Get float from memory (address on stack)
    POKEF                    ; Put float in memory (value, address on stack)
    FTOI                     ; Convert float to integer

    ; Byte-oriented operations (values are presented as integers)
    PRINTB                   ; Print top item on stack
    PEEKB                    ; Get byte from memory (address on stack)
    POKEB                    ; Put byte in memory (value, address on stack)

    ; Variable load/store.
    ; These instructions read/write both local and global variables. Variables
    ; are referenced by some kind of name that identifies the variable.  The management
    ; and declaration of these names must also be handled by your code generator.
    ; However, variable declarations are not a normal "instruction."  Instead, it's
    ; a kind of data that needs to be associated with a module or function.
    LOCAL_GET name           ; Read a local variable onto stack
    LOCAL_SET name           ; Save local variable from stack
    GLOBAL_GET name          ; Read a global variable onto the stack
    GLOBAL_SET name          ; Save a global variable from the stack

    ; Function call and return.
    ; Functions are referenced by name.   Your code generator will need to figure
    ; out some way to manage these names.
    CALL name                ; Call function. All arguments must be on stack
    RET                      ; Return from a function. Value must be on stack

    ; Structured control flow
    IF                       ; Start consequence part of an "if". Test on stack
    ELSE                     ; Start alternative part of an "if".
    ENDIF                    ; End of an "if" statement.

    LOOP                     ; Start of a loop
    CBREAK                   ; Conditional break. Test on stack.
    CONTINUE                 ; Go back to loop start
    ENDLOOP                  ; End of a loop

    ; Memory
    GROW                     ; Increment memory (size on stack) (returns new size)

One word about memory access... the PEEK and POKE instructions are
used to access raw memory addresses.  Both instructions require a
memory address to be on the stack *first*.  For the POKE instruction,
the value being stored is pushed after the address. The order is
important and it's easy to mess it up.  So pay careful attention to
that.

Your Task
=========
Your task is as follows: Write code that walks through the program structure
and flattens it to a sequence of instructions represented as tuples of the
form:

       (operation, operands, ...)

For example, the code at the top might end up looking like this:

    code = [
       ('CONSTI', 2),
       ('CONSTI', 3),
       ('CONSTI', 4),
       ('MULI',),
       ('ADDI',),
       ('CONSTI', 5),
       ('SUBI',),
       ('LOCAL_SET', 'a'),
    ]

Functions
=========
All generated code is associated with some kind of function.  For
example, with a user-defined function like this:

    func fact(n int) int {
        var result int = 1;
        var x int = 1;
        while x <= n {
            result = result * x;
            x = x + 1;
        }
     }

You should create a Function object that contains the name of the
function, the arguments, the return type, local variables, and a body
which contains all of the low-level instructions.  Note: at this
level, the types are going to represent low-level IR types like
Integer (I) and Float (F).  They are not the same types as used in the
high-level Wabbit code.

Also, all code that's defined *outside* of a Function should still
go into a function called "_init()".  For example, if you have
global declarations like this:

     const pi = 3.14159;
     const r = 2.0;
     print pi*r*r;

Your code generator should actually treat them like this:

     func _init() int {
         const pi = 3.14159;
         const r = 2.0;
         print pi*r*r;
         return 0;
     }

Bottom line: All code goes into a function.

Modules
=======
The final output of code generation should be some kind of Module object that
holds everything. The module includes function objects, global variables, and
anything else you might need to generate code later.
'''

from typing import List, Dict
from dataclasses import dataclass

from wabbit.model import *
from wabbit.visitor import Visitor

@dataclass
class IRFunction:
    module: 'IRModule'
    name: str
    return_type: str
    code: List[tuple]
    params: Dict[str, str] = field(default_factory=dict)
    locals: Dict[str, str] = field(default_factory=dict)

@dataclass
class IRModule:
    functions = List[IRFunction]
    globals: Dict[str, str] = field(default_factory=dict)

class IRGenerator(Visitor):

    @classmethod
    def generate(cls, model):
        assert model is not None, "model=None passed to IRGenerator.generate"
        generator = cls()
        module = IRModule()
        main = IRFunction(module, "main", None, [], [])
        model.accept(generator, main)
        module.functions = [main]
        return module

    def visit(self, prog: Prog, func):
        errors = []
        errors += [self.visit(stmt, func) for stmt in prog.stmts]
        return errors

    def visit(self, print: Print, func):
        errors = []
        dbg(print, func)
        errors += self.visit(print.expr, func)
        if print.expr.type == Type('int'):
            func.code += [('PRINTI',)]
        elif print.expr.type  == Type('float'):
            func.code += [('PRINTF',)]
        return errors

    def visit(self, binop: BinOp, func):
        errors = []
        errors += self.visit(binop.left, func)
        errors += self.visit(binop.right, func)
        if binop.left.type == Type('int'):
            if binop.operator == Name('+'):
                func.code += [('ADDI',)]
            if binop.operator == Name('-'):
                func.code += [('SUBI',)]
            if binop.operator == Name('*'):
                func.code += [('MULI',)]
            if binop.operator == Name('/'):
                func.code += [('DIVI',)]
        elif binop.right.type == Type('float'):
            if binop.operator == Name('+'):
                func.code += [('ADDF',)]
            if binop.operator == Name('-'):
                func.code += [('SUBF',)]
            if binop.operator == Name('*'):
                func.code += [('MULF',)]
            if binop.operator == Name('/'):
                func.code += [('DIVF',)]
        return errors

    def visit(self, integer: Integer, func):
        errors = []
        func.code += [('CONSTI', str(integer.value))]
        return errors

    def visit(self, float: Float, func):
        errors = []
        func.code += [('CONSTF', str(float.value))]
        return errors

    def visit(self, name: Name, func):
        dbg(vars_name=vars(name))
        if getattr(name, 'lvalue', False):
            self.generate(name.value, func)
            func.code += [('GLOBAL_SET', name.value)]
        else:
            func.code += [('GLOBAL_GET', name.value)]

    def visit(self, definition: Definition, func):
        if definition.type in (Type('int'), Type('bool'), Type('char')):
            g_irtype = 'I'
        elif definition.type  == Type('float'):
            g_irtype = 'F'

        func.module.globals[definition.name.value] = g_irtype

        if definition.value:
            self.visit(definition.value, func)
            func.code += [('GLOBAL_SET', definition.name)]

    def visit(self, assignment: Assignment, func):
        pass

