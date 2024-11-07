''' Pythonic representative class of the GAM Datasource '''
from martepy.marte2.datasource import MARTe2DataSource


class GAMDataSource(MARTe2DataSource):
    ''' Pythonic representation of the GAMDataSource '''
    def __init__(self,
                    configuration_name: str = 'DDB',
                    input_signals = [],
                    output_signals = []
                ):
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'GAMDataSource',
            )

    def writeDatasourceConfig(self, _):
        ''' Write nothing for our GAM configuration '''

    def serialize(self):
        ''' Serialize nothing '''
        res = super().serialize()
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True) -> bool:
        ''' Deserialize nothing additional '''
        res = super().deserialize(data, hashmap, restore_id)
        return res

def initialize(factory, plugin_datastore) -> None:
    ''' Initialize our object with the factory '''
    factory.registerBlock("GAMDataSource", GAMDataSource, plugin_datastore)
