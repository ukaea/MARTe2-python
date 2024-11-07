import pytest

from martepy.marte2.datasources import UDPReceiver
from martepy.marte2.datasources.udp.receiver import initialize
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget, QComboBox

from ...utilities import *

@pytest.mark.parametrize(
    "address, configuration_name, cpu_mask, executionmode, interfaceaddress, port, stacksize, timeout, output_signals",
    [
        ("192.197.378.192", "dummyvalue", 1, "RealTimeThread", "127.0.0.1", "4001", 1585, "0",[('Constant',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})]),
        ("254.687.979.08", "dummyvalue1", 0x66, "IndependentThread", "localhost", 364, "76376", "-1",[('Hello',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}}),('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float64','Alias':'HW'}})]),
        ("localhost", "dummyvalue2", "0x98", "RealTimeThread", "36.87.78.29", "2001", "1024", 0,[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3}})]),
        ("127.0.0.1", "dummyvalue2", "87", "IndependentThread", "273.898.87.76", 5754, 256, 10,[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3,'NumberOfDimensions':'1'}})])
    ]
)
def test_UDPReceiver(address, configuration_name, cpu_mask, executionmode, interfaceaddress, port, stacksize, timeout, output_signals, load_parameters):
    setup_writer = marteconfig.StringConfigWriter()
    example_udpreceiver = UDPReceiver(address=address, configuration_name=configuration_name, cpu_mask=cpu_mask, executionmode=executionmode, interfaceaddress=interfaceaddress, port=port, stacksize=stacksize, timeout=timeout, output_signals=output_signals)
    
    # Assert attributes
    assert example_udpreceiver.address == address
    assert example_udpreceiver.configuration_name == configuration_name
    assert example_udpreceiver.cpu_mask == cpu_mask
    assert example_udpreceiver.executionmode == executionmode
    assert example_udpreceiver.interfaceaddress == interfaceaddress
    assert example_udpreceiver.port == port
    assert example_udpreceiver.stacksize == stacksize
    assert example_udpreceiver.timeout == timeout
    assert example_udpreceiver.output_signals == output_signals

    # Assert Serializations
    assert example_udpreceiver.serialize()['parameters']['address'] == address
    assert example_udpreceiver.serialize()['configuration_name'] == configuration_name
    assert example_udpreceiver.serialize()['parameters']['cpu_mask'] == cpu_mask
    assert example_udpreceiver.serialize()['parameters']['executionmode'] == executionmode
    assert example_udpreceiver.serialize()['parameters']['interfaceaddress'] == interfaceaddress
    assert example_udpreceiver.serialize()['parameters']['port'] == port
    assert example_udpreceiver.serialize()['parameters']['stacksize'] == stacksize
    assert example_udpreceiver.serialize()['parameters']['timeout'] == timeout

    # Assert Deserialization
    new_udpreceiver = UDPReceiver().deserialize(example_udpreceiver.serialize())
    assert new_udpreceiver.address == address
    assert new_udpreceiver.configuration_name.lstrip('+') == configuration_name
    assert new_udpreceiver.cpu_mask == cpu_mask
    assert new_udpreceiver.executionmode == executionmode
    assert new_udpreceiver.interfaceaddress == interfaceaddress
    assert new_udpreceiver.port == port
    assert new_udpreceiver.stacksize == stacksize
    assert new_udpreceiver.timeout == timeout
    assert new_udpreceiver.output_signals == output_signals

    # Assert config written
    example_udpreceiver.write(setup_writer)
    test_writer = write_datasource_signals_section(output_signals)

    cpu_mask = cpu_mask
    if isinstance(cpu_mask, str):
        if 'x' in cpu_mask:
            cpu_mask = cpu_mask
        else:
            cpu_mask =  hex(int(cpu_mask))
    else:
        cpu_mask = hex(cpu_mask)

    assert str(setup_writer) == f'''+{configuration_name} = {{
    Class = UDP::UDPReceiver
    ExecutionMode = "{executionmode}"
    Timeout = {timeout}
    Port = {port}
    CPUMask = {cpu_mask}
    Address = "{address}"
    InterfaceAddress = "{interfaceaddress}"
    StackSize = {stacksize}
{str(test_writer)}\n}}'''

    example_udpreceiver.loadParameters(load_parameters, GAMNode(example_udpreceiver))

    classes = [QLabel, QLineEdit, QPushButton, QWidget, QLabel,
           QLineEdit, QLabel, QLineEdit, QLabel, QLineEdit, QLabel, QLineEdit, QLabel, QComboBox, QLabel, QLineEdit, QLabel, QLineEdit]
    default_text = ['Number of output signals: ', str(len(output_signals)), 'Configure Signals', False, 'Port: ',
                str(port), 'Timeout: ', str(timeout), 'Address: ', address, 'Interface Address: ', interfaceaddress, 'Execution Mode: ', False, 'Stack Size: ', str(stacksize),
                'CPU Mask: ', cpu_mask]
    assert len(load_parameters.configbarBox) == len(classes)
    for i in range(len(classes)):
        assert load_parameters.configbarBox.itemAt(i).widget().__class__ == classes[i]
        if not(classes[i] == QWidget or classes[i] == QComboBox):
            assert load_parameters.configbarBox.itemAt(i).widget().text() == default_text[i]

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('UDPReceiver') == UDPReceiver
