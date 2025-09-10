''' Pythonic representative class of the File Reader Datasource ''' 

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
                                         addOutputSignalsSection,
                                         addLineEdit,
                                         paraChange)

class FileReader(MARTe2DataSource):
    ''' Pythonic representation of the FileReader '''
    def __init__(self,
                    configuration_name: str = 'FileReader',
                    output_signals = [],
                    filename = "",
                    fileformat = "csv",
                    separator = ",",
                    interpolate = "no",
                    eof = "Rewind",
                    preload = "yes"
                ):
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'FileDataSource::FileReader',
                output_signals = output_signals,
            )
        self.filename = filename
        self.fileformat = fileformat
        self.csvseparator = separator
        self.interpolate = interpolate
        self.eof = eof
        self.preload = preload

    def writeDatasourceConfig(self, config_writer):
        ''' Write the datasource configuration '''
        config_writer.writeNode('Filename', f'"{self.filename}"')
        config_writer.writeNode('FileFormat', f'"{self.fileformat}"')
        config_writer.writeNode('CSVSeparator', f'"{self.csvseparator}"')
        config_writer.writeNode('Interpolate', f'"{self.interpolate}"')
        config_writer.writeNode('EOF', f'"{self.eof}"')
        config_writer.writeNode('Preload', f'"{self.preload}"')
        self.writeOutputSignals(config_writer, section_name='Signals')

    def serialize(self):
        ''' Serialize our current configuration '''
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
        ''' Deserialize the object to our class instance '''
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
        """This function is intended to be for the GUI where it can
        call the static instance of the class directly to generate
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

        addComboEdit(mainpanel_instance, node,"Interpolate: ", 'interpolate', 3, 0, ['yes', 'no'])

        addLineEdit(mainpanel_instance, node,"Separator: ",'csvseparator', 3, 2)

        addComboEdit(mainpanel_instance, node,"Preload: ", 'preload', 4, 0, ['yes', 'no'])

        addComboEdit(mainpanel_instance, node,"EOF: ", 'eof', 4, 2, ['Rewind', 'Last', 'Error'])

def initialize(factory, plugin_datastore) -> None:
    ''' Initialize the object with the factory '''
    factory.registerBlock("FileReader", FileReader, plugin_datastore)
