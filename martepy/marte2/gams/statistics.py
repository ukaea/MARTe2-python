''' Pythonic representation of the PID GAM'''

from martepy.marte2.gam import MARTe2GAM
from martepy.marte2.qt_functions import (addInputSignalsSection,
                                         addOutputSignalsSection,
                                         addLineEdit)

class StatisticsGAM(MARTe2GAM):
    ''' Pythonic representation of the Statistics GAM'''
    def __init__(self,
                    configuration_name: str = 'Statistics',
                    input_signals: list = [],
                    output_signals: list = [],
                    windowsize = 0,
                    startcyclenumber = 0,
                    infinitemaxmin = 0
                ):
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'StatisticsGAM',
                input_signals = input_signals,
                output_signals = output_signals,
            )
        self.windowsize = windowsize
        self.startcyclenumber = startcyclenumber
        self.infinitemaxmin = infinitemaxmin

    def writeGamConfig(self, config_writer):
        ''' Write our GAM Configuration '''
        config_writer.writeNode("WindowSize",self.windowsize)
        config_writer.writeNode("StartCycleNumber",self.startcyclenumber)
        config_writer.writeNode("InfiniteMaxMin",self.infinitemaxmin)

    def serialize(self):
        ''' Serialize the object '''
        res = super().serialize()
        res['parameters']['windowsize'] = self.windowsize
        res['parameters']['startcyclenumber'] = self.startcyclenumber
        res['parameters']['infinitemaxmin'] = self.infinitemaxmin
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True) -> bool:
        ''' Deserialize the given object to the class instance '''
        super().deserialize(data, hashmap, restore_id)
        # Now we build up
        self.windowsize = data['parameters']["windowsize"]
        self.startcyclenumber = data['parameters']["startcyclenumber"]
        self.infinitemaxmin = data['parameters']["infinitemaxmin"]
        return self

    @staticmethod
    def loadParameters(mainpanel_instance, node):
        """This function is intended to be for the GUI where it can
        call the static instance of the class directly to generate
        the appropriate parameter modifier for the node in XMARTe2.
        """
        app_def = mainpanel_instance.parent.API.getServiceByName('ApplicationDefinition')
        datasource = app_def.configuration['misc']['gamsources'][0]
        addInputSignalsSection(mainpanel_instance, node, False)

        addOutputSignalsSection(mainpanel_instance, node, 3, False, datasource=datasource)

        addLineEdit(mainpanel_instance, node, "Window Size: ", 'windowsize', 3, 0)

        addLineEdit(mainpanel_instance, node, "Start Cycle Number: ", 'startcyclenumber', 3, 2)
        
        addLineEdit(mainpanel_instance, node, "Infinite Max Min: ", 'infinitemaxmin', 4, 0)


def initialize(factory, plugin_datastore) -> None:
    ''' Initialize the object with the factory '''
    factory.registerBlock("StatisticsGAM", StatisticsGAM, plugin_datastore)
