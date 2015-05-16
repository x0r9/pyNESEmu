"""
A module to help reverse engineer / disassemble 6502 binaries
"""

from CPU6502 import *

class DisOpCode(object):
    OpCode = OP_UNKOWN
    MemType =  MEM_IMPLICIT
    OpLength = 1
    OpClks = 1
    OpClkPageChange = 1
    OpArg = None

def Disassemble(bin):
    """
    Attempt to decode binary, and return tuple with:
    op, memtype, oplength, opclk, extraClockOnPageChange
    """
    res = DisOpCode()

    if sbinIns in OpCodes.keys():
        op, memtype, oplength, opclk, extraClockOnPageChange = OpCodes[sbinIns]
        res.OpCdoe = op
        res.MemType = memtype
        res.OpLength = oplength
        res.OpClks = opclk
        res.OpClkPageChange = extraClockOnPageChange
        #Attempt to read in an argument
     
        opArg = 0
        if oplength > 1:
            opArg += ord(sbinIns[1])
        if oplength > 2:
            opArg += ord(sbinIns[2]) << 8 
        if oplength > 1:      
            res.OpArg = opArg  
            
    return res

class Disassembler(object):
    def __init__(self):
        self.binaryOffset = 0x8000
        self.binary = Memory(0x8000) # 32K
        pass
        
    def LoadBinary(self, bindata):
        self.binary.InitWithString(bindata)
    
    def GetMemLoc(self, location):
        return location - self.binaryOffset
    
    def GetBytesAt(self, location, amount=3):
        ti = self.GetMemLoc(location)
        return self.binary[ti:ti+amount] 
        
    def GetVector(self, address):
        vecAddr = self.GetMemLoc(address)
        hi = self.binary[vecAddr+1]
        lo = self.binary[vecAddr]
        vecVal = lo + (hi<<8)
        return vecVal
    
