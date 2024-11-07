''' Pythonic representation of the Constant GAM '''
from martepy.marte2.gam import MARTe2GAM
from martepy.marte2.qt_functions import addOutputSignalsSection

class ConstantGAM(MARTe2GAM):
    """This block allows you to define multiple constant signals
    with multiple dimensions and elements. You can also adjust the
    constant values during runtime via messages
    """
    def __init__(self,
                    configuration_name: str = 'Constants',
                    output_signals: list = [],
                    input_signals = []
                ):
        #assert all(('Default' in d['MARTeConfig'] for n, d in output_signals))
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'ConstantGAM',
                output_signals = output_signals,
                input_signals = []
            )

    def writeGamConfig(self, _):
        ''' Write an empty configuration '''

    def serialize(self):
        ''' Serialize nothing but the base class setup '''
        res = super().serialize()
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True) -> bool:
        ''' Deserialize the object '''
        super().deserialize(data, hashmap, restore_id)
        return self

    @staticmethod
    def loadParameters(mainpanel_instance, node):
        """This function is intended to be for the GUI where it can call
        the static instance of the class directly to generate
        the appropriate parameter modifier for the node in XMARTe2.
        """
        app_def = mainpanel_instance.parent.API.getServiceByName('ApplicationDefinition')
        datasource = app_def.configuration['misc']['gamsources'][0]
        addOutputSignalsSection(mainpanel_instance, node, default=True, datasource=datasource)


def initialize(factory, plugin_datastore) -> None:
    ''' Initialize the object with the factory '''
    factory.registerBlock("ConstantGAM", ConstantGAM, plugin_datastore)
