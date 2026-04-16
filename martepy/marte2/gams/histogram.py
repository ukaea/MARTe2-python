''' Pythonic representation of the PID GAM'''

from martepy.marte2.gam import MARTe2GAM
from martepy.marte2.qt_functions import (addInputSignalsSection,
                                         addOutputSignalsSection,
                                         addLineEdit,
                                         addComboEdit)

class HistogramGAM(MARTe2GAM):
    ''' Pythonic representation of the Histogram GAM'''
    def __init__(self,
                    configuration_name: str = 'Histogram',
                    input_signals: list = [],
                    output_signals: list = [],
                    begincyclenumber = 0,
                    statechangeresetname = "All"
                ):
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'HistogramGAM',
                input_signals = input_signals,
                output_signals = output_signals,
            )
        self.begincyclenumber = begincyclenumber
        self.statechangeresetname = statechangeresetname

    def writeGamConfig(self, config_writer):
        ''' Write our GAM Configuration '''
        config_writer.writeNode("BeginCycleNumber",self.begincyclenumber)
        config_writer.writeNode("StateChangeResetName",self.statechangeresetname)

    def serialize(self):
        ''' Serialize the object '''
        res = super().serialize()
        res['parameters']['begincyclenumber'] = self.begincyclenumber
        res['parameters']['statechangeresetname'] = self.statechangeresetname
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True) -> bool:
        ''' Deserialize the given object to the class instance '''
        super().deserialize(data, hashmap, restore_id)
        # Now we build up
        self.begincyclenumber = data['parameters']["begincyclenumber"]
        self.statechangeresetname = data['parameters']["statechangeresetname"]
        return self

    @staticmethod
    def loadParameters(mainpanel_instance, node):
        """This function is intended to be for the GUI where it can
        call the static instance of the class directly to generate
        the appropriate parameter modifier for the node in XMARTe2.
        """
        app_def = mainpanel_instance.parent.API.getServiceByName('ApplicationDefinition')
        datasource = app_def.configuration['misc']['gamsources'][0]
        addInputSignalsSection(mainpanel_instance, node, False, samples=True, lims=True)

        addOutputSignalsSection(mainpanel_instance, node, 3, False, datasource=datasource)

        addLineEdit(mainpanel_instance, node, "Begin Cycle Number: ", 'begincyclenumber', 3, 0)

        addComboEdit(mainpanel_instance, node, "State Change Reset Name: ",
                     'statechangeresetname', 3, 2, ['All','0'])


def initialize(factory, plugin_datastore) -> None:
    ''' Initialize the object with the factory '''
    factory.registerBlock("HistogramGAM", HistogramGAM, plugin_datastore)
