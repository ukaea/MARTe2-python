''' Pythonic representation of the WaveformSin GAM'''

from martepy.marte2.gam import MARTe2GAM
from martepy.marte2.qt_functions import addInputSignalsSection, addOutputSignalsSection, addLineEdit

class WaveformSinGAM(MARTe2GAM):
    ''' Pythonic representation of the WaveformSin GAM'''
    def __init__(self,
                    configuration_name: str = 'WaveSine',
                    input_signals: list = [],
                    output_signals: list = [],
                    amplitude = 1.0,
                    frequency = 1.0,
                    phase = 0.0,
                    offset = 0.0,
                    starttriggertime = [],
                    stoptriggertime = []
                ):
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'WaveformGAM::WaveformSin',
                input_signals = input_signals,
                output_signals = output_signals,
            )
        self.amplitude = amplitude
        self.frequency = frequency
        self.phase = phase
        self.offset = offset
        self.starttriggertime = starttriggertime
        self.stoptriggertime = stoptriggertime

    def writeGamConfig(self, config_writer):
        ''' Write our GAM Configuration '''
        def validateTime(name, value):
            if not (len(value) == 0 or value == '' or value == '{}'):
                if isinstance(value, list):
                    value = '{' + ' '.join([str(a) for a in value]) + '}'
                config_writer.writeNode(name,'{' + value.replace('{','').replace('}','') + '}')

        config_writer.writeNode("Amplitude",self.amplitude)
        config_writer.writeNode("Frequency",self.frequency)
        config_writer.writeNode("Phase",self.phase)
        config_writer.writeNode("Offset",self.offset)
        validateTime("StartTriggerTime", self.starttriggertime)
        validateTime("StopTriggerTime", self.stoptriggertime)

    def serialize(self):
        ''' Serialize the object '''
        res = super().serialize()
        res['parameters']['amplitude'] = self.amplitude
        res['parameters']['frequency'] = self.frequency
        res['parameters']['phase'] = self.phase
        res['parameters']['offset'] = self.offset
        res['parameters']['starttriggertime'] = self.starttriggertime
        res['parameters']['stoptriggertime'] = self.stoptriggertime
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True) -> bool:
        ''' Deserialize the given object to the class instance '''
        super().deserialize(data, hashmap, restore_id)
        # Now we build up
        self.amplitude = data['parameters']["amplitude"]
        self.frequency = data['parameters']["frequency"]
        self.phase = data['parameters']["phase"]
        self.offset = data['parameters']["offset"]
        self.starttriggertime = data['parameters']["starttriggertime"]
        self.stoptriggertime = data['parameters']["stoptriggertime"]
        return self

    @staticmethod
    def loadParameters(mainpanel_instance, node):
        """This function is intended to be for the GUI where it can
        call the static instance of the class directly to generate
        the appropriate parameter modifier for the node in XMARTe2.
        """
        def validateTime(field):
            if not (len(node.parameters[field]) == 0 or
                    node.parameters[field] == '' or
                    node.parameters[field]== '{}'):
                if isinstance(node.parameters[field], list):
                    times = [str(a) for a in node.parameters[field]]
                    node.parameters[field] = '{' + ' '.join(times) + '}'

        app_def = mainpanel_instance.parent.API.getServiceByName('ApplicationDefinition')
        datasource = app_def.configuration['misc']['gamsources'][0]
        addInputSignalsSection(mainpanel_instance, node, False)

        addOutputSignalsSection(mainpanel_instance, node, 3, False, datasource=datasource)

        addLineEdit(mainpanel_instance, node, "Amplitude: ", 'amplitude', 3, 0)

        addLineEdit(mainpanel_instance, node, "Frequency: ", 'frequency', 3, 2)

        addLineEdit(mainpanel_instance, node, "Phase: ", 'phase', 4, 0)

        addLineEdit(mainpanel_instance, node, "Offset: ", 'offset', 4, 2)

        validateTime('starttriggertime')
        validateTime('stoptriggertime')

        addLineEdit(mainpanel_instance, node, "Start Trigger Time: ", 'starttriggertime', 5, 0)

        addLineEdit(mainpanel_instance, node, "Stop Trigger Time: ", 'stoptriggertime', 5, 2)

def initialize(factory, plugin_datastore) -> None:
    ''' Initialize the objects with the factory '''
    factory.registerBlock("WaveformGAM::WaveformSin", WaveformSinGAM, plugin_datastore)
    factory.registerBlock("WaveformSin", WaveformSinGAM, plugin_datastore)
    factory.registerBlock("WaveformSinGAM", WaveformSinGAM, plugin_datastore)
