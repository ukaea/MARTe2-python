''' Pythonic representative class of the EPICS Subscriber Datasource '''
from martepy.marte2.datasource import MARTe2DataSource

from martepy.marte2.qt_functions import addLineEdit, addOutputSignalsSection

class EPICSSubscriber(MARTe2DataSource):
    ''' Pythonic representation of the EPICS Subscriber class '''
    def __init__(self,
                    configuration_name: str = 'EPICSSubscriber',
                    output_signals = [],
                    StackSize = 1048576,
                    CPUs = 0xff,
                ):
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'EPICSCA::EPICSCAInput',
                output_signals = output_signals,
            )
        self.stacksize = StackSize
        self.cpus = CPUs

    def writeDatasourceConfig(self, config_writer):
        ''' Write the datasource configuration '''
        config_writer.writeNode('StackSize', f'{self.stacksize}')
        if isinstance(self.cpus, str):
            if 'x' in self.cpus:
                config_writer.writeNode('CPUs', self.cpus)
            else:
                config_writer.writeNode('CPUs', hex(int(self.cpus)))
        else:
            config_writer.writeNode('CPUs', hex(self.cpus))
        self.writeOutputSignals(config_writer, section_name='Signals')

    def serialize(self):
        ''' Serialize the EPICS Subscriber'''
        res: dict = super().serialize()
        res['parameters']['stacksize'] = self.stacksize
        res['parameters']['cpus'] = self.cpus
        res['label'] = "EPICSSubscriber"
        res['block_type'] = 'EPICSSubscriber'
        res['class_name'] = 'EPICSSubscriber'
        res['title'] = f"{self.configuration_name} (EPICSSubscriber)"
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True) -> bool:
        ''' Deserialize the EPICS Subscriber '''
        res = super().deserialize(data, hashmap, restore_id)
        self.stacksize = data['parameters']["stacksize"]
        self.cpus = data['parameters']["cpus"]
        return res

    def writeSignals(self, defs, config_writer):
        """Use MARTe1ConfigObject.writeSignals but remove any DataSources."""
        omit_keys = ('DataSource','Alias')
        signals = [(
                n,
                dict(d, **{'MARTeConfig': {
                        k: v for k, v in d['MARTeConfig'].items() if k not in omit_keys
                    }})
            ) for n, d in defs]

        super().writeSignals(signals, config_writer)

    @staticmethod
    def loadParameters(mainpanel_instance, node):
        """This function is intended to be for the GUI where it can call
        the static instance of the class directly to generate
        the appropriate parameter modifier for the node in XMARTe2.
        """
        addOutputSignalsSection(mainpanel_instance, node, epics=True)

        if isinstance(node.parameters['cpus'], str):
            if 'x' in node.parameters['cpus']:
                node.parameters['cpus'] = node.parameters['cpus']
            else:
                node.parameters['cpus'] = hex(int(node.parameters['cpus']))
        else:
            node.parameters['cpus'] = hex(node.parameters['cpus'])

        addLineEdit(mainpanel_instance, node,"CPU mask: ",'cpus', 2, 0)

        addLineEdit(mainpanel_instance, node,"StackSize: ",'stacksize', 2, 2)

def initialize(factory, plugin_datastore) -> None:
    ''' Initialize the object with the factory '''
    factory.registerBlock("EPICSSubscriber", EPICSSubscriber, plugin_datastore)
    factory.registerBlock("EPICSCA::EPICSCAInput", EPICSSubscriber, plugin_datastore)
