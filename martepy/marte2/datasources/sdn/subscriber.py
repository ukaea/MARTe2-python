''' Pythonic representation of the SDN Subscriber '''
from martepy.marte2.datasource import MARTe2DataSource
from martepy.marte2.qt_functions import addComboEdit, addLineEdit, addOutputSignalsSection

class SDNSubscriber(MARTe2DataSource):
    ''' Pythonic representation of the SDN Subscriber '''
    def __init__(self,
                    configuration_name: str = 'SDNSubscriber',
                    output_signals = [],
                    execution_mode: str = 'IndependentThread',
                    topic: str = 'name',
                    interface: str = 'name',
                    internal_timeout: int = 0,
                    timeout: int = -1,
                    cpus: int = 0xFFFFFFFF,
                    ignore_timeout_error: int = 0,
                    class_name: str = 'SDNSubscriber'
                ):
        super().__init__(
                configuration_name = configuration_name,
                class_name = class_name,
                output_signals = output_signals
            )
        self.topic = topic
        self.interface = interface
        self.execution_mode = execution_mode
        self.internal_timeout = internal_timeout
        self.timeout = timeout
        self.ignore_timeout_error = ignore_timeout_error
        self.cpus = cpus

    def writeDatasourceConfig(self, config_writer):
        ''' Write the datasource configuration '''
        config_writer.writeNode('Topic', f'"{self.topic}"')
        config_writer.writeNode('Interface', f'"{self.interface}"')
        config_writer.writeNode('IgnoreTimeoutError', f'"{int(self.ignore_timeout_error)}"')
        config_writer.writeNode('ExecutionMode', f'"{self.execution_mode}"')
        if self.execution_mode == "RealTimeThread":
            config_writer.writeNode('InternalTimeout', f'{self.internal_timeout}')
        else:
            config_writer.writeNode('Timeout', f'{self.timeout}')
        if isinstance(self.cpus, str):
            if 'x' in self.cpus:
                config_writer.writeNode('CPUs', self.cpus)
            else:
                config_writer.writeNode('CPUs', hex(int(self.cpus)))
        else:
            config_writer.writeNode('CPUs', hex(self.cpus))
        self.writeOutputSignals(config_writer, section_name='Signals')

    def serialize(self):
        ''' Serialize the configuration '''
        res: dict = super().serialize()
        res['parameters']['topic'] = self.topic
        res['parameters']['interface'] = self.interface
        res['parameters']['execution_mode'] = self.execution_mode
        res['parameters']['internal_timeout'] = self.internal_timeout
        res['parameters']['timeout'] = self.timeout
        res['parameters']['ignore_timeout_error'] = self.ignore_timeout_error
        res['parameters']['cpus'] = self.cpus
        res['label'] = "SDNSubscriber"
        res['block_type'] = 'SDNSubscriber'
        res['class_name'] = 'SDNSubscriber'
        res['title'] = f"{self.configuration_name} (SDNSubscriber)"
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True) -> bool:
        ''' Deserialize the object to our class instance '''
        res = super().deserialize(data, hashmap, restore_id)
        self.topic = data['parameters']["topic"]
        self.interface = data['parameters']["interface"]
        self.execution_mode = data['parameters']["execution_mode"]
        self.internal_timeout = data['parameters']["internal_timeout"]
        self.timeout = data['parameters']["timeout"]
        self.ignore_timeout_error = data['parameters']["ignore_timeout_error"]
        self.cpus = data['parameters']["cpus"]
        return res

    @staticmethod
    def loadParameters(mainpanel_instance, node):
        """This function is intended to be for the GUI where it can
        call the static instance of the class directly to generate
        the appropriate parameter modifier for the node in XMARTe2.
        """
        addOutputSignalsSection(mainpanel_instance, node, False)

        addLineEdit(mainpanel_instance, node,"Topic: ",'topic', 2, 0)

        addLineEdit(mainpanel_instance, node,"Interface: ",'interface', 2, 2)

        addComboEdit(mainpanel_instance, node,"Execution mode: ", 'execution_mode',
                     3, 0, ['IndependentThread', 'RealTimeThread'])

        addLineEdit(mainpanel_instance, node,"Timeout: ",'timeout', 3, 2)

        addComboEdit(mainpanel_instance, node,"Ignore timeout error: ",
                     'ignore_timeout_error', 4, 0, ['0', '1'])

        addLineEdit(mainpanel_instance, node,"Internal timeout: ",'internal_timeout', 4, 2)
        if isinstance(node.parameters['cpus'], str):
            if 'x' in node.parameters['cpus']:
                node.parameters['cpus'] = node.parameters['cpus']
            else:
                node.parameters['cpus'] = hex(int(node.parameters['cpus']))
        else:
            node.parameters['cpus'] = hex(node.parameters['cpus'])
        addLineEdit(mainpanel_instance, node,"CPU mask: ",'cpus', 5, 0)


def initialize(factory, plugin_datastore) -> None:
    ''' Initialize the object with the factory '''
    factory.registerBlock("SDNSubscriber", SDNSubscriber, plugin_datastore)
