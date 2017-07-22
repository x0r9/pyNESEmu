"""
A basic 6502 Emulator...
"""
import struct

class Register(object):
    """
    Will act like a very simple x bit register
    """
    _v = 0
    _length = 0
    _mask = 0
    _setCall = None
    
    def __init__(self, length=8):
        self._length = length
        self._mask = (2**length)-1
    @property
    def V(self):
        return self._v
    @V.setter
    def V(self, value):
        self._v = value&self._mask
        if self._setCall != None:
            self._setCall(self)
            
    def setCallOnSet(self, func):
        self._setCall = func
class Flag(object):
    """
    this is a flag for the 6502's Status bits
    e.g. Carry, Zero, Int, DecMode, Break, Overflow, Neg
    """
    _v = False
    def __init__(self):
        pass
    def Set(self):
        self._v = True
    def Clear(self):
        self._v = False
        
    @property    
    def V(self):
        return self._v
        
    @V.setter
    def V(self, value):
        self._v = value

###
# Enumerations-
#      Opcodes+MemoryTypes etc...
###

STAT_CARRY      = 0x01
STAT_ZERO       = 0x02
STAT_INT        = 0x04
STAT_DEC        = 0x08
STAT_BRK        = 0x10
STAT_OVERFLOW   = 0x40
STAT_SIGN       = 0x80

MEM_IMPLICIT = -1
MEM_ACCUMULATOR = 0
MEM_IMMEDIATE = 1
MEM_ZEROPAGE = 2
MEM_ZEROPAGE_X = 3
MEM_ZEROPAGE_Y = 4
MEM_RELATIVE = 5
MEM_ABSOLUTE = 6
MEM_ABSOLUTE_X = 7
MEM_ABSOLUTE_Y = 8
MEM_INDIRECT = 9
MEM_INDIRECT_X = 10 #These don't behave as well as you'd hope!
MEM_INDIRECT_Y = 11
    
    
MemBytes = {}
MemBytes[MEM_IMPLICIT]      = 0
MemBytes[MEM_ACCUMULATOR]   = 0
MemBytes[MEM_IMMEDIATE]     = 1
MemBytes[MEM_ZEROPAGE]      = 1
MemBytes[MEM_ZEROPAGE_X]    = 1
MemBytes[MEM_ZEROPAGE_Y]    = 1
MemBytes[MEM_RELATIVE]      = 1
MemBytes[MEM_ABSOLUTE]      = 2
MemBytes[MEM_ABSOLUTE_X]    = 2
MemBytes[MEM_ABSOLUTE_Y]    = 2
MemBytes[MEM_INDIRECT]      = 2
MemBytes[MEM_INDIRECT_X]    = 1   
MemBytes[MEM_INDIRECT_Y]    = 1

MemTypeToString={
    MEM_IMPLICIT        :"IMPLICIT",
    MEM_ACCUMULATOR     :"ACCUMULATOR",
    MEM_IMMEDIATE       :"IMMEDIATE",
    MEM_ZEROPAGE        :"ZEROPAGE",
    MEM_ZEROPAGE_X      :"ZEROPAGE-X",
    MEM_ZEROPAGE_Y      :"ZEROPAGE-Y",
    MEM_RELATIVE        :"RELATIVE",
    MEM_ABSOLUTE        :"ABSOLUTE",
    MEM_ABSOLUTE_X      :"ABSOLUTE-X",
    MEM_ABSOLUTE_Y      :"ABSOLUTE-Y",
    MEM_INDIRECT        :"INDIRECT",
    MEM_INDIRECT_X      :"INDIRECT-X",
    MEM_INDIRECT_Y      :"INDIRECT-Y",
}

#Opcodes
OP_LDA = 1 # Load
OP_LDX = 2
OP_LDY = 3

OP_STA = 4 # Store
OP_STX = 5
OP_STY = 6

OP_TAX = 7 # Transfer
OP_TAY = 8
OP_TXA = 9
OP_TYA = 10

OP_TSX = 11 # Stack
OP_TXS = 12
OP_PHA = 13 
OP_PHP = 14
OP_PLA = 15
OP_PLP = 16

OP_AND = 17 # Logic
OP_EOR = 18
OP_ORA = 19
OP_BIT = 20

OP_ADC = 21 # Arthimetic
OP_SBC = 22
OP_CMP = 23
OP_CPX = 24
OP_CPY = 25

OP_INC = 26 # Increments & Decrements
OP_INX = 27
OP_INY = 28
OP_DEC = 29
OP_DEX = 30
OP_DEY = 31

OP_ASL = 32 # Shifts
OP_LSR = 33
OP_ROL = 34
OP_ROR = 35

OP_JMP = 36 # Jumps
OP_JSR = 37
OP_RTS = 38

OP_BCC = 39 # Branches
OP_BCS = 40
OP_BEQ = 41
OP_BMI = 42
OP_BNE = 43
OP_BPL = 44
OP_BVC = 45
OP_BVS = 46

OP_CLC = 47 # Status Flag
OP_CLD = 48
OP_CLI = 49
OP_CLV = 50
OP_SEC = 51
OP_SED = 52
OP_SEI = 53

OP_BRK = 54 # System Functions
OP_NOP = 55
OP_RTI = 56
OP_UNKOWN = -1

#OpCode to String
OpToString = {
    OP_LDA:"LDA",
    OP_LDX:"LDX",
    OP_LDY:"LDY",
    OP_STA:"STA",
    OP_STX:"STX",
    OP_STY:"STY",
    OP_TAX:"TAX",
    OP_TAY:"TAY",
    OP_TXA:"TXA",
    OP_TYA:"TYA",
    OP_TSX:"TSX",
    OP_TXS:"TXS",
    OP_PHA:"PHA",
    OP_PHP:"PHP",
    OP_PLA:"PLA",
    OP_PLP:"PLP",
    OP_AND:"AND",
    OP_EOR:"EOR",
    OP_ORA:"ORA",
    OP_BIT:"BIT",
    OP_ADC:"ADC",
    OP_SBC:"SBC",
    OP_CMP:"CMP",
    OP_CPX:"CPX",
    OP_CPY:"CPY",
    OP_INC:"INC",
    OP_INX:"INX",
    OP_INY:"INY",
    OP_DEC:"DEC",
    OP_DEX:"DEX",
    OP_DEY:"DEY",
    OP_ASL:"ASL",
    OP_LSR:"LSR",
    OP_ROL:"ROL",
    OP_ROR:"ROR",
    OP_JMP:"JMP",
    OP_JSR:"JSR",
    OP_RTS:"RTS",
    OP_BCC:"BCC",
    OP_BCS:"BCS",
    OP_BEQ:"BEQ",
    OP_BMI:"BMI",
    OP_BNE:"BNE",
    OP_BPL:"BPL",
    OP_BVC:"BVC",
    OP_BVS:"BVS",
    OP_CLC:"CLC",
    OP_CLD:"CLD",
    OP_CLI:"CLI",
    OP_CLV:"CLV",
    OP_SEC:"SEC",
    OP_SED:"SED",
    OP_SEI:"SEI",
    OP_BRK:"BRK",
    OP_NOP:"NOP",
    OP_RTI:"RTI",
    OP_UNKOWN:"XYZ",
}

#OpCode to String
OpToLongString = {
    OP_LDA:"Load A",
    OP_LDX:"Load X",
    OP_LDY:"Load Y",
    OP_STA:"Store A",
    OP_STX:"Store X",
    OP_STY:"Store Y",
    OP_TAX:"Transfer A to X",
    OP_TAY:"Transfer A to Y",
    OP_TXA:"Transfer X to A",
    OP_TYA:"Transfer Y to A",
    OP_TSX:"Transfer StackPtr to X",
    OP_TXS:"Transfer X to StackPtr",
    OP_PHA:"Push A to Stack",
    OP_PHP:"Push Processor Status(Flags) to Stack",
    OP_PLA:"Pull into A",
    OP_PLP:"Pull Processor Status(Flags)",
    OP_AND:"Bitwise AND& with A",
    OP_EOR:"Bitwise XOR^ with A",
    OP_ORA:"Bitwise OR | with A",
    OP_BIT:"Test Bits!?",
    OP_ADC:"Add with carry",
    OP_SBC:"Subtract with carry",
    OP_CMP:"Compare A",
    OP_CPX:"Compare X",
    OP_CPY:"Compare Y",
    OP_INC:"Increment memory",
    OP_INX:"Increment X",
    OP_INY:"Increment Y",
    OP_DEC:"Decrement Memory",
    OP_DEX:"Decrement X",
    OP_DEY:"Decrement Y",
    OP_ASL:"Arithmatic Shift Left",
    OP_LSR:"Logical Shift Right",
    OP_ROL:"Rotate Left",
    OP_ROR:"Rotate Rate",
    OP_JMP:"Jump",
    OP_JSR:"Jump To Subroutine",
    OP_RTS:"Return From Subroutine",
    OP_BCC:"Branch On Carry Clear",
    OP_BCS:"Branch On Carry Set",
    OP_BEQ:"Branch On Equal",
    OP_BMI:"Branch On Minus",
    OP_BNE:"Branch On Not Equal",
    OP_BPL:"Branch On Plus",
    OP_BVC:"Branch On Overflow Clear",
    OP_BVS:"Branch On Overflow Set",
    OP_CLC:"Clear Carry",
    OP_CLD:"Clear Decimal",
    OP_CLI:"Clear Interupt",
    OP_CLV:"Clear Overflow",
    OP_SEC:"Set Carry",
    OP_SED:"Set Decimal",
    OP_SEI:"Set Interupt",
    OP_BRK:"Break",
    OP_NOP:"No Operation",
    OP_RTI:"Retrun From Interupt",
    OP_UNKOWN:"Unrecognised opcode",
}


# Opcode Dictionary
# (Op-type, memory-type, byte-length, clocks, extra clk on page change)

OpCodes = {}
OpCodes["\x69"] = (OP_ADC,  MEM_IMMEDIATE,      2,  2,  False)
OpCodes["\x65"] = (OP_ADC,  MEM_ZEROPAGE,       2,  3,  False)
OpCodes["\x75"] = (OP_ADC,  MEM_ZEROPAGE_X,     2,  4,  False)
OpCodes["\x6D"] = (OP_ADC,  MEM_ABSOLUTE,       3,  4,  False)
OpCodes["\x7D"] = (OP_ADC,  MEM_ABSOLUTE_X,     3,  4,  True )
OpCodes["\x79"] = (OP_ADC,  MEM_ABSOLUTE_Y,     3,  4,  True )
OpCodes["\x61"] = (OP_ADC,  MEM_INDIRECT_X,     2,  6,  False)
OpCodes["\x71"] = (OP_ADC,  MEM_INDIRECT_Y,     2,  5,  True )

OpCodes["\x29"] = (OP_AND,  MEM_IMMEDIATE,      2,  2,  False)
OpCodes["\x25"] = (OP_AND,  MEM_ZEROPAGE,       2,  3,  False)
OpCodes["\x35"] = (OP_AND,  MEM_ZEROPAGE_X,     2,  4,  False)
OpCodes["\x2D"] = (OP_AND,  MEM_ABSOLUTE,       3,  4,  False)
OpCodes["\x3D"] = (OP_AND,  MEM_ABSOLUTE_X,     3,  4,  True )
OpCodes["\x39"] = (OP_AND,  MEM_ABSOLUTE_Y,     3,  4,  True )
OpCodes["\x21"] = (OP_AND,  MEM_INDIRECT_X,     2,  6,  False)
OpCodes["\x31"] = (OP_AND,  MEM_INDIRECT_Y,     2,  5,  True )

OpCodes["\x0A"] = (OP_ASL,  MEM_ACCUMULATOR,    1,  2,  False)
OpCodes["\x06"] = (OP_ASL,  MEM_ZEROPAGE,       2,  5,  False)
OpCodes["\x16"] = (OP_ASL,  MEM_ZEROPAGE_X,     2,  6,  False)
OpCodes["\x0E"] = (OP_ASL,  MEM_ABSOLUTE,       3,  6,  False)
OpCodes["\x1E"] = (OP_ASL,  MEM_ABSOLUTE_X,     3,  7,  False)

OpCodes["\x90"] = (OP_BCC,  MEM_RELATIVE,       2,  2,  False) # +1 cycle if succeeds, +2 if suceeds into new page
OpCodes["\xB0"] = (OP_BCS,  MEM_RELATIVE,       2,  2,  False) # +1 cycle if succeeds, +2 if suceeds into new page
OpCodes["\xF0"] = (OP_BEQ,  MEM_RELATIVE,       2,  2,  False) # +1 cycle if succeeds, +2 if suceeds into new page
OpCodes["\x30"] = (OP_BMI,  MEM_RELATIVE,       2,  2,  False) # +1 cycle if succeeds, +2 if suceeds into new page
OpCodes["\xD0"] = (OP_BNE,  MEM_RELATIVE,       2,  2,  False) # +1 cycle if succeeds, +2 if suceeds into new page
OpCodes["\x10"] = (OP_BPL,  MEM_RELATIVE,       2,  2,  False) # +1 cycle if succeeds, +2 if suceeds into new page
OpCodes["\x50"] = (OP_BVC,  MEM_RELATIVE,       2,  2,  False) # +1 cycle if succeeds, +2 if suceeds into new page
OpCodes["\x70"] = (OP_BVS,  MEM_RELATIVE,       2,  2,  False) # +1 cycle if succeeds, +2 if suceeds into new page

OpCodes["\x24"] = (OP_BIT,  MEM_ZEROPAGE,       2,  3,  False)
OpCodes["\x2C"] = (OP_BIT,  MEM_ABSOLUTE,       3,  4,  False)

OpCodes["\x00"] = (OP_BRK,  MEM_IMPLICIT,       1,  7,  False)

OpCodes["\x18"] = (OP_CLC,  MEM_IMPLICIT,       1,  2,  False)
OpCodes["\xD8"] = (OP_CLD,  MEM_IMPLICIT,       1,  2,  False)
OpCodes["\x58"] = (OP_CLI,  MEM_IMPLICIT,       1,  2,  False)
OpCodes["\xB8"] = (OP_CLV,  MEM_IMPLICIT,       1,  2,  False)

OpCodes["\xC9"] = (OP_CMP,  MEM_IMMEDIATE,      2,  2,  False)
OpCodes["\xC5"] = (OP_CMP,  MEM_ZEROPAGE,       2,  3,  False)
OpCodes["\xD5"] = (OP_CMP,  MEM_ZEROPAGE_X,     2,  4,  False)
OpCodes["\xCD"] = (OP_CMP,  MEM_ABSOLUTE,       3,  4,  False)
OpCodes["\xDD"] = (OP_CMP,  MEM_ABSOLUTE_X,     3,  4,  True )
OpCodes["\xD9"] = (OP_CMP,  MEM_ABSOLUTE_Y,     3,  4,  True )
OpCodes["\xC1"] = (OP_CMP,  MEM_INDIRECT_X,     2,  6,  False)
OpCodes["\xD1"] = (OP_CMP,  MEM_INDIRECT_Y,     2,  5,  True )

OpCodes["\xE0"] = (OP_CPX,  MEM_IMMEDIATE,      2,  2,  False)
OpCodes["\xE4"] = (OP_CPX,  MEM_ZEROPAGE,       2,  3,  False)
OpCodes["\xEC"] = (OP_CPX,  MEM_ABSOLUTE,       3,  4,  False)

OpCodes["\xC0"] = (OP_CPY,  MEM_IMMEDIATE,      2,  2,  False)
OpCodes["\xC4"] = (OP_CPY,  MEM_ZEROPAGE,       2,  3,  False)
OpCodes["\xCC"] = (OP_CPY,  MEM_ABSOLUTE,       3,  4,  False)

OpCodes["\xC6"] = (OP_DEC,  MEM_ZEROPAGE,       2,  5,  False)
OpCodes["\xD6"] = (OP_DEC,  MEM_ZEROPAGE_X,     2,  6,  False)
OpCodes["\xCE"] = (OP_DEC,  MEM_ABSOLUTE,       3,  6,  False)
OpCodes["\xDE"] = (OP_DEC,  MEM_ABSOLUTE_X,     3,  7,  False)

OpCodes["\xCA"] = (OP_DEX,  MEM_IMPLICIT,       1,  2,  False)

OpCodes["\x88"] = (OP_DEY,  MEM_IMPLICIT,       1,  2,  False)

OpCodes["\x49"] = (OP_EOR,  MEM_IMMEDIATE,      2,  2,  False)
OpCodes["\x45"] = (OP_EOR,  MEM_ZEROPAGE,       2,  3,  False)
OpCodes["\x55"] = (OP_EOR,  MEM_ZEROPAGE_X,     2,  4,  False)
OpCodes["\x4D"] = (OP_EOR,  MEM_ABSOLUTE,       3,  4,  False)
OpCodes["\x5D"] = (OP_EOR,  MEM_ABSOLUTE_X,     3,  4,  True )
OpCodes["\x59"] = (OP_EOR,  MEM_ABSOLUTE_Y,     3,  4,  True )
OpCodes["\x41"] = (OP_EOR,  MEM_INDIRECT_X,     2,  6,  False)
OpCodes["\x51"] = (OP_EOR,  MEM_INDIRECT_Y,     2,  5,  True )

OpCodes["\xE6"] = (OP_INC,  MEM_ZEROPAGE,       2,  5,  False)
OpCodes["\xF6"] = (OP_INC,  MEM_ZEROPAGE_X,     2,  6,  False)
OpCodes["\xEE"] = (OP_INC,  MEM_ABSOLUTE,       3,  6,  False)
OpCodes["\xFE"] = (OP_INC,  MEM_ABSOLUTE_X,     3,  7,  False)

OpCodes["\xE8"] = (OP_INX,  MEM_IMPLICIT,       1,  2,  False)

OpCodes["\xC8"] = (OP_INY,  MEM_IMPLICIT,       1,  2,  False)

OpCodes["\x4C"] = (OP_JMP,  MEM_ABSOLUTE,       3,  3,  False)
OpCodes["\x6C"] = (OP_JMP,  MEM_INDIRECT,       3,  5,  False)

OpCodes["\x20"] = (OP_JSR,  MEM_ABSOLUTE,       3,  6,  False)

OpCodes["\xA9"] = (OP_LDA,  MEM_IMMEDIATE,      2,  2,  False)
OpCodes["\xA5"] = (OP_LDA,  MEM_ZEROPAGE,       2,  3,  False)
OpCodes["\xB5"] = (OP_LDA,  MEM_ZEROPAGE_X,     2,  4,  False)
OpCodes["\xAD"] = (OP_LDA,  MEM_ABSOLUTE,       3,  4,  False)
OpCodes["\xBD"] = (OP_LDA,  MEM_ABSOLUTE_X,     3,  4,  True )
OpCodes["\xB9"] = (OP_LDA,  MEM_ABSOLUTE_Y,     3,  4,  True )
OpCodes["\xA1"] = (OP_LDA,  MEM_INDIRECT_X,     2,  6,  False)
OpCodes["\xB1"] = (OP_LDA,  MEM_INDIRECT_Y,     2,  5,  True )

OpCodes["\xA2"] = (OP_LDX,  MEM_IMMEDIATE,      2,  2,  False)
OpCodes["\xA6"] = (OP_LDX,  MEM_ZEROPAGE,       2,  3,  False)
OpCodes["\xB6"] = (OP_LDX,  MEM_ZEROPAGE_Y,     2,  4,  False)
OpCodes["\xAE"] = (OP_LDX,  MEM_ABSOLUTE,       3,  4,  False)
OpCodes["\xBE"] = (OP_LDX,  MEM_ABSOLUTE_Y,     3,  4,  True )

OpCodes["\xA0"] = (OP_LDY,  MEM_IMMEDIATE,      2,  2,  False)
OpCodes["\xA4"] = (OP_LDY,  MEM_ZEROPAGE,       2,  3,  False)
OpCodes["\xB4"] = (OP_LDY,  MEM_ZEROPAGE_X,     2,  4,  False)
OpCodes["\xAC"] = (OP_LDY,  MEM_ABSOLUTE,       3,  4,  False)
OpCodes["\xBC"] = (OP_LDY,  MEM_ABSOLUTE_X,     3,  4,  True )

OpCodes["\x4A"] = (OP_LSR,  MEM_ACCUMULATOR,    1,  2,  False)
OpCodes["\x46"] = (OP_LSR,  MEM_ZEROPAGE,       2,  5,  False)
OpCodes["\x56"] = (OP_LSR,  MEM_ZEROPAGE_X,     2,  6,  False)
OpCodes["\x4E"] = (OP_LSR,  MEM_ABSOLUTE,       3,  6,  False)
OpCodes["\x5E"] = (OP_LSR,  MEM_ABSOLUTE_X,     3,  7,  False)

OpCodes["\xEA"] = (OP_NOP,  MEM_IMPLICIT,       1,  2,  False)
#OpCodes["\x44"] = (OP_NOP,  MEM_IMPLICIT,       1,  2,  False)

OpCodes["\x09"] = (OP_ORA,  MEM_IMMEDIATE,      2,  2,  False)
OpCodes["\x05"] = (OP_ORA,  MEM_ZEROPAGE,       2,  3,  False)
OpCodes["\x15"] = (OP_ORA,  MEM_ZEROPAGE_X,     2,  4,  False)
OpCodes["\x0D"] = (OP_ORA,  MEM_ABSOLUTE,       3,  4,  False)
OpCodes["\x1D"] = (OP_ORA,  MEM_ABSOLUTE_X,     3,  4,  True )
OpCodes["\x19"] = (OP_ORA,  MEM_ABSOLUTE_Y,     3,  4,  True )
OpCodes["\x01"] = (OP_ORA,  MEM_INDIRECT_X,     2,  6,  False)
OpCodes["\x11"] = (OP_ORA,  MEM_INDIRECT_Y,     2,  5,  True )

OpCodes["\x48"] = (OP_PHA,  MEM_IMPLICIT,       1,  3,  False)
OpCodes["\x08"] = (OP_PHP,  MEM_IMPLICIT,       1,  3,  False)
OpCodes["\x68"] = (OP_PLA,  MEM_IMPLICIT,       1,  4,  False)
OpCodes["\x28"] = (OP_PLP,  MEM_IMPLICIT,       1,  4,  False)

OpCodes["\x2A"] = (OP_ROL,  MEM_ACCUMULATOR,    1,  2,  False)
OpCodes["\x26"] = (OP_ROL,  MEM_ZEROPAGE,       2,  5,  False)
OpCodes["\x36"] = (OP_ROL,  MEM_ZEROPAGE_X,     2,  6,  False)
OpCodes["\x2E"] = (OP_ROL,  MEM_ABSOLUTE,       3,  6,  False)
OpCodes["\x3E"] = (OP_ROL,  MEM_ABSOLUTE_X,     3,  7,  False)

OpCodes["\x2A"] = (OP_ROL,  MEM_ACCUMULATOR,    1,  2,  False)
OpCodes["\x26"] = (OP_ROL,  MEM_ZEROPAGE,       2,  5,  False)
OpCodes["\x36"] = (OP_ROL,  MEM_ZEROPAGE_X,     2,  6,  False)
OpCodes["\x2E"] = (OP_ROL,  MEM_ABSOLUTE,       3,  6,  False)
OpCodes["\x3E"] = (OP_ROL,  MEM_ABSOLUTE_X,     3,  7,  False)

OpCodes["\x6A"] = (OP_ROR,  MEM_ACCUMULATOR,    1,  2,  False)
OpCodes["\x66"] = (OP_ROR,  MEM_ZEROPAGE,       2,  5,  False)
OpCodes["\x76"] = (OP_ROR,  MEM_ZEROPAGE_X,     2,  6,  False)
OpCodes["\x6E"] = (OP_ROR,  MEM_ABSOLUTE,       3,  6,  False)
OpCodes["\x7E"] = (OP_ROR,  MEM_ABSOLUTE_X,     3,  7,  False)

OpCodes["\x40"] = (OP_RTI,  MEM_IMPLICIT,       1,  6,  False)
OpCodes["\x60"] = (OP_RTS,  MEM_IMPLICIT,       1,  6,  False)

OpCodes["\xE9"] = (OP_SBC,  MEM_IMMEDIATE,      2,  2,  False)
OpCodes["\xE5"] = (OP_SBC,  MEM_ZEROPAGE,       2,  3,  False)
OpCodes["\xF5"] = (OP_SBC,  MEM_ZEROPAGE_X,     2,  4,  False)
OpCodes["\xED"] = (OP_SBC,  MEM_ABSOLUTE,       3,  4,  False)
OpCodes["\xFD"] = (OP_SBC,  MEM_ABSOLUTE_X,     3,  4,  True )
OpCodes["\xF9"] = (OP_SBC,  MEM_ABSOLUTE_Y,     3,  4,  True )
OpCodes["\xE1"] = (OP_SBC,  MEM_INDIRECT_X,     2,  6,  False)
OpCodes["\xF1"] = (OP_SBC,  MEM_INDIRECT_Y,     2,  5,  True )

OpCodes["\x38"] = (OP_SEC,  MEM_IMPLICIT,       1,  2,  False)
OpCodes["\xF8"] = (OP_SED,  MEM_IMPLICIT,       1,  2,  False)
OpCodes["\x78"] = (OP_SEI,  MEM_IMPLICIT,       1,  2,  False)

OpCodes["\x85"] = (OP_STA,  MEM_ZEROPAGE,       2,  3,  False)
OpCodes["\x95"] = (OP_STA,  MEM_ZEROPAGE_X,     2,  4,  False)
OpCodes["\x8D"] = (OP_STA,  MEM_ABSOLUTE,       3,  4,  False)
OpCodes["\x9D"] = (OP_STA,  MEM_ABSOLUTE_X,     3,  5,  False)
OpCodes["\x99"] = (OP_STA,  MEM_ABSOLUTE_Y,     3,  5,  False)
OpCodes["\x81"] = (OP_STA,  MEM_INDIRECT_X,     2,  6,  False)
OpCodes["\x91"] = (OP_STA,  MEM_INDIRECT_Y,     2,  6,  False)

OpCodes["\x86"] = (OP_STX,  MEM_ZEROPAGE,       2,  3,  False)
OpCodes["\x96"] = (OP_STX,  MEM_ZEROPAGE_Y,     2,  4,  False)
OpCodes["\x8E"] = (OP_STX,  MEM_ABSOLUTE,       3,  4,  False)

OpCodes["\x84"] = (OP_STY,  MEM_ZEROPAGE,       2,  3,  False)
OpCodes["\x94"] = (OP_STY,  MEM_ZEROPAGE_X,     2,  4,  False)
OpCodes["\x8C"] = (OP_STY,  MEM_ABSOLUTE,       3,  4,  False)

OpCodes["\xAA"] = (OP_TAX,  MEM_IMPLICIT,       1,  2,  False)
OpCodes["\xA8"] = (OP_TAY,  MEM_IMPLICIT,       1,  2,  False)
OpCodes["\xBA"] = (OP_TSX,  MEM_IMPLICIT,       1,  2,  False)
OpCodes["\x8A"] = (OP_TXA,  MEM_IMPLICIT,       1,  2,  False)
OpCodes["\x9A"] = (OP_TXS,  MEM_IMPLICIT,       1,  2,  False)
OpCodes["\x98"] = (OP_TYA,  MEM_IMPLICIT,       1,  2,  False)

def BinToHexString(s):
    """
    Convert a sttring of binary values into a Hex representation
    e.g. "\x03|Z1" outputs "037C5A31"
    """
    if type(s) != list:
        s = [s]
    if len(s) == 0:
        return ""
    if type( s[0] ) == str and len(s[0]) == 1: ## Assuming each item is a byte?
        return "".join( "%02X"%ord(b) for b in s)
    elif type(s[0] ) == str and len(s) == 1: ## We just made a list
        return "".join( "%02X"%ord(b) for b in s[0])
    else:
        return "".join( "%02X"%b for b in s)
        
class Memory(object):
    def __init__(self, size):
        self.data = [Register() for x in xrange(size)]
    
    def InitWithString(self, string):
        for n in xrange(len(string)):
            self.data[n].V = ord(string[n])
        
    def __getitem__(self, addr): 
        if type(addr) == slice:
            return [x.V for x in self.data[addr] ]
        return self.data[addr].V   
    def __setitem__(self, addr, val):
        self.data[addr].V = val
        
class MemoryBus(object):
    """
    This will act as a memory bus, directing address space to the correct
    periphreal or memory bank.
    """
    
    def __init__(self):
        self.banks = []        
        
    def fetchBank(self, addr):
        """
        Search all the banks, and return one to the addr,
        if none found, return None
        """
        foundBank = None
        for start, length, bank in self.banks:
            if addr >= start and addr < start+length:
                #Got it        
                foundBank = (bank, start)
                break
                
        return foundBank
            
    def __getitem__(self, addr):
        #Search the banks for the address
        foundBank = self.fetchBank(addr)
        
        if foundBank != None:
            return foundBank[0][addr-foundBank[1]]
        else:
            raise Exception("Memory Address {0} wasn't in a valid bank".format("%04X"%addr))
            
    def __setitem__(self, addr, val):
        #Search the banks for the address
        foundBank = self.fetchBank(addr)
        
        if foundBank != None:
            foundBank[0][addr-foundBank[1]] = val
        else:
            raise Exception("Memory Address {0} wasn't in a valid bank".format("%04X"%addr))

    def addBank(self, addr, length, bank):
        self.banks.append((addr, length, bank))
                    
class CPU6502(object):
    def __init__(self):
    
        ###
        # Registers
        ###
        self.pCnt = Register(16) # Program Counter
        self.sPtr = Register(8) # Stack Pointer
        self.regA = Register(8)  # Accumulator, used for arthmatic?
        self.regX = Register(8) # Index Register A
        self.regY = Register(8) # Index Register B
        
        
        ###
        # Bit Flags
        ###
        
        # Set if during arithmatic bit 7 overflow
        # Set during Arthmatic, comparison and logical shifts
        self.flagCarry = Flag()
        
        #Set if the last operation was zero
        self.flagZero = Flag()
        
        #Interupt Disable
        self.flagInterruptDisable = Flag()
        
        #Use Arthmatic in BCD mode during add/sub (Odd to see this, wonder where it's being used)
        self.flagDecimal = Flag()
        
        #If the interupt was caused by a software Break command
        self.flagBreak = Flag()
        
        #Raised when the operations yeild and invalid 2's bit compliment result. I.e. Wrong sign.
        #Determined by looking at carry between bits 6,7 and between bit 7 and carry flag.
        self.flagOverflow = Flag()
        
        #Is set if the result of the last operation had bit 7 set to 1. Makes sense
        self.flagNegative = Flag()
        
        self._regS = Register(8)
        self._regS.setCallOnSet( self.onRegSSet )
        
        #Setup Memeory
        self.memory = MemoryBus()
        
        ###
        # Extra Goodies
        ###
        
        self.OpCode = OP_NOP
    
    @property
    def regS(self):
        v = 0x00
        v += STAT_CARRY*int(self.flagCarry.V)
        v += STAT_ZERO*int(self.flagZero.V)
        v += STAT_INT*int(self.flagInterruptDisable.V)
        v += STAT_DEC*int(self.flagDecimal.V)
        v += STAT_BRK*int(self.flagBreak.V)
        v += STAT_OVERFLOW*int(self.flagOverflow.V)
        v += STAT_SIGN*int(self.flagNegative.V)
        
        self._regS.V = v
        return self._regS
        
    def onRegSSet(self, reg):
        #Assign all the bits to the flags
        self.flagCarry.V            = bool(reg.V & STAT_CARRY)
        self.flagZero.V             = bool(reg.V & STAT_ZERO)
        self.flagInterruptDisable.V = bool(reg.V & STAT_INT)
        self.flagDecimal.V          = bool(reg.V & STAT_DEC)
        self.flagBreak.V            = bool(reg.V & STAT_BRK)
        self.flagOverflow.V         = bool(reg.V & STAT_OVERFLOW)
        self.flagNegative.V         = bool(reg.V & STAT_SIGN)
        
        
    def LoadAsNESConsole(self):
        """
        Will load up the memory to mimick that of the NES console
        """
        self.wram = Memory(2048)
        self.memory.addBank( 0x0000, 2048, self.wram )
        self.memory.addBank( 0x0800, 2048, self.wram )
        self.memory.addBank( 0x1000, 2048, self.wram )
        self.memory.addBank( 0x1800, 2048, self.wram )
        self.ppuReg = Memory(8)
        offset = 0x2000
        while offset < 0x4000:
            self.memory.addBank( offset, 8, self.ppuReg )
            offset += 8
        self.apuReg = Memory(0x18)
        
        self.memory.addBank( 0x4000, 0x18, self.apuReg )
        
        #Weird memory bank...
        self.expansionBank = Memory((1024*8)-18)
        self.memory.addBank( 0x4018 , (1024*8)-18, self.expansionBank)
        
        #cartidge SRAM
        self.cartSRAM = Memory( 0x2000)
        self.memory.addBank(0x6000, 0x2000, self.cartSRAM)
        
        #program-rom
        self.prgRom = Memory(0x8000)
        self.memory.addBank(0x8000, 0x8000, self.prgRom)
        
    def ReadAtProgramCounter(self):
        """
        Read and return value at program counter and post increment it
        """
        result = self.memory[self.pCnt.V]
        self.pCnt.V += 1
        return result
    
    def getRegString(self):
        """
        Return String of all registers
        """
        
        result = "A:%04X X:%04X Y:%04X SP:%02X S:%02X" % (self.regA.V, self.regX.V, self.regY.V, self.sPtr.V, self.regS.V )
        return result
    
    def pushStack(self, data):
        """
        Will push the binary data onto the stack
        """
        p = self.sPtr.V
        for c in data:
            self.memory[p+128] = ord(c)
            p -= 1
        self.sPtr.V = p
        
    def popStack(self, bytes):
        """
        """
        result = ""
        p = self.sPtr.V
        for x in xrange(bytes):
            p += 1
            result += chr(self.memory[p+128])
        self.sPtr.V = p
        return result
    
    def readResetVector(self):
        """
        Will read the reset vector...
        """
        return self.memory[0xFFFC] + (self.memory[0xFFFD] << 8)
        
    def readNMIVector(self):
        """
        Will read the NMI vector...
        """
        return self.memory[0xFFFA] + (self.memory[0xFFFB] << 8)
        
    def readIRQVector(self):
        """
        Will read the IRQ/BRK vector...
        """
        return self.memory[0xFFFE] + (self.memory[0xFFFF] << 8)
    
    def Tick(self):
    
        #Fetch Instruction...
        instructionAddress = self.pCnt.V
        ins = chr(self.ReadAtProgramCounter())
        
        op, memtype, oplength, opclk, extraClockOnPageChange = OpCodes[ins]
        
        self.OpCode = op
        
        #Load in whole opcode
        lengthRem = oplength-1
        while lengthRem > 0:
            lengthRem -= 1
            ins += chr(self.ReadAtProgramCounter())
       
        #Figure out the Memory address it was pointing to or The Value...
        memoryPtr = None
        ptrPtr = None
        if memtype == MEM_IMPLICIT:
            pass
        elif memtype == MEM_ACCUMULATOR:
            pass
        elif memtype == MEM_IMMEDIATE:
            memoryPtr = ord(ins[1])
        elif memtype == MEM_ZEROPAGE:
            memoryPtr = ord(ins[1])
        elif memtype == MEM_ZEROPAGE_X:
            memoryPtr = (ord(ins[1])+self.regX.V)&0xFF # wraps around in the first 8 bits!
        elif memtype == MEM_ZEROPAGE_Y:
            memoryPtr = (ord(ins[1])+self.regX.V) # No mention of 8bit wrap around. :s
        elif memtype == MEM_RELATIVE:
            memoryPtr = (struct.unpack("b", ins[1])[0] + instructionAddress + 2)&0xFFFF # The reason for the plus 2 is that the cpu evaluates it at the end of loading the relativeoffset.
        elif memtype == MEM_ABSOLUTE:
            memoryPtr = struct.unpack("<H", ins[1:3])[0]
        elif memtype == MEM_ABSOLUTE_X:
            memoryPtr = (struct.unpack("<H", ins[1:3])[0] + self.regX.V)&0xFFFF
        elif memtype == MEM_ABSOLUTE_Y:
            memoryPtr = (struct.unpack("<H", ins[1:3])[0] + self.regY.V)&0xFFFF
        elif memtype == MEM_INDIRECT:
            ptrPtr = (struct.unpack("<H", ins[1:3])[0])
            memoryPtr = self.memory[ptrPtr]+(self.memory[ptrPtr+1]<<8)
        elif memtype == MEM_INDIRECT_X:
            #val = PEEK(PEEK((arg + X) % 256) + PEEK((arg + X + 1) % 256) * 256)	
            arg = ord(ins[1])
            memoryPtr = self.memory[(arg + self.regX.V)&0xFF] + (self.memory[(arg + self.regX.V + 1)&0xFF]*256)
        elif memtype == MEM_INDIRECT_Y:
            # val = PEEK(PEEK(arg) + PEEK((arg + 1) % 256) * 256 + Y)
            arg = ord(ins[1])
            memoryPtr = self.memory[arg] + (self.memory[(arg + 1)&0xFF]*256) + self.regY.V 

       
        #Load in Memory if it's reffereneced...
        memVal = None
        if memtype == MEM_IMMEDIATE:
            memVal = memoryPtr
        elif memoryPtr != None:
            memVal = self.memory[memoryPtr]
            
        #Print?
        memstring = ""
        if ptrPtr != None:
            memstring += "{0:6}".format(BinToHexString( struct.pack(">H", ptrPtr) ))
        if  memoryPtr != None:
            if len(memstring) > 0:
                memstring += " - "
            memstring += "{0:6}".format(BinToHexString( struct.pack(">H", memoryPtr) ))  
        if memVal != None:
            if len(memstring) > 0:
                memstring += " ~ "
            memstring += "{0:6}".format(BinToHexString( struct.pack(">H", memVal) ))  

        s = "{0:6} - {1:10} - {2:4} - {3:14}".format(
            BinToHexString(  struct.pack(">H", instructionAddress) ),
            BinToHexString(ins),
            OpToString[op],
            MemTypeToString[memtype]
            )
        print s+" + "+ memstring
        
        
        
        
        
        
        ###
        #  Execution Time!      
        ###
        if op == OP_LDA: # Load
            #load A
            self.regA.V = memVal
        elif op == OP_LDX:
            #load X
            self.regX.V = memVal
        elif op == OP_LDY:
            #load Y
            self.regY.V = memVal
        
        elif op == OP_STA: # Store
            #store A
            self.memory[memoryPtr] = self.regA.V
        elif op == OP_STX:
            #store X
            self.memory[memoryPtr] = self.regX.V
        elif op == OP_STY:
            #store Y
            self.memory[memoryPtr] = self.regY.V
            
        elif op == OP_TAX: # Transfer
            # A to X
            self.regX.V = self.regA.V
        elif op == OP_TAY:
            # A to Y
            self.regY.V = self.regA.V
        elif op == OP_TXA:
            # X to A
            self.regA.V = self.regX.V
        elif op == OP_TYA:
            # Y to A
            self.regA.V = self.regY.V
            
        elif op == OP_TSX: # Stack
            #Transfer stack prt to X
            self.regX.V = self.sPtr.V
        elif op == OP_TXS:
            #Transfer X to stack ptr
            self.sPtr.V = self.regX.V
        elif op == OP_PHA:
            #Push Accumulator onto stack
            self.pushStack( chr(self.regA.V) )
            pass
        elif op == OP_PHP:
            pass
        elif op == OP_PLA:
            pass
        elif op == OP_PLP:
            pass
            
        elif op == OP_AND: # Logic
            pass
        elif op == OP_EOR:
            pass
        elif op == OP_ORA:
            pass
        elif op == OP_BIT:
            pass
            
        elif op == OP_ADC: # Arthimetic
            pass
        elif op == OP_SBC:
            pass
        elif op == OP_CMP:
            #Compare value with the Accumulator and set the Carry bit as necessary
            if  self.regA.V >= memVal:
                #Set the Carry flag
                self.flagCarry.Set()
            pass
        elif op == OP_CPX:
            pass
        elif op == OP_CPY:
            pass
            
        elif op == OP_INC: #Inc and Dec
            #Increment at memory
            self.memory[memoryPtr] += 1
        elif op == OP_INX:
            #incrememnt Reg x
            self.regX.V += 1
        elif op == OP_INY:
            #incrememnt Reg Y
            self.regY.V += 1
        elif op == OP_DEC:
            #decrement at Reg
            self.memory[memoryPtr] -= 1
        elif op == OP_DEX:
            #decrememnt Reg x
            self.regX.V -= 1
        elif op == OP_DEY:
            #decrememnt Reg y
            self.regY.V -= 1
            
        elif op == OP_ASL: # Shifts
            pass
        elif op == OP_LSR:
            pass
        elif op == OP_ROL:
            pass
        elif op == OP_ROR:
            pass
            
        elif op == OP_JMP: # Jumps
            self.pCnt.V = memoryPtr
        elif op == OP_JSR:
            #Jump to Subroutine, push present programCounter onto stack
            self.pushStack( struct.pack( ">H", self.pCnt.V ) )
            self.pCnt.V = memoryPtr
        elif op == OP_RTS:
            pass
            
        elif op == OP_BCC: #Branches
            pass
        elif op == OP_BCS:
            #Branch on carry set
            if self.flagCarry.V:
                #Branch!
                self.pCnt.V = memoryPtr
            pass
        elif op == OP_BEQ:
            pass
        elif op == OP_BMI:
            pass
        elif op == OP_BNE:
            #Branch if not equal
            if self.flagZero.V == False:
                self.pCnt.V = memoryPtr
        elif op == OP_BPL:
            #Branch if is positive...
            if self.flagNegative.V:
                self.pCnt.V = memoryPtr
            pass
        elif op == OP_BVC:
            pass
        elif op == OP_BVS:
            pass
            
        elif op == OP_CLC: # Status Flags
            pass
        elif op == OP_CLD: #clear decimal mode. (nes doesn't support decimal mode)
            self.flagDecimal.V = False
        elif op == OP_CLI:
            pass
        elif op == OP_CLV:
            pass
        elif op == OP_SEC:
            pass
        elif op == OP_SED:
            pass
        elif op == OP_SEI: #Set interupt flag
            self.flagInterruptDisable.V = True
            
        elif op == OP_BRK: # System Functions
            pass
        elif op == OP_NOP:
            pass
        elif op == OP_RTI:
            pass

        #Update Flags
        if (self.regA.V & 0x80) != 0:
            print "a=Neg"
            self.flagNegative.Set()
        else:
            print "a=Pos"
            self.flagNegative.Clear()
            
        if self.regA.V == 0x00:
            self.flagZero.Set()
        else:
            self.flagZero.Clear()
