''' Pythonic representation of the Conversion GAM'''

from martepy.marte2.gam import MARTe2GAM
from martepy.marte2.qt_functions import addInputSignalsSection, addOutputSignalsSection

class ConversionGAM(MARTe2GAM):
    ''' Pythonic representation of the Conversion GAM'''
    def __init__(self,
                    configuration_name: str = 'Conversion',
                    input_signals: list = [],
                    output_signals: list = [],
                ):
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'ConversionGAM',
                input_signals = input_signals,
                output_signals = output_signals,
            )

    def writeGamConfig(self, _):
        ''' Nothing to write for this GAM '''


    @staticmethod
    def loadParameters(mainpanel_instance, node):
        """This function is intended to be for the GUI where it can
        call the static instance of the class directly to generate
        the appropriate parameter modifier for the node in XMARTe2.
        """
        app_def = mainpanel_instance.parent.API.getServiceByName('ApplicationDefinition')
        datasource = app_def.configuration['misc']['gamsources'][0]
        addInputSignalsSection(mainpanel_instance, node, False)

        addOutputSignalsSection(mainpanel_instance, node, 3, False, datasource=datasource)

def initialize(factory, plugin_datastore) -> None:
    ''' Initialize the object with the factory '''
    factory.registerBlock("ConversionGAM", ConversionGAM, plugin_datastore)
