"""
A simple program to strip out all the headers+other stuff 
"""

import sys
from NESEmu import NESEmu

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "NESStrip.py [input] [output]"
        sys.exit()
    inpath = sys.argv[1]
    outpath = sys.argv[2]
    
    if inpath == "-h":
        #Just print out the header
        inpath = outpath
        nesLoader = NESEmu()
        nesLoader.loadCartFile(inpath)
    else:
        #load in file
        nesLoader = NESEmu()
        nesLoader.loadCartFile(inpath)
    
        #save file
        print "Saving PRGROM"
        with open(outpath, "wb") as f:
            f.write(nesLoader.PRGROM)
        print "all saved"
    
    
