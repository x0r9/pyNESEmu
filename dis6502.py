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

parser.add_argument("-M", "--memmap", help="file for memory map, print hints on assembler",
                     )
                                        
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
    
    #load in mem hints
    memhints = MemHints()
    if args.memmap:
        memhints.LoadFile(args.memmap)
    
    dis = Disassembler()
    dis.LoadBinary(bindata)
   
    if args.vectors:
        print "Vectors:"
        print "NMI {0:0000X}".format(dis.GetVector(0xFFFA))
        print "RST {0:0000X}".format(dis.GetVector(0xFFFC))
        print "IRQ {0:0000X}".format(dis.GetVector(0xFFFE))
        sys.exit()
    
    startDisFrom = absoluteOffset
    if args.routine:
        startDisFrom = args.routine
    
    if args.length:
        limit = args.length
    else:
        limit = 0
    
    walkAlign = True
    if args.refsub:
        #Walk the binary, but try and find where there are jumps to the address
        walkAlign = False
    
    # Disasemble 
    for d in dis.Walk(startDisFrom, limit, walkAlign):
    
        #print d
        
        if args.refsub and d.OpCode != OP_JSR:
            continue
        elif args.refsub and d.OpArg != args.refsub:
            continue
        
        #check for a memhint
        mhAtAddr = memhints.GetHintAtAddr(d.MemAddress)
        mhAtArgAddr = d.GetMemPointer()
        mhAtArg = None
        if mhAtArgAddr != None:
            mhAtArg = memhints.GetHintAtAddr(mhAtArgAddr)
            
        hintLine = ""
        if  mhAtAddr:
            hintLine += "At - "+   mhAtAddr[1]+ " "
        if mhAtArg:
            hintLine += "Ptr - "+ mhAtArg[1]
        
        if args.simple:
            #print "s"
            sLine = "0x{0:04X} {1:4}".format(d.MemAddress, d.OpCodeString())+"  "+d.MemTypeString()
            if len(hintLine) > 0:
                sLine += " ; "+hintLine
            print sLine
            
        else:
            print "ns"
            print "Address:      0x{0:04X}".format(d.MemAddress)
            print "Whole Op:     0x"+BinToHexString(d.WholeOpCode)
            print "OpCode:       {0}".format(d.OpCodeString())
            print "OpCode Long:  {0}".format(d.OpCodeLongString())
            print "OpCode Len:   {0}".format(d.OpLength)
            print d.MemTypeString() #sMemType
            if len(hintLine) > 0:
                print "Hint:            "+hintLine
            print 
            
        #If we are printing out a subroutine, stop printing if we get a return op code.
        if args.routine:
            if d.OpCode == OP_RTS or d.OpCode == OP_RTI:
                break    
            
    sys.exit()
    
    
   
    
    
