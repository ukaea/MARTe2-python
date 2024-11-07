''' Pythonic representation of the WaveformPoints GAM'''

from martepy.marte2.gam import MARTe2GAM
from martepy.marte2.qt_functions import (addInputSignalsSection,
                                         addOutputSignalsSection,
                                         addLineEdit)

class WaveformPointsGAM(MARTe2GAM):
    ''' Pythonic representation of the WaveformPoints GAM'''
    def __init__(self,
                    configuration_name: str = 'WavePoints',
                    input_signals: list = [],
                    output_signals: list = [],
                    points = [],
                    times = [],
                    starttriggertime = [],
                    stoptriggertime = []
                ):
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'WaveformGAM::WaveformPointsDef',
                input_signals = input_signals,
                output_signals = output_signals,
            )
        self.points = points
        self.times = times
        self.starttriggertime = starttriggertime
        self.stoptriggertime = stoptriggertime

    def writeGamConfig(self, config_writer):
        ''' Write our GAM Configuration '''
        def validateTime(name, value):
            if not (len(value) == 0 or value == '' or value == '{}'):
                if isinstance(value, list):
                    value = '{' + ' '.join([str(a) for a in value]) + '}'
                config_writer.writeNode(name,'{' + value.replace('{','').replace('}','') + '}')

        if isinstance(self.points, list):
            self.points = '{' + ' '.join([str(a) for a in self.points]) + '}'
        config_writer.writeNode("Points",'{' + self.points.replace('{','').replace('}','') + '}')
        if isinstance(self.times, list):
            self.times = '{' + ' '.join([str(a) for a in self.times]) + '}'
        config_writer.writeNode("Times",'{' + self.times.replace('{','').replace('}','') + '}')
        validateTime("StartTriggerTime", self.starttriggertime)
        validateTime("StopTriggerTime", self.stoptriggertime)

    def serialize(self):
        ''' Serialize the object '''
        res = super().serialize()
        res['parameters']['points'] = self.points
        res['parameters']['times'] = self.times
        res['parameters']['starttriggertime'] = self.starttriggertime
        res['parameters']['stoptriggertime'] = self.stoptriggertime
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True) -> bool:
        ''' Deserialize the given object to the class instance '''
        super().deserialize(data, hashmap, restore_id)
        # Now we build up
        self.points = data['parameters']["points"]
        self.times = data['parameters']["times"]
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

        validateTime('points')
        validateTime('times')

        addLineEdit(mainpanel_instance, node, "Points: ", 'points', 3, 0)

        addLineEdit(mainpanel_instance, node, "Times: ", 'times', 3, 2)

        validateTime('starttriggertime')
        validateTime('stoptriggertime')

        addLineEdit(mainpanel_instance, node, "Start Trigger Time: ", 'starttriggertime', 4, 0)

        addLineEdit(mainpanel_instance, node, "Stop Trigger Time: ", 'stoptriggertime', 4, 2)

def initialize(factory, plugin_datastore) -> None:
    ''' Initialize the objects with the factory '''
    factory.registerBlock("WaveformGAM::WaveformPointsDef", WaveformPointsGAM, plugin_datastore)
    factory.registerBlock("WaveformPointsDef", WaveformPointsGAM, plugin_datastore)
    factory.registerBlock("WaveformPointsGAM", WaveformPointsGAM, plugin_datastore)
