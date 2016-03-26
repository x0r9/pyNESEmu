"""
NES debug, a utility for loading in a nes game and actively debugging it
"""

import sys
from NESEmu import *


def parseaddress(sadd):
    if not sadd.startswith("0x") or not sadd.startswith("x"):
        try:
            return int(sadd, 16)
        except ValueError:
            return None
    else:
        try:
            return int(sadd)
        except ValueError:
            return None


class MemoryBusDbg(MemoryBus):
    """
    A bus that will replace the CPU memory bus class
    This allows us to modify the memory, particularly perma setting bits
    from peripheral. 
    """
    def __init__(self, memorybus):
        """
        will inherit already instantiated memory bus
        """
        super(MemoryBusDbg, self).__init__()
        #self = memorybus
        self.banks = memorybus.banks
        self.masks = {}
       
        
    def addMask(self, address, mask, value):
        """
        address = the address to be affected
        mask = the bits that will be set high/low
        value = the value of the bits that are set high or low
        
        so if you want xx1100xx
        mask = 0x3C
        value = 0x30
        """
        self.masks[address] = (mask, value)
    
    def __getitem__(self, addr):
        result = super(MemoryBusDbg, self).__getitem__( addr)
        #result = super().__getitem(self, addr)
        print "before", result, addr
        #See if mask exists
        maskval = self.masks.get(addr, None)

        
        if maskval:
            # Apply mask that does exist
            mask, value = maskval
            
            invertmask = (2**8)-1 # just equals 0xFF
            invertmask = invertmask^mask # xor 0xFF is more reliable than ~
            result = (result&invertmask) | (value&mask)
            
        return result


if __name__ == "__main__":
    print "NES dbg"
    
    if len(sys.argv) < 2:
        print "NESdbg.py [path-to-Rom]"
        sys.exit()
    
    nesPath = sys.argv[1]
    nese = NESEmu()
    
    #inject debugging memory bus
    modbus =  MemoryBusDbg(nese.membus)
    nese.membus = modbus
    nese.cpu.memory = modbus
    
    print "Loading Cart"
    nese.loadCartFile(nesPath)
    print "Cart Loaded!"
    
    nese.cpu.sPtr.V = 0xFF
    #nese.cpu.BeginInit()
    resetVector = nese.cpu.readResetVector()
    print "rv: "+str(resetVector)
    nese.cpu.pCnt.V = resetVector
    
    #load in address..
    print "reset Vector: {0:02X} {1:02X}".format(nese.cpuMemoryBus[0xFFFC],nese.cpuMemoryBus[0xFFFD])
    print nese.cpu.getRegString()
    
    
    #Pause loading here and ask user what to do next
    while True:
        uinput = raw_input(">>>").strip()
        uinputp = uinput.split(" ")
        if uinput == "i": # step into
            nese.cpu.Tick()                        
            print nese.cpu.getRegString()
        if uinput == "rst":
            nese.cpu.sPtr.V = 0xFF
            #nese.cpu.BeginInit()
            resetVector = nese.cpu.readResetVector()
            print "rv: "+str(resetVector)
            nese.cpu.pCnt.V = resetVector
            print "reset"
            print nese.cpu.getRegString()
        if uinputp[0] == "set":
            if len(uinputp) < 3:
                print "set [reg/addrs] [value] [mask]"
            else:
                
                #are we a reg or mem address...
                addr = parseaddress(uinputp[1])
                value = parseaddress(uinputp[2])
                mask = parseaddress(uinputp[3])

                print addr,value,mask

                if  addr is None or value is None or mask is None:
                    print "invalid args"
                else:
                    nese.membus.addMask(addr, mask, value)
        if uinputp[0] == "jmp":
            if len(uinputp) < 2:
                print "jmp [addr]"
            else:
                # Set instruction pointer to given address.
                addr = parseaddress(uinputp[1])
                if addr is None:
                    print "invalid args"
                else:
                    nese.cpu.pCnt.V = addr
        if uinputp[0] == "r":
            if len(uinputp) < 2:
                print "r [reg/addrs]"
            else:
                addr = parseaddress(uinputp[1])
                if not addr:
                    print "invalid addr"
                else:
                    try:
                        v = nese.membus[addr]
                        print "read {0:04X} : {1:02X}".format(addr, v)

                    except ValueError:
                        print "could not read address"


        if uinput == "q":
            sys.exit()
