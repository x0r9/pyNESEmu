"""
Disassembler6502

Will attempt to disassemble 6502 binary, as a way of reverse engineering NES
games and figuring out if my Emulator is working right?
"""

import sys
from CPU6502Reverse import *
import argparse

def auto_int(x):
    return int(x,0)

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--simple", help="outputs one instruction per line",
                    action="store_true")
                    
parser.add_argument("-r", "--routine", help="just look at subroutine at address",
                    type=auto_int)

parser.add_argument("-Rs", "--refsub", help="find all references to subroutine address",
                    type=auto_int)

parser.add_argument("-l", "--length", help="limit number of bytes to crawl",
                    type=auto_int)

parser.add_argument("-V", "--vectors", help="print vector addresses",
                     action="store_true")
                                        
parser.add_argument('binpath', nargs=1, default=[], help='path to binary to disassemble')

args = parser.parse_args()


absoluteOffset = 0x8000 #This is IMPORTANT. As the NES cart address starts at 0x8000.

def getVector(name, rom, address):
    vecAddr = address 
    print  name+" Vector at : 0x{0:04X}".format(address)
    #resetaddr = resetaddr - absoluteOffset
    #print "Reset Vector at : 0x{0:04X} (after aboslute removal)".format(resetaddr)
    hi = mem[vecAddr+1]
    lo = mem[vecAddr]
    vecVal = lo + (hi<<8)
    print name+" Vector val: 0x{0:04X}".format(vecVal)
    vecVal = vecVal- absoluteOffset 
    print name+" Vector val: 0x{0:04X} (after aboslute removal)".format(vecVal)
    
    #vecAddr = rom[vecVal] + (rom[vecVal+1] << 8)
    #print name+" Final Addr : 0x{0:04X}".format(vecAddr)
    #return vecAddr
    return vecVal

if __name__ == "__main__":
    print "Disassembler6502"
    
    fpath = args.binpath[0]
    
    with open(fpath, "r") as f:
        bindata = f.read()
    
    print "Loading file", "0x{0:0000X}".format(len(bindata)), "bytes" 
    
    subroutines = []
    
    #Figure out the Reset vectors and NMI vectors...
    mem = Memory(0x8000) # 32K
    mem.InitWithString(bindata)
    
    dis = Disassembler()
    dis.LoadBinary(bindata)
   
    if args.vectors:
        print "Vectors:"
        print "NMI {0:0000X}".format(dis.GetVector(0xFFFA))
        print "RST {0:0000X}".format(dis.GetVector(0xFFFC))
        print "IRQ {0:0000X}".format(dis.GetVector(0xFFFE))
        sys.exit()
    
    startOffset = 0
    routineOffset = 0
    if args.routine:
        startOffset = args.routine - absoluteOffset
        routineOffset = startOffset
        print "start offset", startOffset
    
    if args.length:
        limit = args.length
    else:
        limit = 0
    
    # Disasemble 
    for d in dis.Walk(absoluteOffset, limit):
    
        #print d
        
        if args.simple:
            #print "s"
            sLine = "0x{0:04X} {1:4}".format(d.MemAddress, d.OpCodeString())+"  "+d.MemTypeString()
            print sLine
            
        else:
            print "ns"
            print "Address:      0x{0:04X}".format(d.MemAddress)
            print "Whole Op:     0x"+BinToHexString(d.WholeOpCode)
            print "OpCode:       {0}".format(d.OpCodeString())
            print "OpCode Long:  {0}".format(d.OpCodeLongString())
            print "OpCode Len:   {0}".format(d.OpLength)
            print d.MemTypeString() #sMemType
            print 
            
    sys.exit()
    
    
    for x in xrange(startOffset, 60000): #decode the first 10 opcodes?
        originalAddr =  disAddr + absoluteOffset + routineOffset
        binIns = mem[disAddr]
        disAddr +=1
        sbinIns = chr(binIns)
        
        #print "Address:      0x{0:04X}".format(originalAddr)
        
        if sbinIns not in OpCodes.keys():
            #print "BinIns: 0x{0:02X}".format(binIns)
            #print "Unrecognised OpCode!"
            #break
            op, memtype, oplength, opclk, extraClockOnPageChange = OP_UNKOWN, MEM_IMPLICIT, 1, 1, 1
        else:    
            op, memtype, oplength, opclk, extraClockOnPageChange = OpCodes[sbinIns]
        
        #load in full op code and know how much to offset disAdd
        disAddrAdd = 0
        lengthRem = oplength-1
        while lengthRem > 0:
            lengthRem -= 1
            sbinIns += chr(mem[disAddr])
            disAddrAdd += 1
            #disAddr += 1 
            
        opArg = 0
        if oplength > 1:
            opArg += ord(sbinIns[1])
        if oplength > 2:
            opArg += ord(sbinIns[2]) << 8 
              
        if args.refsub:
            
            if op == OP_JSR:
                if memtype == MEM_ABSOLUTE and opArg == args.refsub:
                    print "found"       
            continue
        
        #Load Full Opcode + increment Address
        disAddr += disAddrAdd
        
        opStr = OpToString[op]
        opStrLong = OpToLongString[op]
       
        opArg = 0
        if oplength > 1:
            opArg += ord(sbinIns[1])
        if oplength > 2:
            opArg += ord(sbinIns[2]) << 8   
       
        #print "Whole Op:     0x"+BinToHexString(sbinIns)
        #print "OpCode:       {0}".format(opStr)
        #print "OpCode Long:  {0}".format(opStrLong)
        #print "OpCode Len:   {0}".format(oplength)
        sMemType =  "MemType:      "+MemTypeToString[memtype]
        
        
        #Attempt to work out where we are trying to branch to?
        sMemType =  "MemType:      "+MemTypeToString[memtype]
        if memtype == MEM_ABSOLUTE:
            sMemType += " (0x{0:04X})".format(opArg)   
        elif memtype == MEM_RELATIVE:
            p = opArg
            #print "{0:02X}".format(p)
            if opArg&0x80:
                #print "neg"
                p = -((opArg^0xFF)+1) + oplength
            addr = originalAddr+p
            sMemType += " (0x{0:04X})".format(addr)
        elif memtype == MEM_IMMEDIATE:
            sMemType += " (0x{0:02X})".format(opArg) 
        elif memtype == MEM_ABSOLUTE_X or memtype == MEM_ABSOLUTE_Y:
            sMemType += " (0x{0:04X})".format(opArg) 
        #print sMemType
        #print 
        
        #print the output here...
        if args.simple:
            #print "s"
            sLine = "0x{0:04X} {1:4}".format(originalAddr, opStr)+"  "+sMemType
            print sLine
            
        else:
            print "ns"
            print "Address:      0x{0:04X}".format(originalAddr)
            print "Whole Op:     0x"+BinToHexString(sbinIns)
            print "OpCode:       {0}".format(opStr)
            print "OpCode Long:  {0}".format(opStrLong)
            print "OpCode Len:   {0}".format(oplength)
            print sMemType
            print 
        
        #If we are printing out a subroutine, stop priting if we get a return op code.
        if args.routine:
            if op == OP_RTS or opStr == OP_RTI:
                break
    
