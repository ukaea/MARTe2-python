''' Pythonic representation of the Filter GAM'''

from martepy.marte2.gam import MARTe2GAM
from martepy.marte2.qt_functions import (addInputSignalsSection,
                                         addOutputSignalsSection,
                                         addLineEdit,
                                         addComboEdit)

class FilterGAM(MARTe2GAM):
    ''' Pythonic representation of the Filter GAM'''
    def __init__(self,
                    configuration_name: str = 'Filter',
                    input_signals: list = [],
                    output_signals: list = [],
                    num = [],
                    den = [],
                    resetineachstate = 0,
                ):
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'FilterGAM',
                input_signals = input_signals,
                output_signals = output_signals,
            )
        self.num = num
        self.den = den
        self.resetineachstate = resetineachstate

    def writeGamConfig(self, config_writer):
        ''' Write the Filter GAM Configuration '''
        reset_state = '0' if str(self.resetineachstate) == '0' else '1'
        config_writer.writeNode("Num",'{' + self.num.replace('{','').replace('}','') + '}')
        config_writer.writeNode("Den",'{' + self.den.replace('{','').replace('}','') + '}')
        config_writer.writeNode("ResetInEachState", reset_state)

    def serialize(self):
        ''' Serialize the object '''
        res = super().serialize()
        res['parameters']['num'] = self.num
        res['parameters']['den'] = self.den
        res['parameters']['resetineachstate'] = self.resetineachstate
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True) -> bool:
        ''' Deserialize the given object to our class instance '''
        super().deserialize(data, hashmap, restore_id)
        # Now we build up
        self.resetineachstate = data['parameters']["resetineachstate"]
        self.num = data['parameters']["num"]
        self.den = data['parameters']["den"]
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

        addLineEdit(mainpanel_instance, node, "Amplitude: ", 'num', 3, 0)

        addLineEdit(mainpanel_instance, node, "Frequency: ", 'den', 3, 2)

        addComboEdit(mainpanel_instance, node, "Reset in Each State: ",
                     'resetineachstate', 4, 0, ['1','0'])

def initialize(factory, plugin_datastore) -> None:
    ''' Initialize the object with the factory '''
    factory.registerBlock("FilterGAM", FilterGAM, plugin_datastore)
