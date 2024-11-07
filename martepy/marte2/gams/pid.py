''' Pythonic representation of the PID GAM'''

from martepy.marte2.gam import MARTe2GAM
from martepy.marte2.qt_functions import (addInputSignalsSection,
                                         addOutputSignalsSection,
                                         addLineEdit)

class PIDGAM(MARTe2GAM):
    ''' Pythonic representation of the PID GAM'''
    def __init__(self,
                    configuration_name: str = 'PID',
                    input_signals: list = [],
                    output_signals: list = [],
                    kp = 0.0,
                    ki = 0.0,
                    kd = 0.0,
                    samplefrequency = 1.0,
                    maxoutput = 1.0,
                    minoutput = 0.0
                ):
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'PIDGAM',
                input_signals = input_signals,
                output_signals = output_signals,
            )
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.samplefrequency = samplefrequency
        self.maxoutput = maxoutput
        self.minoutput = minoutput

    def writeGamConfig(self, config_writer):
        ''' Write our GAM Configuration '''
        config_writer.writeNode("kp",self.kp)
        config_writer.writeNode("ki",self.ki)
        config_writer.writeNode("kd",self.kd)
        config_writer.writeNode("sampleFrequency",self.samplefrequency)
        config_writer.writeNode("maxOutput",self.maxoutput)
        config_writer.writeNode("minOutput",self.minoutput)

    def serialize(self):
        ''' Serialize the object '''
        res = super().serialize()
        res['parameters']['kp'] = self.kp
        res['parameters']['ki'] = self.ki
        res['parameters']['kd'] = self.kd
        res['parameters']['samplefrequency'] = self.samplefrequency
        res['parameters']['maxoutput'] = self.maxoutput
        res['parameters']['minoutput'] = self.minoutput
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True) -> bool:
        ''' Deserialize the given object to the class instance '''
        super().deserialize(data, hashmap, restore_id)
        # Now we build up
        self.kp = data['parameters']["kp"]
        self.ki = data['parameters']["ki"]
        self.kd = data['parameters']["kd"]
        self.samplefrequency = data['parameters']["samplefrequency"]
        self.maxoutput = data['parameters']["maxoutput"]
        self.minoutput = data['parameters']["minoutput"]
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

        addLineEdit(mainpanel_instance, node, "Kp: ", 'kp', 3, 0)

        addLineEdit(mainpanel_instance, node, "Ki: ", 'ki', 3, 2)

        addLineEdit(mainpanel_instance, node, "Kd: ", 'kd', 4, 0)

        addLineEdit(mainpanel_instance, node, "Sample Frequency: ", 'samplefrequency', 4, 2)

        addLineEdit(mainpanel_instance, node, "Max Output: ", 'maxoutput', 5, 0)

        addLineEdit(mainpanel_instance, node, "Min Output: ", 'minoutput', 5, 2)

def initialize(factory, plugin_datastore) -> None:
    ''' Initialize the object with the factory '''
    factory.registerBlock("PIDGAM", PIDGAM, plugin_datastore)
