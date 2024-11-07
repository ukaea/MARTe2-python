''' Pythonic representation of the SSM GAM'''
from martepy.marte2.gam import MARTe2GAM
from martepy.marte2.qt_functions import (addComboEdit,
                                         addInputSignalsSection,
                                         addLineEdit,
                                         addOutputSignalsSection)

class SSMGAM(MARTe2GAM):
    ''' Pythonic representation of the SSM GAM'''
    def __init__(self,
                    configuration_name: str = 'SSMGAM',
                    state_matrix = '{}',
                    input_matrix = '{}',
                    output_matrix = '{}',
                    feedthroughmatrix = '{}',
                    samplefreq = 1,
                    reset_each_state = 1,
                    input_signals: list = [],
                    output_signals: list = [],
                ):
        self.statematrix = state_matrix
        self.inputmatrix = input_matrix
        self.outputmatrix = output_matrix
        self.feedthroughmatrix = feedthroughmatrix
        self.samplefrequency = samplefreq
        self.resetineachstate = reset_each_state
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'SSMGAM',
                input_signals = input_signals,
                output_signals = output_signals,
            )

    def writeGamConfig(self, config_writer):
        ''' Write our GAM Configuration '''
        reset_state = '0' if str(self.resetineachstate) == '0' else '1'
        config_writer.writeNode('StateMatrix', f'{self.statematrix}')
        config_writer.writeNode('InputMatrix', f'{self.inputmatrix}')
        config_writer.writeNode('OutputMatrix', f'{self.outputmatrix}')
        config_writer.writeNode('FeedthroughMatrix', f'{self.feedthroughmatrix}')
        config_writer.writeNode('ResetInEachState', reset_state)
        config_writer.writeNode('SampleFrequency', f'{self.samplefrequency}')

    def serialize(self):
        ''' Serialize the object '''
        res: dict = super().serialize()
        res['parameters']['statematrix'] = self.statematrix
        res['parameters']['inputmatrix'] = self.inputmatrix
        res['parameters']['outputmatrix'] = self.outputmatrix
        res['parameters']['feedthroughmatrix'] = self.feedthroughmatrix
        res['parameters']['resetineachstate'] = int(self.resetineachstate)
        res['parameters']['samplefrequency'] = float(self.samplefrequency)
        res['label'] = "SSMGAM"
        res['block_type'] = 'SSMGAM'
        res['class_name'] = 'SSMGAM'
        res['title'] = f"{self.configuration_name} (SSMGAM)"
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True) -> bool:
        ''' Deserialize the given object to the class instance '''
        res = super().deserialize(data, hashmap, restore_id)
        self.statematrix = data['parameters']["statematrix"]
        self.inputmatrix = data['parameters']["inputmatrix"]
        self.outputmatrix = data['parameters']["outputmatrix"]
        self.feedthroughmatrix = data['parameters']["feedthroughmatrix"]
        self.resetineachstate = int(data['parameters']["resetineachstate"])
        self.samplefrequency = data['parameters']["samplefrequency"]
        return res

    @staticmethod
    def loadParameters(mainpanel_instance, node):
        """This function is intended to be for the GUI where it can
        call the static instance of the class directly to generate
        the appropriate parameter modifier for the node in XMARTe2.
        """
        app_def = mainpanel_instance.parent.API.getServiceByName('ApplicationDefinition')
        datasource = app_def.configuration['misc']['gamsources'][0]
        addInputSignalsSection(mainpanel_instance, node, False, True)

        addOutputSignalsSection(mainpanel_instance, node, 3, False, datasource, True)

        addLineEdit(mainpanel_instance, node, "StateMatrix: ", 'statematrix', 3, 0)

        addLineEdit(mainpanel_instance, node, "InputMatrix: ", 'inputmatrix', 3, 2)

        addLineEdit(mainpanel_instance, node, "OutputMatrix: ", 'outputmatrix', 4, 0)

        addLineEdit(mainpanel_instance, node, "Feed through Matrix: ", 'feedthroughmatrix', 4, 2)

        addComboEdit(mainpanel_instance, node, "Reset in each State:",
                     "resetineachstate", 5, 0, ['1', '0'])

        addLineEdit(mainpanel_instance, node, "Sample Frequency: ", 'samplefrequency', 5, 2)

def initialize(factory, plugin_datastore) -> None:
    ''' Initialize the object with the factory '''
    factory.registerBlock("SSMGAM", SSMGAM, plugin_datastore)
