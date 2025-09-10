''' Pythonic representation of the UDP Sender '''

from martepy.marte2.datasource import MARTe2DataSource
from martepy.marte2.qt_functions import addComboEdit, addLineEdit, addInputSignalsSection

class UDPSender(MARTe2DataSource):
    ''' Pythonic representation of the UDP Sender '''
    def __init__(self,
                    configuration_name: str = 'UDPSender',
                    input_signals = [],
                    port: int = 0,
                    cpumask: int = 0xFFFFFFFF,
                    executionmode = 'IndependentThread',
                    address = '127.0.0.1',
                    numberofpretriggers = 0,
                    numberofposttriggers = 0,
                    stacksize = 10000000
                ):
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'UDP::UDPSender',
                input_signals = input_signals
            )
        self.port = port
        self.cpumask = cpumask
        self.executionmode = executionmode
        self.address = address
        self.numberofpretriggers = numberofpretriggers
        self.numberofposttriggers = numberofposttriggers
        self.stacksize = stacksize

    def writeDatasourceConfig(self, config_writer):
        ''' Write the Datasource configuration '''
        config_writer.writeNode('Port', f'{self.port}')
        config_writer.writeNode('Address', f'"{self.address}"')
        config_writer.writeNode('ExecutionMode', f'{self.executionmode}')
        config_writer.writeNode('NumberOfPreTriggers', f'{self.numberofpretriggers}')
        config_writer.writeNode('NumberOfPostTriggers', f'{self.numberofposttriggers}')
        if isinstance(self.cpumask, str):
            if 'x' in self.cpumask:
                config_writer.writeNode('CPUMask', self.cpumask)
            else:
                config_writer.writeNode('CPUMask', hex(int(self.cpumask)))
        else:
            config_writer.writeNode('CPUMask', hex(self.cpumask))
        config_writer.writeNode('StackSize', f'{self.stacksize}')
        self.writeInputSignals(config_writer, section_name='Signals')

    def serialize(self):
        ''' Serialize the object '''
        res: dict = super().serialize()
        res['parameters']['port'] = self.port
        res['parameters']['cpumask'] = self.cpumask
        res['parameters']['numberofpretriggers'] = self.numberofpretriggers
        res['parameters']['numberofposttriggers'] = self.numberofposttriggers
        res['parameters']['stacksize'] = self.stacksize
        res['parameters']['address'] = self.address
        res['parameters']['executionmode'] = self.executionmode
        res['label'] = "UDPSender"
        res['block_type'] = 'UDPSender'
        res['class_name'] = 'UDPSender'
        res['title'] = f"{self.configuration_name} (UDPSender)"
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True) -> bool:
        ''' Deserialize the object to the class instance '''
        res = super().deserialize(data, hashmap, restore_id)
        self.port = data['parameters']["port"]
        self.cpumask = data['parameters']["cpumask"]
        self.address = data['parameters']["address"]
        self.executionmode = data['parameters']["executionmode"]
        self.numberofpretriggers = data['parameters']["numberofpretriggers"]
        self.numberofposttriggers = data['parameters']["numberofposttriggers"]
        self.stacksize = data['parameters']["stacksize"]
        return res

    @staticmethod
    def loadParameters(mainpanel_instance, node):
        """This function is intended to be for the GUI where it can
        call the static instance of the class directly to generate
        the appropriate parameter modifier for the node in XMARTe2.
        """
        addInputSignalsSection(mainpanel_instance,node,False, datasource=node.configuration_name)

        addLineEdit(mainpanel_instance, node, "Port: ", 'port', 2, 0)

        addLineEdit(mainpanel_instance, node, "Address: ", 'address', 2, 2)

        addComboEdit(mainpanel_instance, node, "Execution Mode: ", 'executionmode',
                     3, 0, ['IndependentThread', 'RealTimeThread'])

        addLineEdit(mainpanel_instance, node, "Number of Pretriggers: ",
                    'numberofpretriggers', 3, 2)

        addLineEdit(mainpanel_instance, node, "Number of Posttriggers: ",
                    'numberofposttriggers', 4, 0)

        if isinstance(node.parameters['cpumask'], str):
            if 'x' in node.parameters['cpumask']:
                node.parameters['cpumask'] = node.parameters['cpumask']
            else:
                node.parameters['cpumask'] = hex(int(node.parameters['cpumask']))
        else:
            node.parameters['cpumask'] = hex(node.parameters['cpumask'])

        addLineEdit(mainpanel_instance, node, "CPU Mask: ", 'cpumask', 4, 2)

        addLineEdit(mainpanel_instance, node, "Stack Size: ", 'stacksize', 5, 0)

def initialize(factory, plugin_datastore) -> None:
    ''' Initialize the object with the factory '''
    factory.registerBlock("UDPSender", UDPSender, plugin_datastore)
