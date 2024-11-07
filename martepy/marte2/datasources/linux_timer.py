''' Pythonic representative class of the LinuxTimer Datasource '''

import copy

from PyQt5.QtWidgets import (
    QWidget,
    QSizePolicy
)

from martepy.marte2.datasource import MARTe2DataSource
from martepy.marte2.qt_functions import addLineEdit

class LinuxTimer(MARTe2DataSource):
    ''' Pythonic representation of the LinuxTimer '''
    def __init__(self,
                    configuration_name: str = 'Timer',
                    sleep_nature: str = 'Default',
                    execution_mode: str = 'IndependentThread',
                    cpu_mask: int = 0xFFFFFFFF,
                    sleep_percentage: int = 0,
                    phase: int = 0,
                    frequency = 1000,
                    input_signals = [],
                    output_signals = []
                ):
        self.frequency = frequency
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'LinuxTimer'
            )
        self.sleep_nature = sleep_nature
        self.execution_mode = execution_mode
        self.cpu_mask = cpu_mask
        self.frequency = frequency
        self.phase = phase
        self.sleep_percentage = sleep_percentage

    def _defineBasicSignal(self, name, marte_type):
        ''' Simplification of defining the output signals '''
        return (name,{'MARTeConfig':{'Type': marte_type,
                                     'NumberOfDimensions': '1', 'NumberOfElements':'1'}})

    @property
    def output_signals(self):
        ''' Return all the possible signals always '''
        frequency_sgl = self._defineBasicSignal('Time', 'uint32')
        frequency_sgl[1]['MARTeConfig']['Frequency'] = self.frequency
        return [self._defineBasicSignal('Counter', 'uint32'),
                frequency_sgl,
                self._defineBasicSignal('AbsoluteTime', 'uint64'),
                self._defineBasicSignal('DeltaTime', 'uint64'),
                self._defineBasicSignal('TrigRephase', 'uint8')]

    @output_signals.setter
    def output_signals(self, _):
        ''' Enforce that we always have all output signals available and defined '''

    def writeDatasourceConfig(self, config_writer):
        ''' Write the configuration of our linux timer '''
        config_writer.writeNode('SleepNature', f'"{self.sleep_nature}"')
        config_writer.writeNode('ExecutionMode', f'"{self.execution_mode}"')
        if isinstance(self.cpu_mask, str):
            if 'x' in self.cpu_mask:
                config_writer.writeNode('CPUMask', self.cpu_mask)
            else:
                config_writer.writeNode('CPUMask', hex(int(self.cpu_mask)))
        else:
            config_writer.writeNode('CPUMask', hex(self.cpu_mask))
        config_writer.writeNode('Phase', f'{self.phase}')
        config_writer.writeNode('SleepPercentage', f'{self.sleep_percentage}')
        self.writeOutputSignals(config_writer, section_name='Signals')

    def serialize(self):
        ''' Serialize our timer object '''
        res = super().serialize()
        res['parameters']['sleep_nature'] = self.sleep_nature
        res['parameters']['execution_mode'] = self.execution_mode
        res['parameters']['cpu_mask'] = self.cpu_mask
        res['parameters']['frequency'] = self.frequency
        res['parameters']['sleep_percentage'] = self.sleep_percentage
        res['parameters']['phase'] = self.phase
        output_signals = []
        for output in self.output_signals:
            newoutput = copy.deepcopy(output)
            newoutput[1]['MARTeConfig']['Alias'] = newoutput[0]
            output_signals.append(newoutput)
        res['outputsb'] = output_signals
        res['outputs'] = [(0, 'Counter'),
                          (0, 'Time'),
                          (0, 'AbsoluteTime'),
                          (0, 'DeltaTime'),
                          (0, 'TrigRephase')]
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True) -> bool:
        ''' Deserilize the timer parameters '''
        super().deserialize(data, hashmap, restore_id)
        self.sleep_nature = data['parameters']["sleep_nature"]
        self.execution_mode = data['parameters']["execution_mode"]
        self.cpu_mask = data['parameters']["cpu_mask"]
        self.frequency = data['parameters']['frequency']
        # introduce backwards compatibility with versions prior to allowing user
        # configuration of sleep percentage and phase
        try:
            self.sleep_percentage = data['parameters']['sleep_percentage']
        except KeyError:
            self.sleep_percentage = 0
        try:
            self.phase = data['parameters']['phase']
        except KeyError:
            self.phase = 0
        return self

    @staticmethod
    def loadParameters(mainpanel_instance, node):
        ''' Loads the configuration panel used in the XMARTe2 GUI '''
        # Fix to make it look better
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        mainpanel_instance.configbarBox.addWidget(spacer, 0, 2)
        addLineEdit(mainpanel_instance, node, 'Frequency: ','frequency', 1, 0)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        mainpanel_instance.configbarBox.addWidget(spacer, 1, 2)


def initialize(factory, plugin_datastore) -> None:
    ''' Initialize our object with the factory '''
    factory.registerBlock("LinuxTimer", LinuxTimer, plugin_datastore)
