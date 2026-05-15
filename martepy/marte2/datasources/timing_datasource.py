''' Pythonic representative class of the Timing Datasource '''
from martepy.marte2.datasource import MARTe2DataSource


class TimingDataSource(MARTe2DataSource):
    ''' Pythonic representation of the Timing DataSource '''
    def __init__(self,
                    configuration_name: str = 'Timings',
                    input_signals: list = [],
                    output_signals: list = []
                ):
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'TimingDataSource'
            )

    # pylint: disable=line-too-long
    def toPython(self, app_name):
        header = "from martepy.marte2.datasources.timing_datasource import TimingDataSource\n"

        content = f"""_{self.configuration_name} = TimingDataSource('{self.configuration_name}', {self.input_signals}, {self.output_signals})

{app_name}.additional_datasources += [_{self.configuration_name}]\n\n"""

        return content, header

    def writeDatasourceConfig(self, config_writer):
        ''' Write nothing '''

    def serialize(self):
        ''' Serialize nothing - in future will probably need to have some definition '''
        res = super().serialize()
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True) -> bool:
        ''' Deserialize generic timing object '''
        res = super().deserialize(data, hashmap, restore_id)
        return res

def initialize(factory, plugin_datastore) -> None:
    ''' Initialize our object with the factory '''
    factory.registerBlock("TimingDataSource", TimingDataSource, plugin_datastore)
