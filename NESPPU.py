

from CPU6502 import Memory
from CPU6502 import Register


REGADDR_CONTROLLER = 0x00
REGADDR_MASK = 0x01
REGADDR_STATUS = 0x02
REGADDR_OAMADDR = 0x03
REGADDR_OAMDATA = 0x04
REGADDR_SCROLL = 0x05
REGADDR_ADDRESS = 0x06
REGADDR_DATA = 0x07

ANALOGUE_PAL = 1
ANALOGUE_NTSC = 2
ANALOGUE_STATE_VBLANK = 1

class AnalogueTV(object):
    def __init__(self):
        self.state = ANALOGUE_STATE_VBLANK
        self.line = 0
        self.System = ANALOGUE_NTSC
        self.timeElapsed = 0.0
    
    def isVBlank(self):
        return self.state == ANALOGUE_STATE_VBLANK


class NESPPUMemory(Memory):
    def __init__(self):
        self.data = []
        self.Controller = Register()
        self.Mask = Register()
     
        self.TV = AnalogueTV()
        
    def GenerateStatusRegister(self):
        print "GenerateStatusRegister"
        result = 0
        if self.TV.isVBlank():
            result += 0x80
        return result
     
    def __getitem__(self, addr): 
        sAddr = addr%8
        if sAddr == REGADDR_CONTROLLER: 
            return self.Controller.V
        elif sAddr == REGADDR_MASK:
            return self.Mask.V
        elif sAddr == REGADDR_STATUS:
            return self.GenerateStatusRegister()
        else:
            print "Unrecognised PPU Register {0:02X} / {1:0004X}".format(sAddr, addr)
            
              
        
    def __setitem__(self, addr, val):
        sAddr = addr%8
        if sAddr == REGADDR_CONTROLLER: 
            self.Controller.V = val
        elif sAddr == REGADDR_MASK:
            self.Mask.V = val
        elif sAddr == REGADDR_STATUS:
            print "CAN NOT WRITE TO PPU STATUS Reg!"
        else:
            print "Unrecognised PPU Register {0:02X} / {1:0004X}".format(sAddr, addr)

