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
    #env: Env = Env()

    @classmethod
    def check(cls, model):
        checker = cls()
        env = Env()
        errors = model.accept(checker, env)
        for error in errors:
            print(error)
        else:
            return True
        return False

    def visit(self, undef: Undef, env: Env):
        errors = []
        return errors

    def visit(self, type: Type, env: Env):
        errors = []
        return errors

#def check_Name(node, env):
#    if node.name not in env:
#        error(f"Undefined name {node.name}")   # Error in Wabbit
#        node.type = None
#    else:
#        decl = env[node.name]   # Get the declaration
#        node.type = decl.type
#        node.mutable = decl.mutable

    def visit(self, name: Name, env: Env):
        errors = []
        if name.value not in env:
            errors += [NameLookupError(f'undefined name {name.value}', name)]
            name.type = Type('undef')
        else:
            decl = env[name.value]
            name.type = decl.type
            name.mutable = decl.mutable
        return errors
#        result = env.get(name.value)
#        if result is not None:
#            name.type = result.type
#            name.expr = result.value
#        else:
#            errors += [NameLookupError('name lookup error', name)]
#        assert hasattr(name, 'type'), 'uh oh, no type'
#        return errors

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

#def check_VariableDefinition(node, env):
#    # Is it already defined in local scope?  (duplicate definitions)
#    # If both type and value, do types match?  (var x int = 2.3;)
#
#    if node.value:
#        check(node.value, env)
#        # If no type set on var decl, propagate from value
#        if not node.type:
#            node.type = node.value.type
#        if node.type != node.value.type:
#            error(f"Type error. {node.type} = {node.value.type}")
#
#    env[node.name] = node    # Save a reference to the definition

    def visit(self, definition: Definition, env: Env):
        errors = []
        definition.name.lvalue = True
        if definition.value:
            self.visit(definition.value, env)
            if not definition.type:
                definition.type = definition.value.type
            if definition.type != definition.value.type:
                errors += [TypeMismatchError('type mismatch in definition checker', definition)]
        env[definition.name.value] = definition
        return errors
#        errors = []
#        definition.name.lvalue = True
#        errors += self.visit(definition.value, env)
#        env[definition.name.value] = definition.value
#        return errors

#def check_Assignment(node, env):
#    # Left type == right type
#    # Left side must be mutable
#    check(node.location, env)
#    check(node.expression, env)
#​
#    # This is "wishful thinking" coding.  Write code for what you wish
#    # you had.   Then make it work (somehow)
#    if node.location.type != node.expression.type:
#        error(f'Type error {node.location.type} = {node.expression.type}')
#    if not node.location.mutable:
#        error(f"Can't assign to immutable location")

    def visit(self, assignment: Assignment, env: Env):
        errors = []
        assignment.name.lvalue = True
        errors += self.visit(assignment.name, env)
        errors += self.visit(assignment.expr, env)

        if assignment.name.type != assignment.expr.type:
            errors += [TypeMismatchError('type mismatch in assignment checker', assignment)]
        if not assignment.name.mutable:
            errors += [ConstAssignmentError('attempted to assign to const', assignment)]
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
        if if_.test.type != Type('bool'):
            errors += [PredicateNotBoolError('predicate must be boolean expression', if_)]
        errors += self.visit(if_.consequence, env)
        errors += self.visit(if_.alternative, env)
        return errors

    def visit(self, while_: While, env: Env):
        errors = []
        errors += self.visit(while_.test, env)
        if while_.test.type != Type('bool'):
            errors += [PredicateNotBoolError('predicate must be boolean expression', while_)]
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

#def check_FunctionDefinition(node, env):
#    # Check for nested functions?
#
#    # Put a reference to function into the current scope
#    env[node.name] = node
#​
#    # Make a new scope for the function body.
#    local_env = env.new_child()
#    local_env['$func'] = node    # Reference to current function
#    # Check parameters and function body
#    check(node.parameters, local_env)
#    check(node.statements, local_env)

    def visit(self, func: Func, env: Env):
        errors = []

        env[func.name] = func
        func_env = env.new_child()
        func_env['$func'] = func
        errors += chain(*[self.visit(param, env) for param in func.params])
        errors += self.visit(func.block, env)
        return errors

    def visit(self, import_: Import, env: Env):
        errors = []
        errors += chain(*[self.visit(param, env) for param in import_.params])
        return errors

    def visit(self, call: Call, env: Env):
        errors = []
        errors += chain(*[self.visit(param, env) for param in call.params])
        return errors
