''' Pythonic representative class of the EPICS Publisher Datasource '''
from martepy.marte2.datasource import MARTe2DataSource
from martepy.marte2.qt_functions import addComboEdit, addLineEdit, addInputSignalsSection

class EPICSPublisher(MARTe2DataSource):
    ''' Pythonic representation of the EPICS Publisher -
    using the one we have found to reliably work '''

    def __init__(self,
                    configuration_name: str = 'EPICSPublisher',
                    input_signals = [],
                    StackSize = 1048576,
                    CPUs = 0xff,
                    NumberOfBuffers=10,
                    IgnoreBufferOverrun=1,
                    DBR64CastDouble="yes",
                ):
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'EPICSCA::EPICSCAOutput',
                input_signals = input_signals,
            )
        self.stacksize = StackSize
        self.cpus = CPUs
        self.numberofbuffers = NumberOfBuffers
        self.ignorebufferoverrun = IgnoreBufferOverrun
        self.dbr64castdouble = DBR64CastDouble

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
        config_writer.writeNode('NumberOfBuffers', f'{self.numberofbuffers}')
        config_writer.writeNode('IgnoreBufferOverrun', f'{self.ignorebufferoverrun}')
        config_writer.writeNode('DBR64CastDouble', f'{self.dbr64castdouble}')
        self.writeInputSignals(config_writer, section_name='Signals')

    def serialize(self):
        ''' Serialise the EPICS Publisher configuration '''
        res: dict = super().serialize()
        res['parameters']['Class name'] = 'EPICSPublisher'
        res['parameters']['stacksize'] = self.stacksize
        res['parameters']['cpus'] = self.cpus
        res['parameters']['numberofbuffers'] = self.numberofbuffers
        res['parameters']['ignorebufferoverrun'] = self.ignorebufferoverrun
        res['parameters']['dbr64castdouble'] = self.dbr64castdouble
        # We override this as the class name reference is ugly so we just
        # want to be called EPICSPublisher in the GUI
        res['label'] = "EPICSPublisher"
        res['block_type'] = 'EPICSPublisher'
        res['class_name'] = 'EPICSPublisher'
        res['title'] = f"{self.configuration_name} (EPICSPublisher)"
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True) -> bool:
        ''' Deserialize the EPICS Publisher configuration '''
        res = super().deserialize(data, hashmap, restore_id)
        self.stacksize = data['parameters']["stacksize"]
        self.cpus = data['parameters']["cpus"]
        self.numberofbuffers = data['parameters']['numberofbuffers']
        self.ignorebufferoverrun = data['parameters']['ignorebufferoverrun']
        self.dbr64castdouble = data['parameters']['dbr64castdouble']
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
        addInputSignalsSection(mainpanel_instance, node, pack=False,
                               datasource=node.configuration_name, epics=True)

        addLineEdit(mainpanel_instance, node, "Stack Size: ", 'stacksize', 2, 0)

        if isinstance(node.parameters['cpus'], str):
            if 'x' in node.parameters['cpus']:
                node.parameters['cpus'] = node.parameters['cpus']
            else:
                node.parameters['cpus'] = hex(int(node.parameters['cpus']))
        else:
            node.parameters['cpus'] = hex(node.parameters['cpus'])

        addLineEdit(mainpanel_instance, node, "CPU Mask: ", 'cpus', 2, 2)

        addLineEdit(mainpanel_instance, node, "Number of Buffers: ", 'numberofbuffers', 3, 0)

        addComboEdit(mainpanel_instance, node, "Ignore Buffer Overruns?: ",
                     'ignorebufferoverrun', 3, 2, ['1','0'])

        addComboEdit(mainpanel_instance, node, "DBR64CastDouble: ",
                     'dbr64castdouble', 4, 0, ['yes','no'])

def initialize(factory, plugin_datastore) -> None:
    ''' Initialize our publisher with the factory '''
    factory.registerBlock("EPICSPublisher", EPICSPublisher, plugin_datastore)
    factory.registerBlock("EPICSCA::EPICSCAOutput", EPICSPublisher, plugin_datastore)
