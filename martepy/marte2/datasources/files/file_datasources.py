''' Pythonic representative class of the FileReader and Writer created that flushes with each
write to ensure the data is written without breakages in columns during CSV writing Datasource '''

from functools import partial

from PyQt5.QtWidgets import (
    QPushButton,
    QWidget,
    QLineEdit,
    QLabel,
    QHBoxLayout,
    QFileDialog
)

from martepy.marte2.datasource import MARTe2DataSource
from martepy.marte2.qt_functions import (addComboEdit,
                                         addInputSignalsSection,
                                         addOutputSignalsSection,
                                         addLineEdit,
                                         paraChange)

class RFileWriter(MARTe2DataSource):
    ''' Pythonic representation of Flushing FileWriter '''
    def __init__(self,
                    configuration_name: str = 'FileWriter',
                    input_signals = [],
                    numberofbuffers: int = 100000,
                    cpumask: int = 0xFFFFFFFF,
                    stacksize: int = 100000000,
                    filename: str = None,
                    overwrite: bool = True,
                    fileformat: str = 'csv',
                    csvseparator: str = ',',
                    storeontrigger: bool = False,
                    refreshcontent = 0,
                    numberofpretriggers = 0,
                    numberofposttriggers = 0
                ):
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'RFileDataSource::FileWriter',
                input_signals = input_signals
            )
        self.numberofbuffers = numberofbuffers
        self.cpumask = cpumask
        self.stacksize = stacksize
        self.filename = filename
        self.overwrite = overwrite
        self.fileformat = fileformat
        self.csvseparator = csvseparator
        self.storeontrigger = storeontrigger
        self.refreshcontent = refreshcontent
        self.numberofpretriggers = numberofpretriggers
        self.numberofposttriggers = numberofposttriggers

    def writeDatasourceConfig(self, config_writer):
        ''' Write the datasource config '''
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
        ''' Serialize the datasource configuration '''
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
        ''' Deserialize the datasource configuration '''
        res: bool = super().deserialize(data, hashmap, restore_id)
        deserialize_props = ["numberofbuffers",
                             "cpumask",
                             "stacksize",
                             "filename",
                             "overwrite",
                             "fileformat",
                             "csvseparator",
                             "storeontrigger",
                             "refreshcontent",
                             "numberofpretriggers",
                             "numberofposttriggers"]

        self.deserializeProperties(data, deserialize_props)
        return res

    def deserializeProperties(self, data, properties):
        '''Simplifies the deserialization of a list of properties where this becomes
        long.'''
        for property_name in properties:
            if property_name in list(data['parameters'].keys()):
                setattr(self, property_name, data['parameters'][property_name])

    @staticmethod
    def loadParameters(mainpanel_instance, node):
        """This function is intended to be for the GUI where it can call
        the static instance of the class directly to generate
        the appropriate parameter modifier for the node in XMARTe2.
        """
        addInputSignalsSection(mainpanel_instance, node, False, datasource=node.configuration_name)

        addLineEdit(mainpanel_instance, node, "File name: ", 'filename', 2, 0)

        addComboEdit(mainpanel_instance, node, "File format: ", 'fileformat',
                     2, 2, ['CSV', 'Binary'])

        addLineEdit(mainpanel_instance, node, "Separator: ", 'csvseparator', 3, 0)

        addComboEdit(mainpanel_instance, node, "Overwrite: ", 'overwrite', 3, 2, ['Yes', 'No'])

        addComboEdit(mainpanel_instance, node, "Refresh Content: ", 'refreshcontent',
                     4, 0, ['1', '0'])

        if isinstance(node.parameters['cpumask'], str):
            if 'x' in node.parameters['cpumask']:
                node.parameters['cpumask'] = node.parameters['cpumask']
            else:
                node.parameters['cpumask'] = hex(int(node.parameters['cpumask']))
        else:
            node.parameters['cpumask'] = hex(node.parameters['cpumask'])

        addLineEdit(mainpanel_instance, node, "CPU Mask: ", 'cpumask', 4, 2)

        addLineEdit(mainpanel_instance, node, "Stack Size: ", 'stacksize', 5, 0)

        addComboEdit(mainpanel_instance, node, "Store on Trigger: ", 'storeontrigger',
                     5, 2, ['1', '0'])

        addLineEdit(mainpanel_instance, node, "Number of Buffers: ", 'numberofbuffers', 6, 0)

        addLineEdit(mainpanel_instance, node, "Number of Pretriggers: ",
                    'numberofpretriggers', 6, 2)

        addLineEdit(mainpanel_instance, node, "Number of Post Triggers: ",
                    'numberofposttriggers', 7, 0)


class RFileReader(MARTe2DataSource):
    ''' Pythonic representation of Flushing FileReader '''
    def __init__(self,
                    configuration_name: str = 'FileReader',
                    filename = "",
                    fileformat = "csv",
                    csvseparator = ",",
                    interpolate = "no",
                    eof = "Rewind",
                    preload = "yes",
                    input_signals = [],
                    output_signals = []
                ):
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'RFileDataSource::FileReader'
            )
        self.output_signals = output_signals
        self.filename = filename
        self.fileformat = fileformat
        self.csvseparator = csvseparator
        self.interpolate = interpolate
        self.eof = eof
        self.preload = preload

    def writeDatasourceConfig(self, config_writer):
        ''' Write our datasource configuration '''
        config_writer.writeNode('Filename', f'"{self.filename}"')
        config_writer.writeNode('FileFormat', f'"{self.fileformat}"')
        config_writer.writeNode('CSVSeparator', f'"{self.csvseparator}"')
        config_writer.writeNode('Interpolate', f'"{self.interpolate}"')
        config_writer.writeNode('EOF', f'"{self.eof}"')
        config_writer.writeNode('Preload', f'"{self.preload}"')
        self.writeOutputSignals(config_writer, section_name='Signals')

    def serialize(self):
        res: dict = super().serialize()
        res['parameters']['filename'] = self.filename
        res['parameters']['fileformat'] = self.fileformat
        res['parameters']['interpolate'] = self.interpolate
        res['parameters']['csvseparator'] = self.csvseparator
        res['parameters']['eof'] = self.eof
        res['parameters']['preload'] = self.preload

        # Override name
        res['label'] = "FileReader"
        res['block_type'] = 'FileReader'
        res['class_name'] = 'FileReader'
        res['title'] = f"{self.configuration_name} (FileReader)"
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True) -> bool:
        res = super().deserialize(data, hashmap, restore_id)
        self.filename = data['parameters']["filename"]
        self.fileformat = data['parameters']["fileformat"]
        self.interpolate = data['parameters']["interpolate"]
        self.csvseparator = data['parameters']["csvseparator"]
        self.eof = data['parameters']["eof"]
        self.preload = data['parameters']["preload"]
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
        addOutputSignalsSection(mainpanel_instance, node, False)

        # Special file input
        wgt_label = QLabel("File name: ")
        wgt_field = QWidget()
        hlay = QHBoxLayout()
        wgt_field.setLayout(hlay)
        wgt_line = QLineEdit(mainpanel_instance)
        wgt_button = QPushButton("Browse")
        hlay.addWidget(wgt_line)
        hlay.addWidget(wgt_button)
        def filedialog():
            # Open a file dialog to select a file
            file_dialog = QFileDialog()
            file_dialog.setFileMode(QFileDialog.ExistingFile)
            if file_dialog.exec_():
                file_paths = file_dialog.selectedFiles()
                if file_paths:
                    # Read the text content from the selected file
                    file_path = file_paths[0]
                    wgt_line.setText(file_path)

        wgt_button.clicked.connect(filedialog)
        wgt_line.setText(str(node.parameters['filename']))
        wgt_line.textChanged.connect(partial(paraChange, wgt_line, node, 'filename'))
        mainpanel_instance.configbarBox.addWidget(wgt_label, 2, 0)
        mainpanel_instance.configbarBox.addWidget(wgt_field, 2, 1)

        addComboEdit(mainpanel_instance, node,"File format: ", 'fileformat',
                     2, 2, ['csv', 'binary'])

        addComboEdit(mainpanel_instance, node,"Interpolate: ", 'interpolate',
                     3, 0, ['yes', 'no'])

        addLineEdit(mainpanel_instance, node,"Separator: ",'csvseparator', 3, 2)

        addComboEdit(mainpanel_instance, node,"Preload: ", 'preload', 4, 0, ['yes', 'no'])

        addComboEdit(mainpanel_instance, node,"EOF: ", 'eof', 4, 2, ['Rewind', 'Last', 'Error'])

def initialize(factory, plugin_datastore) -> None:
    ''' Initialize the objects with the factory '''
    factory.registerBlock("RFileDataSource::FileReader", RFileReader, plugin_datastore)
    factory.registerBlock("RFileReader", RFileReader, plugin_datastore)
    factory.registerBlock("RFileDataSource::FileWriter", RFileWriter, plugin_datastore)
    factory.registerBlock("RFileWriter", RFileWriter, plugin_datastore)
