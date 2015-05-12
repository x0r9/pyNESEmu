import sys
from NESEmu import *


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "DemoNES.py [path-to-Rom]"
        sys.exit()
    
    nesPath = sys.argv[1]
    nese = NESEmu()
    
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
    for x in xrange(30):
        print
        print x+1, ")"
        nese.cpu.Tick()
        print nese.cpu.getRegString()
    #nese.ReadAll()

    
    #print "Load Tune into RAM"
    #nsfr.LoadInMemory()
    #print "Init Song 1"
    #nsfr.cpu.regA.V = 1-1
    #if nsfr.TuneType == TUNE_PAL:
    #    nsfr.cpu.regX.V = 1
    #else:
    #    nsfr.cpu.regX.V = 0
    #    
    #print "Going to Address 0x"+("%04X"% nsfr.InitAddress)
    #nsfr.cpu.sPtr.V = 0xFF
    #nsfr.BeginInit()
