"""
Base class for reading basic NSF files
"""

from CPU6502 import *
from NESPPU import *
import struct

MIRROR_VERTICAL     = 1
MIRROR_HORIZONTAL   = 2
MIRROR_4SCREEN      = 3

NESFORMAT_1_0        = 1
NESFORMAT_2_0        = 2
TV_NTFS             = 0
TV_PAL              = 1
TV_BOTH             = 2

class NESEmu(object):
    """
    This class will hold an instance of one whole NES console.
    """
    def __init__(self):
        
        ######
        #Generate Memory structure
        ######
        
        self.mem_workRam = Memory(0x800)
        self.mem_PPURegisters = NESPPUMemory()
        self.mem_APURegisters = Memory(0x20)
        self.mem_cartExpan = Memory(0x2000-0x0020) # 8k?
        self.mem_cartSRAM = Memory(0x2000) # 8k?
        self.mem_cart = Memory(0x8000) # 32K
        self.membus = MemoryBus()
        
        #Work ram Mirrored
        for i in xrange(4):
            self.membus.addBank(0x0000+i*0x0800, 0x0800,self.mem_workRam)
        
        #PPU ram Mirrored
        for i in xrange(1024):
            self.membus.addBank(0x0800+i*0x0008, 0x0008, self.mem_PPURegisters)
        
        #APU
        self.membus.addBank(0x4000, 0x0020, self.mem_APURegisters)
        
        #Expansion
        self.membus.addBank(0x4020, 0x2000-0x0020, self.mem_cartExpan)
        
        #SRAM
        self.membus.addBank(0x6000, 0x2000, self.mem_cartSRAM)
        
        #cart?
        self.membus.addBank(0x8000, 0x8000, self.mem_cart)
        
        
        #Generate and initilise CPU
        self.cpu = CPU6502()
        self.cpu.memory= self.membus
        self.cpuMemoryBus = self.membus
        self.cpuMemory = None
        
        #Cart Properties
        self.mirrormode = MIRROR_HORIZONTAL
        self.sramPresent = False
        self.sramPresent10 = False # same big in 10th flag byte
        self.trainerPresent = False
        self.playChoicePresent = False
        self.nesFormat = NESFORMAT_1_0
        self.tvSystem9 = TV_NTFS 
        self.tvSystem10 = TV_NTFS 
        self.boardHasBusConflicts = False
        
        self.PRGROM = ""
        self.CHRROM = ""
        
    def loadCartFile(self, path):
        """
        Load in file and commit it to the cart memory bank.
        """
        
        file = open(path, "rb")
        sfile = file.read()
        file.close()
        
        ###
        # Disect NES file format.
        ###
        
        #Magical word check
        sMagic = sfile[0:4]
        if sMagic != "NES\x1A":
            print "Invalid NES file"
            return
            
        bflags = struct.unpack("BBBBBBB", sfile[4:4+7])    
        
        PRG_size =  bflags[0]*16*1024
        CHR_size =  bflags[1]*8*1024 # 0 means board uses CHR_ram?
        flags6 =    bflags[2]
        flags7 =    bflags[3]
        PRGr_size = bflags[4]*8*1024
        flags9 =    bflags[5]
        flags10 =   bflags[6]
        
        #check for the zeros
        if sfile[11:16] != "\x00\x00\x00\x00\x00":
            print "Zero area isn't zero"
            return
        
        #Flag6 disection
        mirrorbits = flags6 & 0x09
        if mirrorbits == 0x00:
            self.mirrormode = MIRROR_HORIZONTAL
        elif mirrorbits == 0x01:
            self.mirrormode = MIRROR_VERTICAL
        else:
            self.mirrormode = MIRROR_4SCREEN
        
        srambits = flags6 & 0x02
        if srambits > 0:
            self.sramPresent = True
        else:
            self.sramPresent = False
        
        trainerbit = flags6 &0x04
        if trainerbit > 0:
            self.trainerPresent = True
        else:
            self.trainerPresent = False
        
        mapperLowerNibble = (flags6 &0xF0) >> 4
        
        #Flag7 disection
        vsbits = flags7 & 0x01
        if vsbits > 0:
            self.vsUnisystemPresent = True
        else:
            self.vsUnisystemPresent = False
        
        playchoicebits = flags7 & 0x02
        if playchoicebits > 0:
            self.playChoicePresent = True
        else:
            self.playChoicePresent = False
        
        nesformatbits = (flags7 & 0x0B) >> 2
        if nesformatbits == 2:
            self.nesFormat = NESFORMAT_2_0
        else:
            self.nesFormat = NESFORMAT_1_0
        
        mapperUpperNibble = (flags7 & 0xF0) >> 4
        
        #flag9 disection
        
        tvsystem9bit = flags9 & 0x01
        if tvsystem9bit > 0:
            self.tvSystem9 = TV_PAL
        else:
            self.tvSystem9 = TV_NTFS
            
        #other bits should be 0
        zerobits = flags9 & 0xFE
        if zerobits != 0:
            print "Zero bits in flags9 not ZERO!"
        
        #disect flags10
        
        tvsystem10bits = flags10 & 0x03
        if tvsystem10bits == 0:
            self.tvSystem10 = TV_NTFS 
        elif tvsystem10bits == 2:
            self.tvSystem10 = TV_PAL
        else:
            self.tvSystem10 = TV_BOTH
        
        srampresent10bits = flags10 & 0x10
        if srampresent10bits > 0:
            self.sramPresent10 = True
        else:
            self.sramPresent10 = False
        
        busconflictbit = flags10 & 0x20
        if busconflictbit > 0:
            self.boardHasBusConflicts = True
        else:
            self.boardHasBusConflicts = False
        
        memoryOffset = 16
        
        if self.trainerPresent:
            print "Trainer Present"
            memoryOffset += 512
        else:
            print "Traint not present"
        
        print "Loading PRG ROM"
        self.PRGROM = sfile[memoryOffset:memoryOffset+PRG_size]
        memoryOffset += PRG_size
        print "PRGROM size: "+str(len(self.PRGROM))
        self.CHRROM = sfile[memoryOffset:memoryOffset+CHR_size]
        print "Reset Vector {0:02X} {1:02X}".format(ord(self.PRGROM[0xFFFC-0x8000]),ord(self.PRGROM[0xFFFD-0x8000]))
        print "CHRROM size: "+str(len(self.CHRROM))
        
        
        self.mem_cart.InitWithString(self.PRGROM)
        