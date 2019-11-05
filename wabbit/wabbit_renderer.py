#!/usr/bin/env python3

from wabbit.visitor import Visitor
from wabbit.model import *

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

