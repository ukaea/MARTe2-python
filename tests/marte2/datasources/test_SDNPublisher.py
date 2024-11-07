import pytest

from martepy.marte2.datasources import SDNPublisher
from martepy.marte2.datasources.sdn.publisher import initialize
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget, QComboBox

from ...utilities import *

@pytest.mark.parametrize(
    "address, byte_order, configuration_name, interface, port, topic, input_signals",
    [
        ("localhost", "1", "dummyvalue", "eth0", "4000", "hello",[('Constant',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})]),
        ("127.0.0.1", 1, "dummyvalue1", "wlan0", "5762", "world",[('Hello',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}}),('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float64','Alias':'HW'}})]),
        ("215.69.18.65", "0", "dummyvalue2", "eth1", 5672, "good",[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3}})]),
        ("254.97.628.79", 0, "dummyvalue2", "lan0", 4008, "bye",[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3,'NumberOfDimensions':'1'}})])
    ]
)
def test_SDNPublisher(address, byte_order, configuration_name, interface, port, topic, input_signals, load_parameters):
    setup_writer = marteconfig.StringConfigWriter()
    example_sdnpublisher = SDNPublisher(address=address, network_byte_order=byte_order, configuration_name=configuration_name, interface=interface, source_port=port, topic=topic, input_signals=input_signals)
    
    # Assert attributes
    assert example_sdnpublisher.address == address
    assert example_sdnpublisher.byte_order == byte_order
    assert example_sdnpublisher.configuration_name == configuration_name
    assert example_sdnpublisher.interface == interface
    assert example_sdnpublisher.port == port
    assert example_sdnpublisher.topic == topic
    assert example_sdnpublisher.input_signals == input_signals

    # Assert Serializations
    assert example_sdnpublisher.serialize()['parameters']['address'] == address
    assert example_sdnpublisher.serialize()['parameters']['byte_order'] == byte_order
    assert example_sdnpublisher.serialize()['configuration_name'] == configuration_name
    assert example_sdnpublisher.serialize()['parameters']['interface'] == interface
    assert example_sdnpublisher.serialize()['parameters']['port'] == port
    assert example_sdnpublisher.serialize()['parameters']['topic'] == topic

    # Assert Deserialization
    new_sdnpublisher = SDNPublisher().deserialize(example_sdnpublisher.serialize())
    assert new_sdnpublisher.address == address
    assert new_sdnpublisher.byte_order == byte_order
    assert new_sdnpublisher.configuration_name.lstrip('+') == configuration_name
    assert new_sdnpublisher.interface == interface
    assert new_sdnpublisher.port == port
    assert new_sdnpublisher.topic == topic
    assert new_sdnpublisher.input_signals == input_signals

    # Assert config written
    example_sdnpublisher.write(setup_writer)
    test_writer = write_datasource_signals_section(input_signals)

    assert str(setup_writer) == f'''+{configuration_name} = {{
    Class = SDNPublisher
    Topic = {topic}
    Interface = {interface}
    NetworkByteOrder = {byte_order}
    Address = {address}
    SourcePort = {port}
{str(test_writer)}\n}}'''

    example_sdnpublisher.loadParameters(load_parameters, GAMNode(example_sdnpublisher))

    classes = [QLabel, QLineEdit, QPushButton, QLabel, QLineEdit, QLabel, QLineEdit, QLabel, QLineEdit, QLabel, QLineEdit, QLabel, QLineEdit]
    default_text = ['Number of input signals: ', str(len(input_signals)), 'Configure Signals', 'Topic name: ', topic, 'Interface: ', interface, 'Address: ', address, 'Source Port: ',str(port), 'Network Byte Order: ', str(byte_order)]
    assert len(load_parameters.configbarBox) == len(classes)
    for i in range(len(classes)):
        assert load_parameters.configbarBox.itemAt(i).widget().__class__ == classes[i]
        if not(classes[i] == QWidget or classes[i] == QComboBox):
            assert load_parameters.configbarBox.itemAt(i).widget().text() == default_text[i]

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('SDNPublisher') == SDNPublisher