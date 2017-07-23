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
     
def loadRam(cpu, data):
    for n, char in enumerate(data):
        cpu.memory[n] = ord(char)

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
        # Set with SEI
        loadBin(self.cpu, "\x78\x00") 
        self.assertFalse( self.cpu.flagInterruptDisable.V)
        self.cpu.Tick()
        self.assertTrue( self.cpu.flagInterruptDisable.V)
        
        # Disable with CLI
        loadBin(self.cpu, "\x58\x00") 
        self.assertTrue( self.cpu.flagInterruptDisable.V)
        self.cpu.Tick()
        self.assertFalse( self.cpu.flagInterruptDisable.V)
        
    def test_SED(self):
        """
        Test setting and unsetting of Decimal mode
        """
        # Set with SED
        loadBin(self.cpu, "\xF8\x00") 
        self.assertFalse( self.cpu.flagDecimal.V)
        self.cpu.Tick()
        self.assertTrue( self.cpu.flagDecimal.V)
        
        # Disable with CLD
        loadBin(self.cpu, "\xD8\x00") 
        self.assertTrue( self.cpu.flagDecimal.V)
        self.cpu.Tick()
        self.assertFalse( self.cpu.flagDecimal.V)
        
class TestLoadingA(unittest.TestCase):
    def setUp(self):
        """
        Create the CPU ready for testing...
        """
        self.cpu = createCPU()
        
    def test_loadALiteral(self):
        """
        Test load A literally with an immediate memory type
        """
        loadBin(self.cpu, "\xA9\x00\x00")
        self.cpu.Tick()
        self.assertEqual(self.cpu.regA.V, 0)
        
        loadBin(self.cpu, "\xA9\x01\x00")
        self.cpu.Tick()
        self.assertEqual(self.cpu.regA.V, 1)
        
        loadBin(self.cpu, "\xA9\xFF\x00")
        self.cpu.Tick()
        self.assertEqual(self.cpu.regA.V, 0xFF)
         
    def test_loadAZeropage(self):
        """
        Test load A with zeropage
        """
        loadRam(self.cpu, "\xA5\x5A\xAA\x55")
        loadBin(self.cpu, "\xA5\x00\x00")
        self.cpu.Tick()
        self.assertEqual(self.cpu.regA.V, 0xA5)
        
        loadBin(self.cpu, "\xA5\x01\x00")
        self.cpu.Tick()
        self.assertEqual(self.cpu.regA.V, 0x5A)
        
        loadBin(self.cpu, "\xA5\xFF\x00")
        self.cpu.Tick()
        self.assertEqual(self.cpu.regA.V, 0x00)   
                     
if __name__ == '__main__':
    unittest.main()
