#!/usr/bin/env python3

from typing import Any
from dataclasses import dataclass

NL = '\n'

def printf(expr):
    sys.stdout.write(expr)

@dataclass
class Node:
    def to_code(self):
        msg = f"to_code must be implemented for {self.__class__.__name__}"
        raise NotImplementedError(msg)

@dataclass
class Expression(Node):
    pass

@dataclass
class Statement(Node):
    pass

@dataclass
class Block(Node):
    stmts: [Statement]

    def to_code(self, prefix='{\n', suffix='\n}\n'):
        return f"{prefix}{NL.join([stmt.to_code() for stmt in self.stmts])}{suffix}"

@dataclass
class Prog(Block):
    def to_code(self):
        return super(Prog, self).to_code(prefix='', suffix='')

@dataclass
class Type(Node):
    name: str

    def to_code(self):
        return self.name

@dataclass
class Literal(Expression):
    def to_code(self):
        return str(self.value)

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
    def to_code(self):
        return ""

    def __bool__(self):
        return False

@dataclass
class Name(Expression):
    name: str

    def to_code(self):
        return self.name

@dataclass
class Definition(Statement):
    name: Name
    value: Expression = Undef()
    type: Type = Undef()
    mutable: bool = True

    def to_code(self):
        prefix = "var" if self.mutable else "const"
        suffix = f" = {self.value.to_code()}" if self.value else ""
        return f"{prefix} {self.name.to_code()} {self.type.to_code()}{suffix};"

@dataclass
class BinOp(Expression):
    operator: Name
    left: Expression
    right: Expression

    def to_code(self):
        return f"({self.left.to_code()} {self.operator.to_code()} {self.right.to_code()})"

@dataclass
class UnOp(Expression):
    operator: Name
    expr: Expression

    def to_code(self):
        return f"{self.operator.to_code()}{self.expr.to_code()}"

@dataclass
class Location(Node):
    index: int

    def to_code(self):
        return f"{self.index}"

@dataclass
class Assignment(Statement):
    loc: Location
    expr: Expression

    def to_code(self):
        return f"{self.loc.to_code()} = {self.expr.to_code()};"

@dataclass
class Cast(Expression):
    type: Type
    expr: Expression

    def to_code(self):
        return f"{self.type.to_code()}(self.expr.to_code())"

@dataclass
class Print(Statement):
    expr: Expression

    def to_code(self):
        return f"print {self.expr.to_code()};"

@dataclass
class If(Statement):
    test: Expression
    consequence: Block
    alternative: Block

    def to_code(self):
        return f"if {self.test.to_code()} {self.consequence.to_code()}else {self.alternative.to_code()}"

@dataclass
class While(Statement):
    test: Expression
    block: Block

    def to_code(self):
        return f"while {self.test.to_code()} {self.block.to_code()}"

@dataclass
class Break(Statement):
    def to_code(self):
        return "break;"

@dataclass
class Continue(Statement):
    def to_code(self):
        return "continue;"

@dataclass
class Return(Statement):
    expr: Expression

    def to_code(self):
        return f"return {self.expr.to_code()};"

@dataclass
class Parameter(Node):
    name: Name
    type: Type
    value: Expression = Undef()

    def to_code(self):
        suffix = f" = {self.value.to_code()}" if self.value else ""
        return f"{self.name.to_code()} {self.type.to_code()}{suffix}"

@dataclass
class Func(Statement):
    name: Name
    params: [Parameter]
    type: Type
    block: Block

    def to_code(self):
        params = ', '.join([param.to_code() for param in self.params])
        return f"func {self.name.to_code()}({params}) {self.type.to_code()} {self.block.to_code()}"

@dataclass
class Import(Statement):
    name: Name
    params: [Parameter]
    type: Type

    def to_code(self):
        return f"import {self.name.to_code()} ({','.join([param.to_code() for param in self.params])});"

@dataclass
class Call(Expression):
    name: Name
    params: [Expression]

    def to_code(self):
        args = ', '.join([param.to_code() for param in self.params])
        return f"{self.name.to_code()}({args})"
