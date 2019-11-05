#!/usr/bin/env python3

from typing import Any
from dataclasses import dataclass
from multimethod import multimeta

NL = '\n'

def printf(expr):
    sys.stdout.write(expr)

@dataclass
class Node:
    def to_code(self):
        msg = f'to_code must be implemented for {self.__class__.__name__}'
        raise NotImplementedError(msg)

    def accept(self, visitor):
        return visitor.visit(self)

@dataclass
class Expression(Node):
    pass

@dataclass
class Statement(Node):
    pass

@dataclass
class Block(Node):
    stmts: [Statement]

@dataclass
class Prog(Block):
    pass

@dataclass
class Type(Node):
    value: str

@dataclass
class Literal(Expression):
    pass

@dataclass
class Integer(Literal):
    value: int

@dataclass
class Float(Literal):
    value: float

@dataclass
class Boolean(Literal):
    value: bool

@dataclass
class Char(Literal):
    value: str

@dataclass
class Undef(Expression):
    def __bool__(self):
        return False

@dataclass
class Name(Expression):
    value: str

@dataclass
class Definition(Statement):
    name: Name
    value: Expression = Undef()
    type: Type = Undef()
    mutable: bool = True

@dataclass
class BinOp(Expression):
    operator: Name
    left: Expression
    right: Expression

@dataclass
class UnOp(Expression):
    operator: Name
    expr: Expression

@dataclass
class Location(Node):
    value: int

@dataclass
class Assignment(Statement):
    loc: Location
    expr: Expression

@dataclass
class Cast(Expression):
    type: Type
    expr: Expression

@dataclass
class Print(Statement):
    expr: Expression

@dataclass
class If(Statement):
    test: Expression
    consequence: Block
    alternative: Block

@dataclass
class While(Statement):
    test: Expression
    block: Block

@dataclass
class Break(Statement):
    pass

@dataclass
class Continue(Statement):
    pass

@dataclass
class Return(Statement):
    expr: Expression

@dataclass
class Parameter(Node):
    name: Name
    type: Type
    value: Expression = Undef()

@dataclass
class Func(Statement):
    name: Name
    params: [Parameter]
    type: Type
    block: Block

@dataclass
class Import(Statement):
    name: Name
    params: [Parameter]
    type: Type

@dataclass
class Call(Expression):
    name: Name
    params: [Expression]

class Visitor(metaclass=multimeta):
    pass

class WabbitRenderer(Visitor):

    def visit(self, undef: Undef):
        return ''

    def visit(self, type: Type):
        return type.value

    def visit(self, name: Name):
        return name.value

    def visit(self, literal: Literal):
        return str(literal.value)

    def visit(self, location: Location):
        return location.value

    def visit(self, unop: UnOp):
        return f'{self.visit(unop.operator)}{self.visit(unop.expr)}'

    def visit(self, binop: BinOp):
        return f'({self.visit(binop.left)} {self.visit(binop.operator)} {self.visit(binop.right)})'

    def visit(self, definition: Definition):
        prefix = 'var' if definition.mutable else 'const'
        suffix = f' = {self.visit(definition.value)}' if definition.value else ''
        return f'{prefix} {self.visit(definition.name)} {self.visit(definition.type)}{suffix};'

    def visit(self, assignment: Assignment):
        return f'{self.visit(assignment.loc)} = {self.visit(assignment.expr)};'

    def visit(self, cast: Cast):
        return f'{self.visit(cast.type)}({self.visit(cast.expr)})'

    def _render_block(self, stmts, prefix='{\n', suffix='\n}\n'):
        return f'{prefix}{NL.join([self.visit(stmt) for stmt in stmts])}{suffix}'

    def visit(self, block):
        return self._render_block(block.stmts)

    def visit(self, prog):
        return self._render_block(prog.stmts, prefix='', suffix='')

    def visit(self, print: Print):
        return f'print {self.visit(print.expr)};'

    def visit(self, if_: If):
        return f'if {self.visit(if_.test)} {self.visit(if_.consequence)}else {self.visit(if_.alternative)}'

    def visit(self, while_: While):
        return f'while {self.visit(while_.test)} {self.visit(while_.block)}'

    def visit(self, break_: Break):
        return 'break;'

    def visit(self, continue_: Continue):
        return 'continue;'

    def visit(self, return_: Return):
        return f'return {self.visit(return_.expr)};'

    def visit(self, param: Parameter):
        suffix = f' = {self.visit(param.value)}' if param.value else ''
        return f'{self.visit(param.name)} {self.visit(param.type)}{suffix}'

    def visit(self, func: Func):
        params = ', '.join([self.visit(param) for param in func.params])
        return f'func {self.visit(func.name)}({params}) {self.visit(func.type)} {self.visit(func.block)}'

    def visit(self, import_: Import):
        params = ', '.join([self.visit(param) for param in func.params])
        return f'import {self.visit(import_.name)} ({params});'

    def visit(self, call: Call):
        args = ', '.join([self.visit(param) for param in call.params])
        return f"{self.visit(call.name)}({args})"

