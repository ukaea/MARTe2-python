import pytest

from martepy.marte2.datasources import UDPSender
from martepy.marte2.datasources.udp.sender import initialize
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget, QComboBox

from ...utilities import *

@pytest.mark.parametrize(
    "address, configuration_name, cpumask, executionmode, numberofposttriggers, numberofpretriggers, port, stacksize, input_signals",
    [
        ("192.197.378.192", "dummyvalue", 1, "RealTimeThread", 0, 1, "4001", 1585,[('Constant',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})]),
        ("254.687.979.08", "dummyvalue1", 0x66, "IndependentThread", 40, 364, "76376", "89387",[('Hello',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}}),('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float64','Alias':'HW'}})]),
        ("localhost", "dummyvalue2", "0x98", "RealTimeThread", "30", "2001", 92183,"1024",[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3}})]),
        ("127.0.0.1", "dummyvalue2", "87", "IndependentThread", "0", 5754,"937897", 256,[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3,'NumberOfDimensions':'1'}})])
    ]
)
def test_UDPSender(address, configuration_name, cpumask, executionmode, numberofposttriggers, numberofpretriggers, port, stacksize, input_signals, load_parameters):
    setup_writer = marteconfig.StringConfigWriter()
    example_udpsender = UDPSender(address=address, configuration_name=configuration_name, cpumask=cpumask, executionmode=executionmode, numberofposttriggers=numberofposttriggers, numberofpretriggers=numberofpretriggers, port=port, stacksize=stacksize, input_signals=input_signals)
    
    # Assert attributes
    assert example_udpsender.address == address
    assert example_udpsender.configuration_name == configuration_name
    assert example_udpsender.cpumask == cpumask
    assert example_udpsender.executionmode == executionmode
    assert example_udpsender.numberofposttriggers == numberofposttriggers
    assert example_udpsender.numberofpretriggers == numberofpretriggers
    assert example_udpsender.port == port
    assert example_udpsender.stacksize == stacksize
    assert example_udpsender.input_signals == input_signals

    # Assert Serializations
    assert example_udpsender.serialize()['parameters']['address'] == address
    assert example_udpsender.serialize()['configuration_name'] == configuration_name
    assert example_udpsender.serialize()['parameters']['cpumask'] == cpumask
    assert example_udpsender.serialize()['parameters']['executionmode'] == executionmode
    assert example_udpsender.serialize()['parameters']['numberofposttriggers'] == numberofposttriggers
    assert example_udpsender.serialize()['parameters']['numberofpretriggers'] == numberofpretriggers
    assert example_udpsender.serialize()['parameters']['port'] == port
    assert example_udpsender.serialize()['parameters']['stacksize'] == stacksize

    # Assert Deserialization
    new_udpsender = UDPSender().deserialize(example_udpsender.serialize())
    assert new_udpsender.address == address
    assert new_udpsender.configuration_name.lstrip('+') == configuration_name
    assert new_udpsender.cpumask == cpumask
    assert new_udpsender.executionmode == executionmode
    assert new_udpsender.numberofposttriggers == numberofposttriggers
    assert new_udpsender.numberofpretriggers == numberofpretriggers
    assert new_udpsender.port == port
    assert new_udpsender.stacksize == stacksize
    assert new_udpsender.input_signals == input_signals

    # Assert config written
    example_udpsender.write(setup_writer)

    cpu_mask = cpumask
    if isinstance(cpu_mask, str):
        if 'x' in cpu_mask:
            cpu_mask = cpu_mask
        else:
            cpu_mask =  hex(int(cpu_mask))
    else:
        cpu_mask = hex(cpu_mask)

    test_writer = write_datasource_signals_section(input_signals)

    assert str(setup_writer) == f'''+{configuration_name} = {{
    Class = UDPDrv::UDPSender
    Port = {port}
    Address = "{address}"
    ExecutionMode = {executionmode}
    NumberOfPreTriggers = {numberofpretriggers}
    NumberOfPostTriggers = {numberofposttriggers}
    CPUMask = {cpu_mask}
    StackSize = {stacksize}
{str(test_writer)}\n}}'''

    example_udpsender.loadParameters(load_parameters, GAMNode(example_udpsender))

    classes = [QLabel, QLineEdit, QPushButton, QLabel, QLineEdit, QLabel, QLineEdit, QLabel, QComboBox, QLabel,
           QLineEdit, QLabel, QLineEdit, QLabel, QLineEdit, QLabel, QLineEdit]
    default_text = ['Number of input signals: ', str(len(input_signals)), 'Configure Signals', 'Port: ', str(port), 'Address: ', address,
                'Execution Mode: ', False, 'Number of Pretriggers: ', str(numberofpretriggers), 'Number of Posttriggers: ', str(numberofposttriggers),
                'CPU Mask: ', cpu_mask, 'Stack Size: ', str(stacksize)]
    assert len(load_parameters.configbarBox) == len(classes)
    for i in range(len(classes)):
        assert load_parameters.configbarBox.itemAt(i).widget().__class__ == classes[i]
        if not(classes[i] == QWidget or classes[i] == QComboBox):
            assert load_parameters.configbarBox.itemAt(i).widget().text() == default_text[i]

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('UDPSender') == UDPSender
