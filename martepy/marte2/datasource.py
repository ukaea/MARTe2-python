''' The basic definition for a MARTe2 python datasource object '''

import logging
import copy
from martepy.marte2.config_object import MARTe2ConfigObject

logger = logging.getLogger(__name__)

class MARTe2DataSource(MARTe2ConfigObject):
    """Object for configuring GAMs for MARTe2RealTimeThread instances"""

    plugin = 'marte2_datasources'
    def __init__(self,
                    configuration_name: str = 'datasource',
                    class_name: str = 'UnknownDataSource',
                    input_signals: list = [],
                    output_signals: list = [],
                ):
        super().__init__(configuration_name=configuration_name)
        self.class_name = class_name
        self.comment = ''
        self.input_signals = list(input_signals)
        self.output_signals = list(output_signals)

    def writeDatasourceConfig(self, config_writer):
        ''' Needs implementing but how to write the datasource '''
        raise NotImplementedError()

    def writeInputSignals(self, config_writer, section_name='InputSignals'):
        ''' Write the input signals section '''
        if self.input_signals:
            config_writer.startSection(section_name)
            self.writeSignals(self.input_signals, config_writer)
            config_writer.endSection(section_name)

    def writeOutputSignals(self, config_writer, section_name='OutputSignals'):
        ''' Write the output signal section '''
        if self.output_signals:
            config_writer.startSection(section_name)
            self.writeSignals(self.output_signals, config_writer)
            config_writer.endSection(section_name)

    def write(self, config_writer):
        ''' Default method of writing the datasource - assuming you have written the
        writeDatasourceConfig '''
        config_writer.startClass('+' + self.configuration_name.strip('+'), self.class_name)
        self.writeDatasourceConfig(config_writer)
        config_writer.endSection('+' + self.configuration_name.strip('+'))

    def writeSignals(self, defs, config_writer): # pylint: disable=W0237, W0221
        """Use MARTe1ConfigObject.writeSignals but remove any DataSources."""
        super().writeSignals([(
                n,
                dict(d, **{'MARTeConfig': {
                        k: v for k, v in d['MARTeConfig'].items() if
                        k not in ('DataSource','Alias')
                    }})
            ) for n, d in defs], config_writer)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            myself = copy.deepcopy(self.serialize())
            theother = copy.deepcopy(other.serialize())
            myself['id'] = 0
            theother['id'] = 0
            if myself == theother:
                return True
        return False

    def serialize(self):
        ''' Serialize the datasource '''
        res = super().serialize()
        res['class_name'] = self.class_name
        res['configuration_name'] = self.configuration_name
        res['inputsb'] = self.input_signals
        res['outputsb'] = self.output_signals
        res['class_name'] = self.class_name
        res['block_type'] = self.class_name
        res['comment'] = self.comment
        res['rank'] = False
        res['plugin'] = 'marte2_datasources'
        res['label'] = self.class_name
        res['parameters'] = {}
        res['content'] = {}
        res['inputs'] = []
        res['outputs'] = []
        res['id'] = id(self)
        res['pos_x'] = 0
        res['title'] = self.configuration_name + "(" + self.class_name + ")"
        # Need to have this match the format expected in GUI
        res['pos_y'] = 0
        return copy.deepcopy(res)

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True) -> bool: # pylint: disable=W0221
        ''' Deserialize our object from a dictionary '''
        super().deserialize(data, hashmap, restore_id)
        #self.class_name = data['class_name']
        self.configuration_name = "+" + data['configuration_name'].strip('+')
        self.input_signals = data["inputsb"]
        self.output_signals = data["outputsb"]
        self.configuration_name = data['configuration_name']
        self.comment = data['comment']
        return self
