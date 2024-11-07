import pytest

from martepy.marte2.datasources import EPICSSubscriber
from martepy.marte2.datasources.epics.subscriber import initialize
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget, QComboBox

from ...utilities import *

@pytest.mark.parametrize(
    "configuration_name, cpus, stacksize, output_signals",
    [
        ("dummyvalue", "0", 10,[('Constant',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})]),
        ("dummyvalue1", "0x86", 127836,[('Hello',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}}),('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float64','Alias':'HW'}})]),
        ("dummyvalue2", 10, "32455",[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3}})]),
        ("dummyvalue2", 0x89, "92749",[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3,'NumberOfDimensions':'1'}})])
    ]
)
def test_EPICSSubscriber(configuration_name, cpus, stacksize, output_signals, load_parameters):
    setup_writer = marteconfig.StringConfigWriter()
    example_epicssubscriber = EPICSSubscriber(configuration_name=configuration_name, CPUs=cpus, StackSize=stacksize, output_signals=output_signals)
    
    # Assert attributes
    assert example_epicssubscriber.configuration_name == configuration_name
    assert example_epicssubscriber.cpus == cpus
    assert example_epicssubscriber.stacksize == stacksize
    assert example_epicssubscriber.output_signals == output_signals

    # Assert Serializations
    assert example_epicssubscriber.serialize()['configuration_name'] == configuration_name
    assert example_epicssubscriber.serialize()['parameters']['cpus'] == cpus
    assert example_epicssubscriber.serialize()['parameters']['stacksize'] == stacksize

    # Assert Deserialization
    new_epicssubscriber = EPICSSubscriber().deserialize(example_epicssubscriber.serialize())
    assert new_epicssubscriber.configuration_name.lstrip('+') == configuration_name
    assert new_epicssubscriber.cpus == cpus
    assert new_epicssubscriber.stacksize == stacksize
    assert new_epicssubscriber.output_signals == output_signals

    # Assert config written
    example_epicssubscriber.write(setup_writer)
    test_writer = write_datasource_signals_section(output_signals)
    cpu_mask = cpus
    if isinstance(cpu_mask, str):
        if 'x' in cpu_mask:
            cpu_mask = cpu_mask
        else:
            cpu_mask =  hex(int(cpu_mask))
    else:
        cpu_mask = hex(cpu_mask)
    assert str(setup_writer) == f'''+{configuration_name} = {{
    Class = EPICSCA::EPICSCAInput
    StackSize = {stacksize}
    CPUs = {cpu_mask}
{str(test_writer)}\n}}'''

    example_epicssubscriber.loadParameters(load_parameters, GAMNode(example_epicssubscriber))
    
    classes = [QLabel, QLineEdit, QPushButton, QWidget, QLabel, QLineEdit, QLabel, QLineEdit]
    default_text = ['Number of output signals: ', str(len(output_signals)), 'Configure Signals', False, 'CPU mask: ', str(cpu_mask), 'StackSize: ', str(stacksize)]
    assert len(load_parameters.configbarBox) == len(classes)
    for i in range(len(classes)):
        assert load_parameters.configbarBox.itemAt(i).widget().__class__ == classes[i]
        if not(classes[i] == QWidget or classes[i] == QComboBox):
            assert load_parameters.configbarBox.itemAt(i).widget().text() == default_text[i]

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('EPICSSubscriber') == EPICSSubscriber
    