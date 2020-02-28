"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
ADD = 0b10100000
SUB = 0b10100001
MUL = 0b10100010
DIV = 0b10100011
AND = 0b10101000
CMP = 0b10100111
DEC = 0b01100110
INC = 0b01100101
MOD = 0b10100100
NOT = 0b01101001
OR = 0b10101010
SHL = 0b10101100
SHR = 0b10101101
XOR = 0b10101011
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ST = 0b10000100
JMP = 0b01010100
JEQ = 0b01010101
JGE = 0b01011010
JGT = 0b01010111
JLE = 0b01011001
JLT = 0b01011000
JNE = 0b01010110
LD = 0b10000011
NOP = 0b00000000
PRA = 0b01001000
INT = 0b01010010
IRET = 0b00010011
ADDI = 0b10101110


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # memory
        self.ram = [0] * 256
        # registers
        self.reg = [0] * 8
        # reset stack pointer - R7
        self.reg[7] = 0xF4

        # internal registers:
        # program counter
        self.pc = 0
        # flags - 00000LGE
        self.fl = 0

        # branch table
        self.branchtable = {
            HLT: self.HLT,
            LDI: self.LDI,
            PRN: self.PRN,
            ADD: self.alu,
            SUB: self.alu,
            MUL: self.alu,
            DIV: self.alu,
            AND: self.alu,
            CMP: self.alu,
            DEC: self.alu,
            INC: self.alu,
            MOD: self.alu,
            NOT: self.alu,
            OR: self.alu,
            SHL: self.alu,
            SHR: self.alu,
            XOR: self.alu,
            PUSH: self.PUSH,
            POP: self.POP,
            CALL: self.CALL,
            RET: self.RET,
            ST: self.ST,
            JMP: self.JMP,
            JEQ: self.JEQ,
            JGE: self.JGE,
            JGT: self.JGT,
            JLE: self.JLE,
            JLT: self.JLT,
            JNE: self.JNE,
            LD: self.LD,
            NOP: self.NOP,
            PRA: self.PRA,
            INT: self.INT,
            IRET: self.IRET,
            ADDI: self.alu,
        }

    def load(self):
        """Load a program into memory."""

        # check for filename arg
        if len(sys.argv) != 2:
            print("ERROR: must have file name")
            sys.exit(1)

        address = 0

        try:
            with open(sys.argv[1]) as f:
                # read all the lines
                for line in f:
                    # parse out comments
                    comment_split = line.strip().split("#")

                    value = comment_split[0].strip()

                    # ignore blank lines
                    if value == "":
                        continue

                    # cast the numbers from strings to ints
                    num = int(value, 2)

                    self.ram[address] = num
                    address += 1

        except FileNotFoundError:
            print("File not found")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == ADD:
            self.reg[reg_a] += self.reg[reg_b]
        elif op == SUB:
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == DIV:
            if self.reg[reg_b] == 0:
                print("ERROR: cannot divide by zero")
                sys.exit(1)
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == AND:
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]
        elif op == CMP:
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001

            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010

            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
        elif op == DEC:
            self.reg[reg_a] -= 1
        elif op == INC:
            self.reg[reg_a] += 1
        elif op == MOD:
            if self.reg[reg_b] == 0:
                print("ERROR: cannot divide by zero")
                sys.exit(1)
            self.reg[reg_a] %= self.reg[reg_b]
        elif op == NOT:
            self.reg[reg_a] = ~self.reg[reg_a]
        elif op == OR:
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]
        elif op == SHL:
            self.reg[reg_a] = self.reg[reg_a] << self.reg[reg_b]
        elif op == SHR:
            self.reg[reg_a] = self.reg[reg_a] >> self.reg[reg_b]
        elif op == XOR:
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]
        elif op == ADDI:
            val = reg_b
            self.reg[reg_a] += val
        else:
            raise Exception("Unsupported ALU operation")

        # keep value between 0-255
        self.reg[reg_a] = self.reg[reg_a] & 0xFF

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        while True:
            # instruction register
            ir = self.pc
            # read command
            op = self.ram_read(ir)
            # read operands
            operand_a = self.ram_read(ir + 1)
            operand_b = self.ram_read(ir + 2)

            # execute command
            if op in self.branchtable:
                # check if alu operation
                if op & 0b00100000 != 0:
                    self.branchtable[op](op, operand_a, operand_b)
                # check number of operands
                elif op >> 6 == 0:
                    self.branchtable[op]()
                elif op >> 6 == 1:
                    self.branchtable[op](operand_a)
                elif op >> 6 == 2:
                    self.branchtable[op](operand_a, operand_b)
            else:
                print(f"Command not found: {bin(op)}")
                sys.exit(1)

            # check if command sets pc
            # if not, update pc
            if op & 0b00010000 == 0:
                # op: AABCDDDD, where AA == num operands
                self.pc += (op >> 6) + 1

    def ram_read(self, mar):  # mar - Memory Address Register
        """Return value stored at address"""
        mdr = self.ram[mar]  # mdr - Memory Data Register
        return mdr

    def ram_write(self, mar, mdr):
        """Write value to address"""
        self.ram[mar] = mdr

    def HLT(self):
        sys.exit(0)

    def LDI(self, operand_a, operand_b):
        # set value of register to an int
        self.reg[operand_a] = operand_b

    def PRN(self, operand_a):
        # print value stored in given register
        print(self.reg[operand_a])

    def PUSH(self, reg_a):
        # decrement sp
        self.reg[7] -= 1
        # copy value in the given register to the address pointed to by sp
        self.ram[self.reg[7]] = self.reg[reg_a]

    def POP(self, reg_a):
        # copy the value from the address pointed to by sp to the given register
        self.reg[reg_a] = self.ram[self.reg[7]]
        # increment sp
        self.reg[7] += 1

    def CALL(self, reg_a):
        # push return address on to stack
        ret_addr = self.pc + 2
        self.reg[7] -= 1
        self.ram[self.reg[7]] = ret_addr

        # set pc to address stored in given register
        self.pc = self.reg[reg_a]

    def RET(self):
        # pop the value from top of the stack and store it in the pc
        self.pc = self.ram[self.reg[7]]
        self.reg[7] += 1

    def ST(self, reg_a, reg_b):
        # store value in register b in the address stored in register a
        self.ram[self.reg[reg_a]] = self.reg[reg_b]

    def JMP(self, reg_a):
        # set the pc to the address stored in the given register
        self.pc = self.reg[reg_a]

    def JEQ(self, reg_a):
        # if equal flag set to true, jump to address stored in given register
        if self.fl & 0b00000001 != 0:
            self.JMP(reg_a)
        else:
            self.pc += 2

    def JGE(self, reg_a):
        # if greater-than flag or equal flag set to true, jump to address stored in given register
        if self.fl & 0b00000011 != 0:
            self.JMP(reg_a)
        else:
            self.pc += 2

    def JGT(self, reg_a):
        # if greater-than flag set to true, jump to address stored in given register
        if self.fl & 0b00000010 != 0:
            self.JMP(reg_a)
        else:
            self.pc += 2

    def JLE(self, reg_a):
        # if less-than flag or equal flag set to true, jump to address stored in given register
        if self.fl & 0b00000101 != 0:
            self.JMP(reg_a)
        else:
            self.pc += 2

    def JLT(self, reg_a):
        # if less-than flag set to true, jump to address stored in given register
        if self.fl & 0b00000100 != 0:
            self.JMP(reg_a)
        else:
            self.pc += 2

    def JNE(self, reg_a):
        # if equal flag is clear (false, 0), jump to the address stored in the given register.
        if self.fl & 0b00000001 == 0:
            self.JMP(reg_a)
        else:
            self.pc += 2

    def LD(self, reg_a, reg_b):
        # loads register a with the value at the memory address stored in register b
        self.reg[reg_a] = self.ram[self.reg[reg_b]]

    def NOP(self):
        # do nothing
        pass

    def PRA(self, reg_a):
        # print alpha character value stored in the given register
        val = self.reg[reg_a]
        print(chr(val))

    def INT(self):
        pass

    def IRET(self):
        pass
