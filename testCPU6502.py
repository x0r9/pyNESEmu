"""
Simple tests to ensure the CPU emulation is operating correctly
"""


import unittest

import CPU6502

def createCPU():
    cpu = CPU6502.CPU6502()
    cpu.LoadAsNESConsole()
    return cpu

def loadBin(cpu, data):
    for n, char in enumerate(data):
        cpu.memory[0x8000+n] = ord(char)
    
    #reset Program Register
    
    cpu.pCnt.V = 0x8000
     

class TestCPUStatusReg(unittest.TestCase):
    def setUp(self):
        """
        Create the CPU ready for testing...
        """
        self.cpu = createCPU()
        print "setup"
        
    def test_SEI(self):
        """
        Test Setting and unsetting of Interupt Disable flag...
        """
        loadBin(self.cpu, "\x78\x00")
        self.assertFalse( self.cpu.flagInterruptDisable.V)
        self.cpu.Tick()
        self.assertTrue( self.cpu.flagInterruptDisable.V)
        loadBin(self.cpu, "\x58\x00")
        self.assertTrue( self.cpu.flagInterruptDisable.V)
        self.cpu.Tick()
        self.assertFalse( self.cpu.flagInterruptDisable.V)

if __name__ == '__main__':
    unittest.main()
