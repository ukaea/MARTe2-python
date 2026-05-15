''' Pythonic representative class of the GAM Datasource '''
from martepy.marte2.datasource import MARTe2DataSource


class GAMDataSource(MARTe2DataSource):
    ''' Pythonic representation of the GAMDataSource '''
    def __init__(self,
                    configuration_name: str = 'DDB',
                    input_signals: list = [],
                    output_signals: list = []
                ):
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'GAMDataSource',
            )

    # pylint: disable=line-too-long
    def toPython(self, app_name):
        header = "from martepy.marte2.datasources.gam_datasource import GAMDataSource\n"

        content = f"""_{self.configuration_name} = GAMDataSource('{self.configuration_name}', {self.input_signals}, {self.output_signals})

{app_name}.additional_datasources += [_{self.configuration_name}]\n\n"""

        return content, header

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
