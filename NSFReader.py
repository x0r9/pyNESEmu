"""
Base class for reading basic NSF files
"""

from CPU6502 import *
import struct

#Enumerate Tune type
TUNE_NTSC   = 1
TUNE_PAL    = 2
TUNE_DUAL   = 3

TuneToString = {
    TUNE_NTSC:"NTSC",
    TUNE_PAL :"PAL",
    TUNE_DUAL:"DUAL"
}

def GetNullTerminatedString(data):
    i = data.find("\x00")
    if i >= 0:
        return data[:i]
    return data

class NSFReader(object):
    def __init__( self, path ):
        self.path = path
        self.file = open( self.path, "rb" )
        
        self.Version = None
        self.TotalSongs = -1
        self.StartingSongIndex = -1
        self.LoadAddress = -1
        self.InitAddress = -1
        self.PlayAddress = -1
        self.SongName = None
        self.Artist = None
        self.Copyright = None
        
        self.cpu = CPU6502()
        self.cpuMemoryBus = MemoryBus()
        self.cpuMemory = None
        self.fileData = ""
        self.tuneData = ""
        self.PlayBackSpeedNTSC = None
        self.PlayBackSpeedPAL = None
        self.BankSwitchingValues = None
        
        self.TuneType = None
        self.ExtraSoundChipsBits = None
        self.ExpansionBytes = None
        
    def ReadAll( self ):
        """
        do as it say, Read the bloody File!
        """

        #Okay, take a peek at the Header :)
        self.fileData = self.file.read(5)
        magicword = self.fileData[0:5] 
        if magicword != "NESM\x1A":
            raise Exception("Not a recognised NSF File")
		
        self.fileData += self.file.read(1)	
        self.Version = ord( self.fileData[-1] )
        if self.Version != 1:
            raise Exception("Does not support version {0}".format( self.Version ))
		
        self.fileData += self.file.read(8)    
        self.TotalSongs = ord( self.fileData[6] )
        self.StartingSongIndex = ord( self.fileData[7] )
        self.LoadAddress = struct.unpack("<H", self.fileData[8:10])[0]
        self.InitAddress = struct.unpack("<H", self.fileData[10:12])[0]
        self.PlayAddress = struct.unpack("<H", self.fileData[12:14])[0]
        
        self.fileData += self.file.read()
        
        self.SongName       = GetNullTerminatedString( self.fileData[14:46] )
        self.Artist         = GetNullTerminatedString( self.fileData[46:78] )
        self.Copyright      = GetNullTerminatedString( self.fileData[78:110] )
        
        self.PlayBackSpeedNTSC = struct.unpack("<H",self.fileData[110:112])[0]
        self.BankSwitchingValues = self.fileData[112:120]
        self.PlayBackSpeedPAL = struct.unpack("<H",self.fileData[120:122])[0]
        
        tuneTypeBits = ord(self.fileData[122])
        if tuneTypeBits&0x02:
            self.TuneType = TUNE_DUAL
        elif tuneTypeBits&0x01:
            self.TuneType = TUNE_PAL
        else:
            self.TuneType = TUNE_NTSC           
        
        self.ExtraSoundChipsBits = ord(self.fileData[123])
        self.ExpansionBytes = self.fileData[124:128]
        self.tuneData = self.fileData[128:]
        #Load file into CPU memory
        self.cpu.LoadAsNESConsole()
        #self.cpu.
        #self.cpu.prgRom.InitWithString(self.tuneData)
    def GetPlayCallFreq(self):
        """
        Return the frequency as to what to call the play frequency...
        """
        ticks = self.PlayBackSpeedNTSC
        if self.TuneType == TUNE_PAL:
            ticks = self.PlayBackSpeedPAL
        
        return 1000000.0/float(ticks)
    
    def UsesBankSwitching(self):
        """
        Return Boolean if bankswitching is used
        """
        return self.BankSwitchingValues != "\x00\x00\x00\x00\x00\x00\x00\x00"
    
    def LoadInMemory(self):
        """
        Will load the song data into the right memory, will select and copy into the correct memory banks
        """
        
        if not self.UsesBankSwitching():
            #No banks used, use 0-2K space...
            fa = self.LoadAddress
            #print "%04X"% fa
            ma = 0
            while ma < 2048:
                #print ma, fa 
                v = ord(self.tuneData[ma])
                self.cpu.memory[fa] = v
                ma += 1
                fa += 1
        else:
            #Load in the data at the sepcified load address
            fa = self.LoadAddress
            #print "%04X"% fa
            ma = 0
            while ma < 2048:
                #print ma, fa 
                v = ord(self.tuneData[ma])
                self.cpu.memory[fa] = v
                ma += 1
                fa += 1
    def BeginInit(self):        
        self.cpu.pCnt.V = self.InitAddress
        print self.cpu.getRegString()
        for x in xrange(30):
            print
            print x+1, ")"
            self.cpu.Tick()
            print self.cpu.getRegString()
            
            if self.cpu.OpCode == OP_BRK:
                print "reached BRK"
                return
                
    def PlayTick(self):
        self.cpu.pCnt.V = self.PlayAddress
        print self.cpu.getRegString()
        for x in xrange(30):
            print
            print x+1, ")"
            self.cpu.Tick()
            print self.cpu.getRegString()
            
            if self.cpu.OpCode == OP_BRK:
                print "reached BRK"
                return
        
