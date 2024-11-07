'''
This GAM is used and useful for running a MARTe2 Configuration where you want it to end execution
after an expected number of iterations.

It requires a input signal but ignores this - it is purely needed because MARTe2 doesn't allow
GAMs without signals.

The parameter MaxCycles is what sets the number of iterations the application should run for.
'''
from martepy.marte2.gam import MARTe2GAM

class EndGAM(MARTe2GAM): #pylint: disable=W0223
    '''
    This GAM is used and useful for running a MARTe2 Configuration where you want
    it to end execution after an expected number of iterations.

    It requires a input signal but ignores this - it is purely needed because MARTe2 doesn't allow
    GAMs without signals.

    The parameter MaxCycles is what sets the number of iterations the application should run for.
    '''
    def __init__(self, #pylint: disable=W0102,W1113
                    configuration_name: str = 'End',
                    maxcycles=500,
                    input_signals=[],
                    *args, **kwargs
                ):
        #assert all(('Default' in d['MARTeConfig'] for n, d in output_signals))
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'EndGAM',
                input_signals=input_signals,
                *args, **kwargs
            )
        self.maxcycles = maxcycles

    def writeGamConfig(self, config_writer):
        '''
        Write the MaxCycles parameter for our GAM
        '''
        config_writer.writeNode('MaxCycles', f'{self.maxcycles}')

def initialize(factory, plugin_datastore) -> None:
    ''' Register EndGAM to our given factory '''
    factory.registerBlock("EndGAM", EndGAM, plugin_datastore)
