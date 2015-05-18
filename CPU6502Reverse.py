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
    MemAddress = 0
    WholeOpCode = ""
    
    def OpCodeString(self):
        return OpToString[self.OpCode]
    def OpCodeLongString(self):
        return OpToLongString[self.OpCode]
        
    def MemTypeString(self):
        sMemType =  "MemType:      "+MemTypeToString[self.MemType]
        if self.MemType == MEM_ABSOLUTE:
            sMemType += " (0x{0:04X})".format(self.OpArg)   
        elif self.MemType == MEM_RELATIVE:
            p = self.OpArg
            #print "{0:02X}".format(p)
            if self.OpArg&0x80:
                #print "neg"
                p = -((self.OpArg^0xFF)+1) + self.OpLength
            addr = self.MemAddress+p
            sMemType += " (0x{0:04X})".format(addr)
        elif self.MemType == MEM_IMMEDIATE:
            sMemType += " (0x{0:02X})".format(self.OpArg) 
        elif self.MemType == MEM_ABSOLUTE_X or self.MemType == MEM_ABSOLUTE_Y:
            sMemType += " (0x{0:04X})".format(self.OpArg) 
        elif self.MemType == MEM_ZEROPAGE:
            sMemType += " (0x{0:04X})".format(self.OpArg) 
        return sMemType 
    def GetMemPointer(self):
        if self.MemType == MEM_ABSOLUTE:
            return  self.OpArg
        if  self.MemType == MEM_RELATIVE:
            p = self.OpArg
            #print "{0:02X}".format(p)
            if self.OpArg&0x80:
                #print "neg"
                p = -((self.OpArg^0xFF)+1) + self.OpLength
            return self.MemAddress+p
        if self.MemType == MEM_IMMEDIATE:
            return self.OpArg
        if self.MemType == MEM_ZEROPAGE:
            return self.OpArg
        
def Disassemble(bin):
    """
    Attempt to decode binary, and return tuple with:
    op, memtype, oplength, opclk, extraClockOnPageChange
    """
    res = DisOpCode()
    # Convert bin to a string type...
    if type( bin[0] ) == int:
        nbin = ""
        for b in bin:
            nbin += chr(b)
        bin = nbin
        
    sbinIns = bin[0]

    if sbinIns in OpCodes.keys():
        op, memtype, oplength, opclk, extraClockOnPageChange = OpCodes[sbinIns]
        res.OpCode = op
        res.MemType = memtype
        res.OpLength = oplength
        res.OpClks = opclk
        res.OpClkPageChange = extraClockOnPageChange
        #Attempt to read in an argument
     
        opArg = 0
        if oplength > 1:
            opArg += ord(bin[1])
        if oplength > 2:
            opArg += ord(bin[2]) << 8 
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
        
    def DecodeAtAddress(self, address):
        ti = self.GetMemLoc(location)
        
        
    def Walk(self, address, limit=0, align=True):
        currentAddress = address
        i = 0
        while i < limit or limit == 0:
            #print "get b",     currentAddress        
            b = self.GetBytesAt(currentAddress)
            opDecode = Disassemble(b)
           
            opDecode.MemAddress = currentAddress
            opDecode.WholeOpCode = b[:opDecode.OpLength]
            
            nudge = 1
            if align:
                nudge = opDecode.OpLength
                
            i += nudge
            currentAddress += nudge
                
            yield opDecode
        
class MemHints(object):
    TYPE_REG = 3
    TYPE_SUB = 1
    TYPE_MEM = 2
    
    TypeLookUp = { "reg" : TYPE_REG ,
                "sub": TYPE_SUB,
                "mem": TYPE_MEM }
        
    def __init__(self):
        self.map = {}
        
    def LoadFile(self, path):
        f = open(path, "r")
        for l in f:
            l = l.strip()
            p = l.split(",")
            if len(p)  < 3:
                continue
            
            addr = int(p[0], 0)
            mtype = self.TypeLookUp[p[1]]
            comment = p[2]
            
            self.map[addr] = (mtype, comment)
    def GetHintAtAddr(self, addr):
        if not addr in self.map.keys():
            return None
        return self.map[addr]  
