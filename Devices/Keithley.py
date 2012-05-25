'''
Created on 25.05.2012

@author: Mathias
'''

import visa

class K2602A(object):
    '''
    classdocs
    '''

    def __init__(self, port):
        '''
        Constructor
        '''
        self.instr=visa.Instrument(self.port)
        self.instr.write('smua.reset')
        self.instr.write('smub.reset')
        self.instr.write('beeper.enable = beeper.ON')
        self.instr.write('beeper.beep(0.4,2300)')
        
    def a_get_current(self):
        return self.instr.ask('print(smua.measure.i())')
    
    def a_get_voltage(self):
        return self.instr.ask('print(smua.measure.i())')
    
    def a_set_voltage(self, voltage):
        '''
        voltage in [V]
        '''
        self.a_set_DCVolts_as_source()
        self.instr.write('smua.source.levelv = ' + str(voltage))
        
    def a_set_current(self, voltage):
        '''
        current in [A]
        '''
        self.a_set_DCAmps_as_source()
        self.instr.write('smua.source.leveli = ' + str(voltage))
    
    def a_set_current_limit(self, limit):
        self.instr.write('smua.source.limiti = ' + str(limit))
    
    def a_on_output(self):
        self.instr.write('smua.source.output = smua.OUTPUT_ON')
        
    def a_off_output(self):
        self.instr.write('smua.source.output = smua.OUTPUT_OFF')
    
    def a_set_DCAmps_as_source(self):
        self.instr.write('smua.source.func = smua.OUTPUT_DCAMPS')
    def a_set_DCVolts_as_source(self):
        self.instr.write('smua.source.func = smua.OUTPUT_DCVolts')