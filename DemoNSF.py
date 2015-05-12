import sys
from NSFReader import *


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "DemoNSF.py [path-to-NSF]"
        sys.exit()
    
    nsfPath = sys.argv[1]
    nsfr = NSFReader(nsfPath)
    
    nsfr.ReadAll()
    
    print "Loaded in", len(nsfr.fileData), "Bytes"
    print "Name:        "+nsfr.SongName
    print "Artist:      "+nsfr.Artist
    print "Copyright:   "+nsfr.Copyright
    print "Total Songs:", nsfr.TotalSongs
    print "Type       :", TuneToString[nsfr.TuneType]
    print "Call-Freq  : %2.2f Hz" % nsfr.GetPlayCallFreq()
    print "Use BSwitch:", nsfr.UsesBankSwitching()
    print "Switch vals:", BinToHexString(nsfr.BankSwitchingValues)
    print "Expans vals:", BinToHexString(nsfr.ExpansionBytes)
    
    print "Load Tune into RAM"
    nsfr.LoadInMemory()
    print "Init Song 1"
    nsfr.cpu.regA.V = 1-1
    if nsfr.TuneType == TUNE_PAL:
        nsfr.cpu.regX.V = 1
    else:
        nsfr.cpu.regX.V = 0
        
    print "Going to Address 0x"+("%04X"% nsfr.InitAddress)
    nsfr.cpu.sPtr.V = 0xFF
    nsfr.BeginInit()
    print
    print "PlayTick"
    print
    nsfr.PlayTick()
