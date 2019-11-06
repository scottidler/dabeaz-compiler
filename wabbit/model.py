#!/usr/bin/env python3

from typing import Any, List
from dataclasses import dataclass, field

from wabbit.visitor import Visitor

from leatherman.dbg import dbg

NL = '\n'

def printf(expr):
    sys.stdout.write(expr)

@dataclass
class Type:
    value: str

@dataclass
class Node:
    def accept(self, visitor: Visitor, *args, **kwargs):
        return visitor.visit(self, *args, **kwargs)

@dataclass
class Expression(Node):
    pass

@dataclass
class Statement(Node):
    pass

@dataclass
class Block(Node):
    stmts: List[Statement] = field(default_factory=list)

@dataclass
class Prog(Block):
    pass

@dataclass
class Literal(Expression):
    pass

@dataclass
class Integer(Literal):
    value: int
    type: Type = Type('int')

@dataclass
class Float(Literal):
    value: float
    type: Type = Type('float')

@dataclass
class Boolean(Literal):
    value: bool
    type: Type = Type('bool')

@dataclass
class Char(Literal):
    value: str
    type: Type = Type('char')

@dataclass
class Undef(Expression):
    type: Type = Type('undef')
    def __bool__(self):
        return False

@dataclass
class Name(Expression):
    value: str

@dataclass
class Definition(Statement):
    name: Name
    type: Type
    value: Expression = Undef()
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

@dataclass
class Call(Expression):
    name: Name
    params: [Expression]


