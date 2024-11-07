''' Pythonic representative class of the Logger Datasource '''

from martepy.marte2.datasource import MARTe2DataSource

from martepy.marte2.qt_functions import addSignalsSection

class LoggerDataSource(MARTe2DataSource):
    ''' Pythonic representation of the Logger DataSource '''
    def __init__(self,
                    configuration_name: str = 'LoggerDataSource',
                    input_signals = [],
                    output_signals = []
                ):
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'LoggerDataSource'
            )

    def writeDatasourceConfig(self, config_writer):
        pass

    def serialize(self):
        res = super().serialize()
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True) -> bool:
        super().deserialize(data, hashmap, restore_id)
        # Now we build up
        return self

    @staticmethod
    def loadParameters(mainpanel_instance, node):
        """This function is intended to be for the GUI where it can
        call the static instance of the class directly to generate
        the appropriate parameter modifier for the node in XMARTe2.
        """
        addSignalsSection(mainpanel_instance, node, type_input=True)



def initialize(factory, plugin_datastore) -> None:
    ''' Initialize our object with the factory '''
    factory.registerBlock("LoggerDataSource", LoggerDataSource, plugin_datastore)
