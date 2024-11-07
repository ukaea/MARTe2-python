import pytest

from martepy.marte2.datasources import FileReader
from martepy.marte2.datasources.files.reader import initialize
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget, QComboBox

from ...utilities import *

@pytest.mark.parametrize(
    "configuration_name, csvseparator, eof, fileformat, filename, interpolate, preload, output_signals",
    [
        ("dummyvalue", ",", "Error", "csv", "dummyvalue", "no", "yes",[('Constant',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})]),
        ("dummyvalue1", ",", "LastValue", "binary", "dummyvalue1", "yes", "yes",[('Hello',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}}),('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float64','Alias':'HW'}})]),
        ("dummyvalue2", "\\t", "Rewind", "binary", "dummyvalue2", "no", "no",[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3}})]),
        ("dummyvalue2", "\\t", "Rewind", "csv", "dummyvalue2", "yes", "no",[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3,'NumberOfDimensions':'1'}})])
    ]
)
def test_FileReader(configuration_name, csvseparator, eof, fileformat, filename, interpolate, preload, output_signals, load_parameters):
    setup_writer = marteconfig.StringConfigWriter()
    example_filereader = FileReader(configuration_name=configuration_name, separator=csvseparator, eof=eof, fileformat=fileformat, filename=filename, interpolate=interpolate, preload=preload, output_signals=output_signals)
    
    # Assert attributes
    assert example_filereader.configuration_name == configuration_name
    assert example_filereader.csvseparator == csvseparator
    assert example_filereader.eof == eof
    assert example_filereader.fileformat == fileformat
    assert example_filereader.filename == filename
    assert example_filereader.interpolate == interpolate
    assert example_filereader.preload == preload
    assert example_filereader.output_signals == output_signals

    # Assert Serializations
    assert example_filereader.serialize()['configuration_name'] == configuration_name
    assert example_filereader.serialize()['parameters']['csvseparator'] == csvseparator
    assert example_filereader.serialize()['parameters']['eof'] == eof
    assert example_filereader.serialize()['parameters']['fileformat'] == fileformat
    assert example_filereader.serialize()['parameters']['filename'] == filename
    assert example_filereader.serialize()['parameters']['interpolate'] == interpolate
    assert example_filereader.serialize()['parameters']['preload'] == preload

    # Assert Deserialization
    new_filereader = FileReader().deserialize(example_filereader.serialize())
    assert new_filereader.configuration_name.lstrip('+') == configuration_name
    assert new_filereader.csvseparator == csvseparator
    assert new_filereader.eof == eof
    assert new_filereader.fileformat == fileformat
    assert new_filereader.filename == filename
    assert new_filereader.interpolate == interpolate
    assert new_filereader.preload == preload
    assert new_filereader.output_signals == output_signals

    # Assert config written
    example_filereader.write(setup_writer)
    test_writer = write_datasource_signals_section(output_signals)

    assert str(setup_writer) == f'''+{configuration_name} = {{
    Class = FileDataSource::FileReader
    Filename = "{filename}"
    FileFormat = "{fileformat}"
    CSVSeparator = "{csvseparator}"
    Interpolate = "{interpolate}"
    EOF = "{eof}"
    Preload = "{preload}"
{str(test_writer)}\n}}'''

    example_filereader.loadParameters(load_parameters, GAMNode(example_filereader))

    classes = [QLabel, QLineEdit, QPushButton, QWidget, QLabel, QWidget, QLabel, QComboBox, QLabel, QComboBox, QLabel, QLineEdit, QLabel, QComboBox, QLabel, QComboBox]
    default_text = ['Number of output signals: ', str(len(output_signals)), 'Configure Signals', False, 'File name: ', False, 'File format: ', False, 'Interpolate: ', False, 'Separator: ', csvseparator, 'Preload: ', False, 'EOF: ', False]
    assert len(load_parameters.configbarBox) == len(classes)
    for i in range(len(classes)):
        assert load_parameters.configbarBox.itemAt(i).widget().__class__ == classes[i]
        if not(classes[i] == QWidget or classes[i] == QComboBox):
            assert load_parameters.configbarBox.itemAt(i).widget().text() == default_text[i]

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('FileReader') == FileReader
