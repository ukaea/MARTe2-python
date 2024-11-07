import pytest

from martepy.marte2.datasources import FileWriter
from martepy.marte2.datasources.files.writer import initialize
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget, QComboBox

from ...utilities import *

@pytest.mark.parametrize(
    "configuration_name, cpumask, csvseparator, fileformat, filename, numberofbuffers, numberofposttriggers, numberofpretriggers, overwrite, refreshcontent, stacksize, storeontrigger, input_signals",
    [
        ("dummyvalue", 0xff, ",", "binary", "dummyvalue", 1, 0, 0, 'yes', 0, 512, True,[('Constant',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})]),
        ("dummyvalue1", "0x20", "\\t", "binary", "dummyvalue1", 5, 1, 1, "no", 1, 256, False,[('Hello',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}}),('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float64','Alias':'HW'}})]),
        ("dummyvalue2", 40, "\\t", "csv", "dummyvalue2", 256, 2, 12, "yes", 1, 256, False,[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3}})]),
        ("dummyvalue2", "1", ",", "csv", "dummyvalue2", 1024, 4, 0, "no", 0, 1024, True,[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3,'NumberOfDimensions':'1'}})])
    ]
)
def test_FileWriter(configuration_name, cpumask, csvseparator, fileformat, filename, numberofbuffers, numberofposttriggers, numberofpretriggers, overwrite, refreshcontent, stacksize, storeontrigger, input_signals, load_parameters):
    setup_writer = marteconfig.StringConfigWriter()
    example_filewriter = FileWriter(configuration_name=configuration_name, cpu_mask=cpumask, csv_separator=csvseparator, file_format=fileformat, file_name=filename, number_of_buffers=numberofbuffers, numposttriggers=numberofposttriggers, numpretriggers=numberofpretriggers, overwrite=overwrite, refreshcontent=refreshcontent, stack_size=stacksize, store_on_trigger=storeontrigger, input_signals=input_signals)
    
    # Assert attributes
    assert example_filewriter.configuration_name == configuration_name
    assert example_filewriter.cpumask == cpumask
    assert example_filewriter.csvseparator == csvseparator
    assert example_filewriter.fileformat == fileformat
    assert example_filewriter.filename == filename
    assert example_filewriter.numberofbuffers == numberofbuffers
    assert example_filewriter.numberofposttriggers == numberofposttriggers
    assert example_filewriter.numberofpretriggers == numberofpretriggers
    assert example_filewriter.overwrite == overwrite
    assert example_filewriter.refreshcontent == refreshcontent
    assert example_filewriter.stacksize == stacksize
    assert example_filewriter.storeontrigger == storeontrigger
    assert example_filewriter.input_signals == input_signals

    # Assert Serializations
    assert example_filewriter.serialize()['configuration_name'] == configuration_name
    assert example_filewriter.serialize()['parameters']['cpumask'] == cpumask
    assert example_filewriter.serialize()['parameters']['csvseparator'] == csvseparator
    assert example_filewriter.serialize()['parameters']['fileformat'] == fileformat
    assert example_filewriter.serialize()['parameters']['filename'] == filename
    assert example_filewriter.serialize()['parameters']['numberofbuffers'] == numberofbuffers
    assert example_filewriter.serialize()['parameters']['numberofposttriggers'] == numberofposttriggers
    assert example_filewriter.serialize()['parameters']['numberofpretriggers'] == numberofpretriggers
    assert example_filewriter.serialize()['parameters']['overwrite'] == overwrite
    assert example_filewriter.serialize()['parameters']['refreshcontent'] == refreshcontent
    assert example_filewriter.serialize()['parameters']['stacksize'] == stacksize
    assert example_filewriter.serialize()['parameters']['storeontrigger'] == storeontrigger

    # Assert Deserialization
    new_filewriter = FileWriter().deserialize(example_filewriter.serialize())
    assert new_filewriter.configuration_name.lstrip('+') == configuration_name
    assert new_filewriter.cpumask == cpumask
    assert new_filewriter.csvseparator == csvseparator
    assert new_filewriter.fileformat == fileformat
    assert new_filewriter.filename == filename
    assert new_filewriter.numberofbuffers == numberofbuffers
    assert new_filewriter.numberofposttriggers == numberofposttriggers
    assert new_filewriter.numberofpretriggers == numberofpretriggers
    assert new_filewriter.overwrite == overwrite
    assert new_filewriter.refreshcontent == refreshcontent
    assert new_filewriter.stacksize == stacksize
    assert new_filewriter.storeontrigger == storeontrigger
    assert new_filewriter.input_signals == input_signals

    # Assert config written
    example_filewriter.write(setup_writer)
    test_writer = write_datasource_signals_section(input_signals)
    cpu_mask = cpumask
    if isinstance(cpu_mask, str):
        if 'x' in cpu_mask:
            cpu_mask = cpu_mask
        else:
            cpu_mask =  hex(int(cpu_mask))
    else:
        cpu_mask = hex(cpu_mask)
    csvline = ''
    if fileformat == 'csv':
        csvline = f'\n    CSVSeparator = "{csvseparator}"'
    assert str(setup_writer) == f'''+{configuration_name} = {{
    Class = FileDataSource::FileWriter
    NumberOfBuffers = {numberofbuffers}
    CPUMask = {cpu_mask}
    StackSize = {stacksize}
    Filename = "{filename}"
    Overwrite = "{overwrite}"
    FileFormat = "{fileformat}"{csvline}
    StoreOnTrigger = {1 if storeontrigger else 0}
    RefreshContent = {refreshcontent}
    NumberOfPreTriggers = {numberofpretriggers}
    NumberOfPostTriggers = {numberofposttriggers}
{str(test_writer)}\n}}'''

    example_filewriter.loadParameters(load_parameters, GAMNode(example_filewriter))

    classes = [QLabel, QLineEdit, QPushButton, QLabel, QLineEdit, QLabel, QComboBox, QLabel, QLineEdit, QLabel, QComboBox, QLabel,
           QComboBox, QLabel, QLineEdit, QLabel, QLineEdit, QLabel, QComboBox, QLabel, QLineEdit, QLabel, QLineEdit, QLabel, QLineEdit]
    default_text = ['Number of input signals: ', str(len(input_signals)), 'Configure Signals', 'File name: ', filename, 'File format: ', False, 'Separator: ',
                csvseparator, 'Overwrite: ', False, 'Refresh Content: ', False, 'CPU Mask: ', cpu_mask, 'Stack Size: ', str(stacksize), 'Store on Trigger: ', False, 'Number of Buffers: ',
                str(numberofbuffers), 'Number of Pretriggers: ', str(numberofpretriggers), 'Number of Post Triggers: ', str(numberofposttriggers)]
    assert len(load_parameters.configbarBox) == len(classes)
    for i in range(len(classes)):
        assert load_parameters.configbarBox.itemAt(i).widget().__class__ == classes[i]
        if not(classes[i] == QWidget or classes[i] == QComboBox):
            assert load_parameters.configbarBox.itemAt(i).widget().text() == default_text[i]

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('FileWriter') == FileWriter
    assert factory.create('FileDataSource::FileWriter') == FileWriter
