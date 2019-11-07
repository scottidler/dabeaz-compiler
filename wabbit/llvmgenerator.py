# llvmgen.py
#
# This file will generate LLVM output for your compiler.
# See Docs/codegen.html for a tutorial on how to generate
# LLVM code.

# Create LLVM from IRModule (from the intermediate code stage)
# Convert stack machine to LLVM.

from llvmlite.ir import (
    Module, Function, FunctionType, IntType, DoubleType, VoidType,
    Constant, IRBuilder, GlobalVariable
    )

from leatherman.dbg import dbg

# Create LLVM versions of the low-level datatypes used in IR code
int_type = IntType(32)
float_type = DoubleType()
void_type = VoidType()

#def generate_llvm(irmodule):
#    gen = LLVMGenerator()
#    for irfunc in irmodule.functions:
#        gen.generate_function(irfunc)
#    return gen.module

class IfBlock:
    def __init__(self, func):
        self.consequence = func.append_basic_block()
        self.alternative = func.append_basic_block()
        self.merge = func.append_basic_block()

class WhileBlock:
    def __init__(self, func):
        self.loop_test = func.append_basic_block()
        self.loop_exit = func.append_basic_block()

class LLVMGenerator:

    def __init__(self):
        self.stack = []
        self.blockstack = []
        self.module = Module()      # The LLVM module
        self.globals = {}

        # Declare external functions needed for runtime functionality such as printing.
        # This code must be implemented in C and linked with the final LLVM output.
        self._print_int = Function(
            self.module,
            FunctionType(void_type, [int_type]),
            name="_print_int")

        self._print_float = Function(
            self.module,
            FunctionType(void_type, [float_type]),
            name="_print_float")

    @classmethod
    def generate(cls, irmodule):
        generator = cls()
        for name, g_irtype in irmodule.globals.items():
            generator.define_global(name, g_irtype)
        for irfunc in irmodule.functions:
            generator.generate_function(irfunc)
        return generator.module

#    def __init__(self):
#        self.stack = []
#        self.module = Module()      # The LLVM module
#
#        # Declare external functions needed for runtime functionality such as printing.
#        # This code must be implemented in C and linked with the final LLVM output.
#        self._print_int = Function(self.module,
#                                    FunctionType(void_type, [int_type]),
#                                    name="_print_int")


    def define_global(self, name, g_irtype):
        assert g_irtype in ('I', 'F'), 'define_global requires I or F'
        if g_irtype == 'I':
            g_llvmtype = int_type
            initializer = Constant(int_type, 0)
        elif g_irtype == 'F':
            g_llvmtype = float_type
            initializer = Constant(float_type, 0.0)

        self.globals[name] = GlobalVariable(self.module, g_llvmtype, name)
        self.globals[name].initializer = initializer


    def generate_function(self, irfunc):
        # Make LLVM code for an IRFunction
        # From exercise (follow the template). Fill in details.
        # Note: Need to fix function signatures later (for model5 and upwards)
        self.func = Function(self.module, FunctionType(int_type, []), name=irfunc.name)
        block = self.func.append_basic_block('entry')
        self.builder = IRBuilder(block)
        for op, *opargs in irfunc.code:
            getattr(self, f'gen_{op}')(*opargs)

        # Function assumes an "int" return. Fake it.
        self.builder.ret(Constant(int_type, 0))

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        return self.stack.pop()

    def pop_left_right(self):
        right = self.pop()
        left = self.pop()
        return left, right

    def gen_CONSTI(self, value):
        self.push(Constant(int_type, value))

    def gen_ADDI(self):
        self.push(self.builder.add(*self.pop_left_right()))

    def gen_SUBI(self):
        self.push(self.builder.sub(*self.pop_left_right()))

    def gen_MULI(self):
        self.push(self.builder.mul(*self.pop_left_right()))

    def gen_DIVI(self):
        self.push(self.builder.sdiv(*self.pop_left_right()))

    def gen_GTI(self):
        result = self.builder.icmp_signed('>', *self.pop_left_right())
        self.push(self.builder.zext(result, int_type))

    def gen_LTI(self):
        result = self.builder.icmp_signed('<', *self.pop_left_right())
        self.push(self.builder.zext(result, int_type))

    def gen_GEI(self):
        result = self.builder.icmp_signed('>=', *self.pop_left_right())
        self.push(self.builder.zext(result, int_type))

    def gen_LEI(self):
        result = self.builder.icmp_signed('<=', *self.pop_left_right())
        self.push(self.builder.zext(result, int_type))

    def gen_EQI(self):
        result = self.builder.icmp_signed('==', *self.pop_left_right())
        self.push(self.builder.zext(result, int_type))

    def gen_NEI(self):
        result = self.builder.icmp_signed('!=', *self.pop_left_right())
        self.push(self.builder.zext(result, int_type))

    def gen_PRINTI(self):
        # See codegen.html pg. 12-13
        self.builder.call(self._print_int, [self.pop()])

    def gen_CONSTF(self, value):
        self.push(Constant(float_type, value))

    def gen_ADDF(self):
        self.push(self.builder.fadd(*self.pop_left_right()))

    def gen_SUBF(self):
        self.push(self.builder.fsub(*self.pop_left_right()))

    def gen_MULF(self):
        self.push(self.builder.fmul(*self.pop_left_right()))

    def gen_DIVF(self):
        self.push(self.builder.fdiv(*self.pop_left_right()))

    def gen_GTF(self):
        result = self.buildler.fcmp_ordered('>', *self.pop_left_right())
        self.push(self.builder.zext(result, float_type))

    def gen_LTF(self):
        result = self.buildler.fcmp_ordered('<', *self.pop_left_right())
        self.push(self.builder.zext(result, float_type))

    def gen_GEF(self):
        result = self.buildler.fcmp_ordered('>=', *self.pop_left_right())
        self.push(self.builder.zext(result, float_type))

    def gen_LEF(self):
        result = self.buildler.fcmp_ordered('<=', *self.pop_left_right())
        self.push(self.builder.zext(result, float_type))

    def gen_EQF(self):
        result = self.buildler.fcmp_ordered('==', *self.pop_left_right())
        self.push(self.builder.zext(result, float_type))

    def gen_NEF(self):
        result = self.buildler.fcmp_ordered('!=', *self.pop_left_right())
        self.push(self.builder.zext(result, float_type))

    def gen_PRINTF(self):
        self.builder.call(self._print_float, [self.pop()])

    def gen_GLOBAL_GET(self, name):
        self.push(self.builder.load(self.globals[name]))

    def gen_GLOBAL_SET(self, name):
        self.builder.store(self.pop(), self.globals[name])

    def gen_IF(self):
        block = IfBlock(self.func)
        self.builder.cbranch(self.builder.trunc(self.pop(), IntType(1)),
            block.consequence,
            block.alternative)
        self.blockstack.append(block)
        self.builder.position_at_end(block.consequence)

    def gen_ELSE(self):
        block = self.blockstack[-1]
        self.builder.branch(block.merge)
        self.builder.position_at_end(block.alternative)

    def gen_ENDIF(self):
        block = self.blockstack.pop()
        self.builder.branch(block.merge)
        self.builder.position_at_end(block.merge)
