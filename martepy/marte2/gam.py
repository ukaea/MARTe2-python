''' This module provides the base representation class for a MARTe2 python GAM '''
import copy

from martepy.marte2.config_object import MARTe2ConfigObject

class MARTe2GAM(MARTe2ConfigObject):
    """Object for configuring GAMs for MARTe2RealTimeThread instances"""
    plugin = "marte2"

    def __init__(self,
                    configuration_name: str = '+gam',
                    class_name: str = 'GAM',
                    input_signals: list = [],
                    output_signals: list = []
                ):
        super().__init__()
        self.configuration_name = configuration_name
        self.class_name = class_name
        self.input_signals = input_signals
        self.output_signals = output_signals

    @property
    def inputs(self):
        ''' Return the input signals as a fixed inputs attr '''
        return self.input_signals

    @property
    def outputs(self):
        ''' Return the output signals as a fixed outputs attr '''
        return self.output_signals


    def writeGamConfig(self, config_writer):
        ''' Write the GAM specific parameters '''
        raise NotImplementedError()

    def write(self, config_writer):
        ''' Write the total GAM configuration '''
        config_writer.startClass('+' + self.configuration_name.lstrip('+'), self.class_name)
        self.writeGamConfig(config_writer)
        if self.input_signals:
            config_writer.startSection('InputSignals')
            self.writeSignals(self.input_signals, config_writer)
            config_writer.endSection('InputSignals')
        if self.output_signals:
            config_writer.startSection('OutputSignals')
            self.writeSignals(self.output_signals, config_writer)
            config_writer.endSection('OutputSignals')
        config_writer.endSection('+' + self.configuration_name.lstrip('+'))

    def isOrderingRank0(self):
        ''' Always returns false, basically used to determine whether
        the GAM should always be placed first above all others in execution
        order (True) or not (False - solve as linked as to when order of
        execution should occur: i.e. after the input signals producer '''
        return False

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
        ''' Serialize our GAM into a dictionary '''
        data = super().serialize()
        data['configuration_name'] = self.configuration_name
        data['inputsb'] = self.input_signals
        data['outputsb'] = self.output_signals
        data['class_name'] = self.class_name
        data['block_type'] = self.class_name
        data['comment'] = ''
        data['rank'] = False
        data['plugin'] = 'marte2'
        data['label'] = self.class_name
        data['parameters'] = {'Class name': self.class_name}
        data['content'] = {}
        data['inputs'] = []
        data['outputs'] = []
        data['id'] = id(self)
        data['pos_x'] = 0
        data['title'] = self.configuration_name + " (" + self.class_name + ")"
        # Need to have this match the format expected in GUI
        data['pos_y'] = 0
        return copy.deepcopy(data)

    def deserialize(self, data: dict, hashmap: dict={}, # pylint: disable=W1113, W0613, W0221
                    restore_id: bool=True) -> bool:
        ''' Deserialize our GAM object from a given dictionary '''
        super().deserialize(data, hashmap, restore_id)
        self.configuration_name = data['configuration_name']
        self.output_signals = data['outputsb']
        self.input_signals = data['inputsb']
        #self.class_name = data['class_name']
        # Now convert an input signal to what we store it as here
        # use the hidden _ versions of signals
        return self

    @staticmethod
    def loadParameters(mainpanel_instance, node):
        """This function is intended to be for the GUI where it can call
        the static instance of the class directly to generate
        the appropriate parameter modifier for the node in XMARTe2.
        """

    def runOde(self):
        ''' For future use - pythonically simulate the GAM. '''
        # inputs is the input signals in their respective order outlined in the GAM.
        class_name = self.serialize()['class_name']
        # It is shown in this format so it is the format known by a user of this file.
        msg = f"This function has not been implemented for the GAM: {class_name}"
        raise NotImplementedError(msg)
