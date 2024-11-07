import pytest

from martepy.marte2.datasources import EPICSPublisher
from martepy.marte2.datasources.epics.publisher import initialize
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget, QComboBox

from ...utilities import *

@pytest.mark.parametrize(
    "configuration_name, cpus, dbr64castdouble, ignorebufferoverrun, numberofbuffers, stacksize, input_signals",
    [
        ("dummyvalue", 8, "yes", 1, 10, 1048576,[('Constant',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})]),
        ("dummyvalue1", 0xff, "yes", 0, 24, 1048576,[('Hello',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}}),('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float64','Alias':'HW'}})]),
        ("dummyvalue2", "65", "no", 1, 100, 5126,[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3}})]),
        ("dummyvalue2", "0xff", "no", 0, 512, 1024,[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3,'NumberOfDimensions':'1'}})])
    ]
)
def test_EPICSPublisher(configuration_name, cpus, dbr64castdouble, ignorebufferoverrun, numberofbuffers, stacksize, input_signals, load_parameters):
    setup_writer = marteconfig.StringConfigWriter()
    example_epicspublisher = EPICSPublisher(configuration_name=configuration_name, CPUs=cpus, DBR64CastDouble=dbr64castdouble, IgnoreBufferOverrun=ignorebufferoverrun, NumberOfBuffers=numberofbuffers, StackSize=stacksize, input_signals=input_signals)
    
    # Assert attributes
    assert example_epicspublisher.configuration_name == configuration_name
    assert example_epicspublisher.cpus == cpus
    assert example_epicspublisher.dbr64castdouble == dbr64castdouble
    assert example_epicspublisher.ignorebufferoverrun == ignorebufferoverrun
    assert example_epicspublisher.numberofbuffers == numberofbuffers
    assert example_epicspublisher.stacksize == stacksize
    assert example_epicspublisher.input_signals == input_signals

    # Assert Serializations
    assert example_epicspublisher.serialize()['configuration_name'] == configuration_name
    assert example_epicspublisher.serialize()['parameters']['cpus'] == cpus
    assert example_epicspublisher.serialize()['parameters']['dbr64castdouble'] == dbr64castdouble
    assert example_epicspublisher.serialize()['parameters']['ignorebufferoverrun'] == ignorebufferoverrun
    assert example_epicspublisher.serialize()['parameters']['numberofbuffers'] == numberofbuffers
    assert example_epicspublisher.serialize()['parameters']['stacksize'] == stacksize

    # Assert Deserialization
    new_epicspublisher = EPICSPublisher().deserialize(example_epicspublisher.serialize())
    assert new_epicspublisher.configuration_name.lstrip('+') == configuration_name
    assert new_epicspublisher.cpus == cpus
    assert new_epicspublisher.dbr64castdouble == dbr64castdouble
    assert new_epicspublisher.ignorebufferoverrun == ignorebufferoverrun
    assert new_epicspublisher.numberofbuffers == numberofbuffers
    assert new_epicspublisher.stacksize == stacksize
    assert new_epicspublisher.input_signals == input_signals

    # Assert config written
    example_epicspublisher.write(setup_writer)
    test_writer = write_datasource_signals_section(input_signals)
    cpu_mask = cpus
    if isinstance(cpu_mask, str):
        if 'x' in cpu_mask:
            cpu_mask = cpu_mask
        else:
            cpu_mask =  hex(int(cpu_mask))
    else:
        cpu_mask = hex(cpu_mask)
    assert str(setup_writer) == f'''+{configuration_name} = {{
    Class = EPICSCA::EPICSCAOutput
    StackSize = {stacksize}
    CPUs = {cpu_mask}
    NumberOfBuffers = {numberofbuffers}
    IgnoreBufferOverrun = {ignorebufferoverrun}
    DBR64CastDouble = {dbr64castdouble}
{str(test_writer)}\n}}'''

    example_epicspublisher.loadParameters(load_parameters, GAMNode(example_epicspublisher))
    
    classes = [QLabel, QLineEdit, QPushButton, QLabel, QLineEdit, QLabel, QLineEdit, QLabel, QLineEdit, QLabel, QComboBox, QLabel, QComboBox]
    default_text = ['Number of input signals: ', str(len(input_signals)), 'Configure Signals', 'Stack Size: ', str(stacksize), 'CPU Mask: ', cpu_mask,
                    'Number of Buffers: ', str(numberofbuffers), 'Ignore Buffer Overruns?: ', str(ignorebufferoverrun), 'DBR64CastDouble: ', str(dbr64castdouble)]
    assert len(load_parameters.configbarBox) == len(classes)
    for i in range(len(classes)):
        assert load_parameters.configbarBox.itemAt(i).widget().__class__ == classes[i]
        if not(classes[i] == QWidget or classes[i] == QComboBox):
            assert load_parameters.configbarBox.itemAt(i).widget().text() == default_text[i]

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('EPICSPublisher') == EPICSPublisher
