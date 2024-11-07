''' The basic config object definition from which all pythonic MARTe2 representations 
should derive. '''
import copy

import martepy.marte2.configwriting as marteconfig
from martepy.marte2.serialize import Serializable
from martepy.functions.extra_functions import normalizeSignal

class MARTe2ConfigObject(Serializable):
    """An object which will write configuration when called"""

    def __init__(self, configuration_name=''):
        super().__init__()
        self._config_writer = None
        self.configuration_name = configuration_name

    def __call__(self, config_writer=None):
        if not config_writer:
            config_writer = self._config_writer
        self.write(config_writer)

    def __str__(self):
        s = marteconfig.StringConfigWriter()
        self.write(s)
        return str(s)

    def __repr__(self):
        class_attributes = [attr for attr in dir(self) if
                            not callable(getattr(self, attr)) and not attr.startswith("__")]
        class_attributes.remove('id')
        string_content = ''
        for i in class_attributes:
            string_content += f'{i} = {getattr(self, i)}\n'
        return string_content

    def setWriter(self, config_writer):
        ''' Set the current writer '''
        self._config_writer = config_writer

    def setTab(self, tab):
        ''' Set the writers tab from within the object. '''
        if self._config_writer:
            self._config_writer.setTab(tab)
        else:
            raise TypeError('This MARTe1ConfigObject has no _config_writer')

    @staticmethod
    def writeSignals(defs, config_writer):
        """Helper function for writing out signals sections. The defs variable
        is a list of tuples of form (str, dict) where the string is a unique
        identifier for a signal and the dict should contain a key 'MARTeConfig'
        and may contain further keys with information about the signal. On
        'MARTeConfig' there should be a dict of key value pairs used to create
        leaf nodes in the signal configuration section.
        """
        for signal_name, details in defs:
            config_writer.startSection(signal_name)
            signal_details = normalizeSignal(copy.deepcopy(details))

            for key, value in signal_details['MARTeConfig'].items():
                config_writer.writeNode(key, value)
            config_writer.endSection(signal_name)

    def write(self, config_writer):
        """Write this configuration object into the provided config writer"""
        raise NotImplementedError

    def serialize(self):
        """Write this configuration object into the provided config writer"""
        return {'configuration_name': self.configuration_name}

    def deserialize(self, data, hashmap={}, restore_id=True, *args, **kwargs): # pylint: disable=W1113, W0613
        """Write this configuration object into the provided config writer"""
        self.configuration_name = data['configuration_name']
        return data
