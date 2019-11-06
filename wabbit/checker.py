#!/usr/bin/env python3

# check.py
#
# This file will have the type-checking/validation
# part of the compiler.  There are a number of things
# that need to be managed to make this work. First,
# you have to have some notion of "type" in your compiler.
# Second, you need to manage environments/scoping in order
# to handle the names of definitions (variables, functions, etc).
#
# A key to this part of the project is going to be proper
# testing.  As you add code, think about how you might test it.

from itertools import chain

from wabbit.visitor import Visitor
from wabbit.model import *
from wabbit.errors import *
from wabbit.env import Env

from leatherman.dbg import dbg

class TypeResolver(Visitor):

    _binop_rules = {
        ('+', 'int', 'int'): 'int',
        ('-', 'int', 'int'): 'int',
        ('*', 'int', 'int'): 'int',
        ('/', 'int', 'int'): 'int',

        ('>', 'int', 'int'): 'bool',
        ('<', 'int', 'int'): 'bool',
        ('>=', 'int', 'int'): 'bool',
        ('<=', 'int', 'int'): 'bool',
        ('==', 'int', 'int'): 'bool',
        ('!=', 'int', 'int'): 'bool',

        ('+', 'float', 'float'): 'float',
        ('-', 'float', 'float'): 'float',
        ('*', 'float', 'float'): 'float',
        ('/', 'float', 'float'): 'float',

        ('>', 'float', 'float'): 'bool',
        ('<', 'float', 'float'): 'bool',
        ('>=', 'float', 'float'): 'bool',
        ('<=', 'float', 'float'): 'bool',
        ('==', 'float', 'float'): 'bool',
        ('!=', 'float', 'float'): 'bool',
    }

    def visit(self, binop: BinOp):
        key = (binop.operator.value, binop.left.type.value, binop.right.type.value)
        result = self._binop_rules.get(key)
        if result:
            return Type(result)
        return result

class TypeChecker(Visitor):

    resolver: TypeResolver = TypeResolver()

    env: Env = Env()

    def visit(self, undef: Undef, env: Env):
        errors = []
        return errors

    def visit(self, type: Type, env: Env):
        errors = []
        return errors

    def visit(self, name: Name, env: Env):
        errors = []
        result = env.get(name.value)
        if result is not None:
            name.type = result.type
        else:
            errors += [NameLookupError('name lookup error', name)]
        return errors

    def visit(self, literal: Literal, env: Env):
        errors = []
        return errors

    def visit(self, location: Location, env: Env):
        errors = []
        return errors

    def visit(self, unop: UnOp, env: Env):
        errors = []
        errors += self.visit(unop.expr, env)
        return errors

    def visit(self, binop: BinOp, env: Env):
        errors = []
        errors += self.visit(binop.left, env)
        errors += self.visit(binop.right, env)
        type = self.resolver.visit(binop)
        if type:
            binop.type = type
        else:
            errors += [TypeResolveError("type resolve error", binop)]
        assert hasattr(binop, 'type'), dbg('missing type annotation', binop)

        assert type is not None, "uh oh sucker!"
        return errors

    def visit(self, definition: Definition, env: Env):
        errors = []
        errors += self.visit(definition.value, env)
        env[definition.name.value] = definition.value
        return errors

    def visit(self, assignment: Assignment, env: Env):
        errors = []
        errors += self.visit(assignment.loc, env)
        errors += self.visit(assignment.expr, env)
        return errors

    def visit(self, cast: Cast, env: Env):
        errors = []
        errors += self.visit(cast.expr, env)
        return errors

    def visit(self, block: Block, env: Env):
        errors = []
        errors += chain(*[self.visit(stmt, env) for stmt in block.stmts])
        return errors

    def visit(self, prog: Prog, env: Env):
        errors = []
        errors += chain(*[self.visit(stmt, env) for stmt in prog.stmts])
        return errors

    def visit(self, print: Print, env: Env):
        errors = []
        errors += self.visit(print.expr, env)
        return errors

    def visit(self, if_: If, env: Env):
        errors = []
        errors += self.visit(if_.test, env)
        errors += self.visit(if_.consequence, env)
        errors += self.visit(if_.alternative, env)
        return errors

    def visit(self, while_: While, env: Env):
        errors = []
        errors += self.visit(while_.test, env)
        errors += self.visit(while_.block, env)
        return errors

    def visit(self, break_: Break, env: Env):
        errors = []
        return errors

    def visit(self, continue_: Continue, env: Env):
        errors = []
        return errors

    def visit(self, return_: Return, env: Env):
        errors = []
        errors += self.visit(return_.expr, env)
        return errors

    def visit(self, param: Parameter, env: Env):
        errors = []
        errors += self.visit(param.value, env)
        return errors

    def visit(self, func: Func, env: Env):
        errors = []
        errors += chain(*[self.visit(param, env) for param in func.params])
        errors += self.visit(func.block, env)
        return []

    def visit(self, import_: Import, env: Env):
        errors = []
        errors += chain(*[self.visit(param, env) for param in import_.params])
        return errors

    def visit(self, call: Call, env: Env):
        errors = []
        errors += chain(*[self.visit(param, env) for param in call.params])
        return errors
