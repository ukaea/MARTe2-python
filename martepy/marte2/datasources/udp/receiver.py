''' Pythonic representation of the UDP Receiver '''
from martepy.marte2.datasource import MARTe2DataSource
from martepy.marte2.qt_functions import addComboEdit, addOutputSignalsSection, addLineEdit


class UDPReceiver(MARTe2DataSource):
    ''' Pythonic representation of the UDP Receiver '''
    def __init__(self,
                    configuration_name: str = 'UDPReceiver',
                    output_signals = [],
                    address: str = '',
                    interfaceaddress: str = '',
                    stacksize = 10000000,
                    executionmode: str = 'IndependentThread',
                    timeout: int = 0,
                    port: int = 40442,
                    cpu_mask: int = 0xFFFFFFFF,
                ):
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'UDP::UDPReceiver',
                output_signals = output_signals
            )
        self.executionmode = executionmode
        self.timeout = timeout
        self.port = port
        self.cpu_mask = cpu_mask
        self.address = address
        self.interfaceaddress = interfaceaddress
        self.stacksize = stacksize

    def writeDatasourceConfig(self, config_writer):
        ''' Write the datasource configuration '''
        config_writer.writeNode('ExecutionMode', f'"{self.executionmode}"')
        config_writer.writeNode('Timeout', f'{self.timeout}')
        config_writer.writeNode('Port', f'{self.port}')
        if isinstance(self.cpu_mask, str):
            if 'x' in self.cpu_mask:
                config_writer.writeNode('CPUMask', self.cpu_mask)
            else:
                config_writer.writeNode('CPUMask', hex(int(self.cpu_mask)))
        else:
            config_writer.writeNode('CPUMask', hex(self.cpu_mask))
        if self.address:
            config_writer.writeNode('Address', f'"{self.address}"')
        if self.interfaceaddress:
            config_writer.writeNode('InterfaceAddress', f'"{self.interfaceaddress}"')
        config_writer.writeNode('StackSize', f'{self.stacksize}')
        self.writeOutputSignals(config_writer, section_name='Signals')

    def serialize(self):
        ''' Serialize the object '''
        res: dict = super().serialize()
        res['parameters']['executionmode'] = self.executionmode
        res['parameters']['timeout'] = self.timeout
        res['parameters']['port'] = self.port
        res['parameters']['address'] = self.address
        res['parameters']['interfaceaddress'] = self.interfaceaddress
        res['parameters']['stacksize'] = self.stacksize
        res['parameters']['cpu_mask'] = self.cpu_mask
        res['label'] = "UDPReceiver"
        res['block_type'] = 'UDPReceiver'
        res['class_name'] = 'UDPReceiver'
        res['title'] = f"{self.configuration_name} (UDPReceiver)"
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True) -> bool:
        ''' Deserialize the object to the class instance '''
        res = super().deserialize(data, hashmap, restore_id)
        self.executionmode = data['parameters']["executionmode"]
        self.timeout = data['parameters']["timeout"]
        self.port = data['parameters']["port"]
        self.cpu_mask = data['parameters']["cpu_mask"]
        self.address = data['parameters']["address"]
        self.interfaceaddress = data['parameters']["interfaceaddress"]
        self.stacksize = data['parameters']["stacksize"]
        return res

    @staticmethod
    def loadParameters(mainpanel_instance, node):
        """This function is intended to be for the GUI where it can
        call the static instance of the class directly to generate
        the appropriate parameter modifier for the node in XMARTe2.
        """
        addOutputSignalsSection(mainpanel_instance, node)

        addLineEdit(mainpanel_instance, node, "Port: ", 'port', 2, 0)

        addLineEdit(mainpanel_instance, node, "Timeout: ", 'timeout', 2, 2)

        addLineEdit(mainpanel_instance, node, "Address: ", 'address', 3, 0)

        addLineEdit(mainpanel_instance, node, "Interface Address: ", 'interfaceaddress', 3, 2)

        addComboEdit(mainpanel_instance, node, "Execution Mode: ", 'executionmode',
                     4, 0, ['IndependentThread', 'RealTimeThread'])

        addLineEdit(mainpanel_instance, node, "Stack Size: ", 'stacksize', 4, 2)
        if isinstance(node.parameters['cpu_mask'], str):
            if 'x' in node.parameters['cpu_mask']:
                node.parameters['cpu_mask'] = node.parameters['cpu_mask']
            else:
                node.parameters['cpu_mask'] = hex(int(node.parameters['cpu_mask']))
        else:
            node.parameters['cpu_mask'] = hex(node.parameters['cpu_mask'])
        addLineEdit(mainpanel_instance, node, "CPU Mask: ", 'cpu_mask', 5, 0)


def initialize(factory, plugin_datastore) -> None:
    ''' Initialize the object with the factory '''
    factory.registerBlock("UDPReceiver", UDPReceiver, plugin_datastore)
