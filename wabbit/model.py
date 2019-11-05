#!/usr/bin/env python3

from typing import Any
from dataclasses import dataclass

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


