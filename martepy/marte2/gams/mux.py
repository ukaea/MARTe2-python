''' Pythonic representation of the Mux GAM'''
from martepy.marte2.gam import MARTe2GAM
from martepy.marte2.qt_functions import addInputSignalsSection, addOutputSignalsSection

class MuxGAM(MARTe2GAM):
    ''' Pythonic representation of the Mux GAM'''
    def __init__(self,
                    configuration_name: str = 'MuxGAM',
                    input_signals: list = [],
                    output_signals: list = [],
                ):
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'MuxGAM',
                input_signals = input_signals,
                output_signals = output_signals,
            )

    def writeGamConfig(self, _):
        ''' Nothing to write for a IO GAM '''

    def serialize(self):
        ''' Serialize the object '''
        res: dict = super().serialize()
        res['label'] = "MuxGAM"
        res['block_type'] = 'MuxGAM'
        res['class_name'] = 'MuxGAM'
        res['title'] = f"{self.configuration_name} (MuxGAM)"
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True) -> bool:
        ''' Deserialize the given object to the class instance '''
        res = super().deserialize(data, hashmap, restore_id)
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


def initialize(factory, plugin_datastore) -> None:
    ''' Initialize the object with the factory '''
    factory.registerBlock("MuxGAM", MuxGAM, plugin_datastore)
