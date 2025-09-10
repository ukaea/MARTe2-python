''' Pythonic representative class of the File Writer Datasource ''' 
from martepy.marte2.datasource import MARTe2DataSource


from martepy.marte2.qt_functions import addComboEdit, addLineEdit, addInputSignalsSection

class FileWriter(MARTe2DataSource):
    ''' Pythonic representation of the File Writer object '''
    def __init__(self,
                    configuration_name: str = 'FileWriter',
                    input_signals = [],
                    output_signals = [],
                    number_of_buffers: int = 100000,
                    cpu_mask: int = 0xFFFFFFFF,
                    stack_size: int = 100000000,
                    file_name: str = '',
                    overwrite: str = 'yes',
                    file_format: str = 'csv',
                    csv_separator: str = ',',
                    store_on_trigger: bool = False,
                    refreshcontent = 0,
                    numpretriggers = 0,
                    numposttriggers = 0
                ):
        if output_signals:
            raise TypeError('''FileWriter does not accept any
 output signals but output signals were given''')
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'FileDataSource::FileWriter',
                input_signals = input_signals,
            )
        self.numberofbuffers = number_of_buffers
        self.cpumask = cpu_mask
        self.stacksize = stack_size
        self.filename = file_name
        self.overwrite = overwrite
        self.fileformat = file_format
        self.csvseparator = csv_separator
        self.storeontrigger = store_on_trigger
        self.refreshcontent = refreshcontent
        self.numberofpretriggers = numpretriggers
        self.numberofposttriggers = numposttriggers

    def writeDatasourceConfig(self, config_writer):
        ''' Write our datasource configuration '''
        def toIntString(string_val):
            return f'{int(string_val)}'
        config_writer.writeNode('NumberOfBuffers', toIntString(self.numberofbuffers))
        if isinstance(self.cpumask, str):
            if 'x' in self.cpumask:
                config_writer.writeNode('CPUMask', self.cpumask)
            else:
                config_writer.writeNode('CPUMask', hex(int(self.cpumask)))
        else:
            config_writer.writeNode('CPUMask', hex(self.cpumask))
        config_writer.writeNode('StackSize', toIntString(self.stacksize))
        config_writer.writeNode('Filename', f'"{self.filename}"')
        if isinstance(self.overwrite, str):
            if self.overwrite in ('yes', '1'):
                overwrite = 'yes'
            else:
                overwrite = 'no'
        else:
            overwrite = 'yes' if self.overwrite else 'no'
        config_writer.writeNode('Overwrite', f'"{overwrite}"')
        config_writer.writeNode('FileFormat', f'"{self.fileformat}"')
        if self.fileformat == 'csv':
            config_writer.writeNode('CSVSeparator', f'"{self.csvseparator}"')
        config_writer.writeNode('StoreOnTrigger', toIntString(self.storeontrigger))
        config_writer.writeNode('RefreshContent', toIntString(self.refreshcontent))
        config_writer.writeNode('NumberOfPreTriggers', toIntString(self.numberofpretriggers))
        config_writer.writeNode('NumberOfPostTriggers', toIntString(self.numberofposttriggers))
        self.writeInputSignals(config_writer, section_name='Signals')

    def serialize(self):
        ''' Serialize our object '''
        res: dict = super().serialize()
        res['parameters']['numberofbuffers'] = self.numberofbuffers
        res['parameters']['cpumask'] = self.cpumask
        res['parameters']['stacksize'] = self.stacksize
        res['parameters']['storeontrigger'] = self.storeontrigger
        res['parameters']['refreshcontent'] = self.refreshcontent
        res['parameters']['numberofpretriggers'] = self.numberofpretriggers
        res['parameters']['numberofposttriggers'] = self.numberofposttriggers
        res['parameters']['filename'] = self.filename
        res['parameters']['overwrite'] = self.overwrite
        res['parameters']['fileformat'] = self.fileformat
        res['parameters']['csvseparator'] = self.csvseparator
        res['label'] = "FileWriter"
        res['block_type'] = 'FileWriter'
        res['class_name'] = 'FileWriter'
        res['title'] = f"{self.configuration_name} (FileWriter)"
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True) -> bool:
        ''' Deserialize the object to our class instance '''
        res: bool = super().deserialize(data, hashmap, restore_id)
        self.numberofbuffers = data['parameters']["numberofbuffers"]
        self.cpumask = data['parameters']["cpumask"]
        self.stacksize = data['parameters']["stacksize"]
        self.filename = data['parameters']["filename"]
        self.overwrite = data['parameters']["overwrite"]
        self.fileformat = data['parameters']["fileformat"]
        self.csvseparator = data['parameters']["csvseparator"]
        self.storeontrigger = data['parameters']["storeontrigger"]
        self.refreshcontent = data['parameters']["refreshcontent"]
        self.numberofpretriggers = data['parameters']["numberofpretriggers"]
        self.numberofposttriggers = data['parameters']["numberofposttriggers"]
        return res

    @staticmethod
    def loadParameters(mainpanel_instance, node):
        """This function is intended to be for the GUI where it can
        call the static instance of the class directly to generate
        the appropriate parameter modifier for the node in XMARTe2.
        """
        addInputSignalsSection(mainpanel_instance, node, False, datasource=node.configuration_name)

        addLineEdit(mainpanel_instance, node, "File name: ", 'filename', 2, 0)

        addComboEdit(mainpanel_instance, node, "File format: ",
                     'fileformat', 2, 2, ['CSV', 'Binary'])

        addLineEdit(mainpanel_instance, node, "Separator: ", 'csvseparator', 3, 0)

        addComboEdit(mainpanel_instance, node, "Overwrite: ", 'overwrite', 3, 2, ['Yes', 'No'])

        addComboEdit(mainpanel_instance, node, "Refresh Content: ",
                     'refreshcontent', 4, 0, ['1', '0'])

        if isinstance(node.parameters['cpumask'], str):
            if 'x' in node.parameters['cpumask']:
                node.parameters['cpumask'] = node.parameters['cpumask']
            else:
                node.parameters['cpumask'] = hex(int(node.parameters['cpumask']))
        else:
            node.parameters['cpumask'] = hex(node.parameters['cpumask'])

        addLineEdit(mainpanel_instance, node, "CPU Mask: ", 'cpumask', 4, 2)

        addLineEdit(mainpanel_instance, node, "Stack Size: ", 'stacksize', 5, 0)

        addComboEdit(mainpanel_instance, node, "Store on Trigger: ",
                     'storeontrigger', 5, 2, ['1', '0'])

        addLineEdit(mainpanel_instance, node, "Number of Buffers: ", 'numberofbuffers', 6, 0)

        addLineEdit(mainpanel_instance, node, "Number of Pretriggers: ",
                    'numberofpretriggers', 6, 2)

        addLineEdit(mainpanel_instance, node, "Number of Post Triggers: ",
                    'numberofposttriggers', 7, 0)


def initialize(factory, plugin_datastore) -> None:
    ''' Initialize the object with the factory '''
    factory.registerBlock("FileDataSource::FileWriter", FileWriter, plugin_datastore)
    factory.registerBlock("FileWriter", FileWriter, plugin_datastore)
