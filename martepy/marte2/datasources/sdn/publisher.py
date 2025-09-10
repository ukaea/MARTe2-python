''' Pythonic representation of the SDN Publisher '''
from martepy.marte2.datasource import MARTe2DataSource
from martepy.marte2.qt_functions import addLineEdit, addInputSignalsSection

class SDNPublisher(MARTe2DataSource):
    ''' Pythonic representation of the SDN Publisher '''
    def __init__(self,
                    configuration_name: str = 'SDNPublisher',
                    input_signals = [],
                    topic: str = 'name',
                    interface: str = 'name',
                    address: str = '',
                    network_byte_order: int = 1,
                    source_port = '',
                ):
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'SDNPublisher',
                input_signals = input_signals,
            )
        self.topic = topic
        self.interface = interface
        self.port = source_port
        self.address = address
        self.byte_order = network_byte_order

    def writeDatasourceConfig(self, config_writer):
        ''' Write the datasource configuration '''
        config_writer.writeNode('Topic', f'{self.topic}')
        config_writer.writeNode('Interface', f'{self.interface}')
        config_writer.writeNode('NetworkByteOrder', f'{self.byte_order}')
        if self.address != '':
            config_writer.writeNode('Address', f'{self.address}')
        if self.port != '':
            config_writer.writeNode('SourcePort', f'{self.port}')
        self.writeInputSignals(config_writer, section_name='Signals')

    def serialize(self):
        ''' Serialize the object '''
        res: dict = super().serialize()
        res['parameters']['topic'] = self.topic
        res['parameters']['interface'] = self.interface
        res['parameters']['address'] = self.address
        res['parameters']['port'] = self.port
        res['parameters']['byte_order'] = self.byte_order
        res['label'] = "SDNPublisher"
        res['block_type'] = 'SDNPublisher'
        res['class_name'] = 'SDNPublisher'
        res['title'] = f"{self.configuration_name} (SDNPublisher)"
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True) -> bool:
        ''' Deserialize the object '''
        res = super().deserialize(data, hashmap, restore_id)
        self.topic = data['parameters']["topic"]
        self.interface = data['parameters']["interface"]
        self.byte_order = data['parameters']["byte_order"]
        self.address = data['parameters']["address"]
        self.port = data['parameters']["port"]
        return res

    @staticmethod
    def loadParameters(mainpanel_instance, node):
        """This function is intended to be for the GUI where it can call
        the static instance of the class directly to generate
        the appropriate parameter modifier for the node in XMARTe2.
        """
        addInputSignalsSection(mainpanel_instance,node, False, datasource=node.configuration_name)

        addLineEdit(mainpanel_instance,node,"Topic name: ", 'topic', 2, 0)

        addLineEdit(mainpanel_instance,node,"Interface: ", 'interface', 2, 2)

        addLineEdit(mainpanel_instance,node,"Address: ", 'address', 3, 0)

        addLineEdit(mainpanel_instance,node,"Source Port: ", 'port', 3, 2)

        addLineEdit(mainpanel_instance,node,"Network Byte Order: ", 'byte_order', 4, 0)


def initialize(factory, plugin_datastore) -> None:
    ''' Initialize the object with the factory '''
    factory.registerBlock("SDNPublisher", SDNPublisher, plugin_datastore)
