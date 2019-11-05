#!/usr/bin/env python3

# metal.py
#
# One of the main roles of a compiler is taking high-level programs
# such as what you might write in C or Python and reducing them to
# instructions that can execute on actual hardware.
#
# This file implements a very tiny simulated CPU in the form of a
# Python program.  Although simulated, this CPU mimics the behavior of
# a real CPU.  There are registers for performing simple mathematical
# calculations, memory operations for loading/storing values, and
# control flow instructions for branching and gotos.
#
# See the end of this file for some exercises.
#
# The machine has 8 registers (R0, R1, ..., R7) that hold 32-bit
# integer values.  Register R0 is hardwired to always contains the
# value 0. Register R7 is initialized to the highest valid memory
# address.   A special register PC holds the memory location of the
# next instruction that will execute.
#
# The machine understands the following instructions--which
# are encoded as tuples:
#
#   ('ADD', 'Ra', 'Rb', 'Rd')       ; Rd = Ra + Rb
#   ('SUB', 'Ra', 'Rb', 'Rd')       ; Rd = Ra - Rb
#   ('AND', 'Ra', 'Rb', 'Rd')       ; Rd = Ra & Rb (bitwise-and)
#   ('OR', 'Ra', 'Rb', 'Rd')        ; Rd = Ra | Rb (bitwise-or)
#   ('XOR', 'Ra', 'Rb', 'Rd')       ; Rd = Ra ^ Rb (bitwise-xor)
#   ('SHL', 'Ra', 'Rb', 'Rd')       ; Rd = Ra << Rb (left bit-shift)
#   ('SHR', 'Ra', 'Rb', 'Rd')       ; Rd = Ra >> Rb (right bit-shift)
#   ('CONST', value, 'Rd')          ; Rd = value
#   ('LOAD', 'Rs', 'Rd', offset)    ; Rd = MEMORY[Rs + offset]
#   ('STORE', 'Rs', 'Rd', offset)   ; MEMORY[Rd + offset] = Rs
#   ('JMP', 'Rd', offset)           ; PC = Rd + offset
#   ('BZ', 'Rt', offset)            ; if Rt == 0: PC = PC + offset
#   ('HALT,)                        ; Halts machine
#
# In the the above instructions 'Rx' means some register number such
# as 'R0', 'R1', etc.  All memory instructions take their address from
# register plus an offset that's encoded as part of the instruction.

MASK    = 0xffffffff
PRINT   = 'PRINT'
ADD     = 'ADD'
SUB     = 'SUB'
AND     = 'AND'
OR      = 'OR'
XOR     = 'XOR'
SHL     = 'SHL'
SHR     = 'SHR'
CONST   = 'CONST'
LOAD    = 'LOAD'
STORE   = 'STORE'
JMP     = 'JMP'
BZ      = 'BZ'
HALT    = 'HALT'
R0      = 'R0'
R1      = 'R1'
R2      = 'R2'
R3      = 'R3'
R4      = 'R4'
R5      = 'R5'
R6      = 'R6'
R7      = 'R7'

class Metal:
    def run(self, memory):
        '''
        Run a program. memory is a Python list containing the program
        instructions and other data.  Upon startup, all registers
        are initialized to 0.  R7 is initialized with the highest valid
        memory index (len(memory) - 1).
        '''
        self.pc = 0
        self.registers = { f'R{d}':0 for d in range(8) }
        self.memory = memory
        self.registers['R7'] = len(memory) - 1
        self.running = True
        while self.running:
            op, *args = self.memory[self.pc]
            self.pc += 1
            getattr(self, op)(*args)
            self.registers['R0'] = 0    # R0 is always 0
        return

    def ADD(self, ra, rb, rd):
        self.registers[rd] = (self.registers[ra] + self.registers[rb]) & MASK

    def SUB(self, ra, rb, rd):
        self.registers[rd] = (self.registers[ra] - self.registers[rb]) & MASK

    def AND(self, ra, rb, rd):
        self.registers[rd] = (self.registers[ra] & self.registers[rb]) & MASK

    def OR(self, ra, rb, rd):
        self.registers[rd] = (self.registers[ra] | self.registers[rb]) & MASK

    def XOR(self, ra, rb, rd):
        self.registers[rd] = (self.registers[ra] ^ self.registers[rb]) & MASK

    def SHL(self, ra, rb, rd):
        self.registers[rd] = (self.registers[ra] << self.registers[rb]) & MASK

    def SHR(self, ra, rb, rd):
        self.registers[rd] = (self.registers[ra] >> self.registers[rb]) & MASK

    def CONST(self, value, rd):
        self.registers[rd] = value & MASK

    def LOAD(self, rs, rd, offset):
        self.registers[rd] = (self.memory[self.registers[rs]+offset]) & MASK

    def STORE(self, rs, rd, offset):
        self.memory[self.registers[rd]+offset] = self.registers[rs]

    def JMP(self, rd, offset):
        self.pc = self.registers[rd] + offset

    def BZ(self, rt, offset):
        if not self.registers[rt]:
            self.pc += offset

    def PRINT(self, rx):
        print(f'{rx} = {self.registers[rx]}')

    def HALT(self):
        self.running = False

if __name__ == '__main__':
    machine = Metal()

    # ----------------------------------------------------------------------
    # Problem 1:  Computers
    #
    # The CPU of a computer executes low-level instructions.  Using the
    # Metal instruction set above, show how you would compute 2 + 3 - 4.

    prog1 = [ # Instructions here
              ('CONST', 2, 'R1'),
              ('CONST', 3, 'R2'),
              # More instructions here
              # ...
              # Save the result. Replace 'R0' with whatever register holds the result.
              ('STORE', 'R0', 'R7', 0),
              ('HALT',),
              0            # Store the result here (note: R7 points here)
              ]

    prog1 = [
        (CONST, 2, R1),
        (CONST, 3, R2),
        (ADD, R1, R2, R3),
        (CONST, 4, R4),
        (SUB, R3, R4, R5),
        (STORE, R5, R7, 0),
        (HALT, ),
        0,
    ]

    machine.run(prog1)
    print('Program 1 Result:', prog1[-1], '(Should be 1)')

    # ----------------------------------------------------------------------
    # Problem 2: Computation
    #
    # Write a Metal program that computes 3 * 7.
    #
    # Note: The machine doesn't implement multiplication. So, you need
    # to figure out how to do it.

    prog2 = [ # Instructions here
              ('CONST', 3, 'R1'),
              ('CONST', 7, 'R2'),
              # ...
              ('HALT',),
              0           # Store result here
            ]

    prog2 = [
        (CONST, 3, R1),
        (CONST, 7, R2),
        (CONST, 0, R3),
        (CONST, 1, R4),
        (ADD, R2, R3, R3),
        (SUB, R1, R4, R1),
        (BZ, R1, 1),
        (JMP, R0, 4),
        (STORE, R3, R7, 0),
        (HALT,),
        0,
    ]

    machine.run(prog2)
    print('Program 2 Result:', prog2[-1], '(Should be 21)')

    # ----------------------------------------------------------------------
    # Problem 3: Abstraction
    #
    # Write a Python function mul(x, y) that computes x * y on Metal.
    # This function, should abstract details away--you're not supposed to
    # worry about how it works.  Just call mul(x, y).  Naturally, you
    # are NOT allowed to use the Python * operator.  Only use the provided
    # Metal instructions.

    def mul(x, y):
        prog = [ # Instructions here
                 # ...

                 ('HALT',),
                 0       # Result
        ]

        prog = [
            (CONST, x, R1),
            (CONST, y, R2),
            (CONST, 0, R3),
            (CONST, 1, R4),
            (ADD, R2, R3, R3),
            (SUB, R1, R4, R1),
            (BZ, R1, 1),
            (JMP, R0, 4),
            (STORE, R3, R7, 0),
            (HALT,),
            0,
        ]
        machine.run(prog)
        return prog[-1]

    print(f'Problem 3: 3 * 9 = {mul(3, 9)}. (Should be 27)')

    # ----------------------------------------------------------------------
    # Optional challenge:
    #
    # What is the fastest algorithm for computing mul(x, y)?
    # Katsuba Algorithm

