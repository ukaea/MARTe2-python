''' Pythonic representation of the WaveformChirp GAM'''

from martepy.marte2.gam import MARTe2GAM
from martepy.marte2.qt_functions import (addInputSignalsSection,
                                         addOutputSignalsSection,
                                         addLineEdit)

class WaveformChirpGAM(MARTe2GAM):
    ''' Pythonic representation of the WaveformChirp GAM'''
    def __init__(self,
                    configuration_name: str = 'WaveChirp',
                    input_signals: list = [],
                    output_signals: list = [],
                    amplitude = 1.0,
                    frequency1 = 1.0,
                    frequency2 = 1.0,
                    phase = 0.0,
                    offset = 0.0,
                    starttriggertime = [],
                    stoptriggertime = []
                ):
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'WaveformGAM::WaveformChirp',
                input_signals = input_signals,
                output_signals = output_signals,
            )
        self.amplitude = amplitude
        self.frequency1 = frequency1
        self.frequency2 = frequency2
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
        config_writer.writeNode("Frequency1",self.frequency1)
        config_writer.writeNode("Frequency2",self.frequency2)
        config_writer.writeNode("Phase",self.phase)
        config_writer.writeNode("Offset",self.offset)
        validateTime("StartTriggerTime", self.starttriggertime)
        validateTime("StopTriggerTime", self.stoptriggertime)


    def write(self, config_writer):
        ''' Overwrite the writer so we can implement a time signal '''
        config_writer.startClass('+' + self.configuration_name.lstrip('+'), self.class_name)
        self.writeGamConfig(config_writer)
        if self.input_signals:
            config_writer.startSection('Time')
            self.writeSignals(self.input_signals, config_writer)
            config_writer.endSection('Time')
        if self.output_signals:
            config_writer.startSection('OutputSignals')
            self.writeSignals(self.output_signals, config_writer)
            config_writer.endSection('OutputSignals')
        config_writer.endSection('+' + self.configuration_name.lstrip('+'))

    def serialize(self):
        ''' Serialize the object '''
        res = super().serialize()
        res['parameters']['amplitude'] = self.amplitude
        res['parameters']['frequency1'] = self.frequency1
        res['parameters']['frequency2'] = self.frequency2
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
        self.frequency1 = data['parameters']["frequency1"]
        self.frequency2 = data['parameters']["frequency2"]
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

        addLineEdit(mainpanel_instance, node, "Frequency 1: ", 'frequency1', 3, 2)

        addLineEdit(mainpanel_instance, node, "Frequency 2: ", 'frequency2', 4, 0)

        addLineEdit(mainpanel_instance, node, "Phase: ", 'phase', 4, 2)

        addLineEdit(mainpanel_instance, node, "Offset: ", 'offset', 5, 0)

        validateTime('starttriggertime')
        validateTime('stoptriggertime')

        addLineEdit(mainpanel_instance, node, "Start Trigger Time: ", 'starttriggertime', 5, 2)

        addLineEdit(mainpanel_instance, node, "Stop Trigger Time: ", 'stoptriggertime', 6, 0)

def initialize(factory, plugin_datastore) -> None:
    ''' Initialize the objects with the factory '''
    factory.registerBlock("WaveformGAM::WaveformChirp", WaveformChirpGAM, plugin_datastore)
    factory.registerBlock("WaveformChirp", WaveformChirpGAM, plugin_datastore)
    factory.registerBlock("WaveformChirpGAM", WaveformChirpGAM, plugin_datastore)
