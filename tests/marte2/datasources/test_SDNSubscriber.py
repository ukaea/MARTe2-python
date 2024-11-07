import pytest

from martepy.marte2.datasources import SDNSubscriber
from martepy.marte2.datasources.sdn.subscriber import initialize
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget, QComboBox

from ...utilities import *

@pytest.mark.parametrize(
    "configuration_name, cpus, execution_mode, ignore_timeout_error, interface, internal_timeout, timeout, topic, output_signals",
    [
        ("dummyvalue", 0x46, "IndependentThread", 0, "eth0", "0", 0, "hello",[('Constant',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})]),
        ("dummyvalue1", "40", "RealTimeThread", 1, "wlan0", "-1", "50", "world",[('Hello',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}}),('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float64','Alias':'HW'}})]),
        ("dummyvalue2", "0x20", "IndependentThread", 0, "lan0", 100, "-1", "good",[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3}})]),
        ("dummyvalue2", 15, "RealTimeThread", 1,  "eth1", -1, -1, "bye",[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3,'NumberOfDimensions':'1'}})])
    ]
)
def test_SDNSubscriber(configuration_name, cpus, execution_mode, ignore_timeout_error, interface, internal_timeout, timeout, topic, output_signals, load_parameters):
    setup_writer = marteconfig.StringConfigWriter()
    example_sdnsubscriber = SDNSubscriber(configuration_name=configuration_name, cpus=cpus, execution_mode=execution_mode, ignore_timeout_error=ignore_timeout_error, interface=interface, internal_timeout=internal_timeout, timeout=timeout, topic=topic, output_signals=output_signals)
    
    # Assert attributes
    assert example_sdnsubscriber.configuration_name == configuration_name
    assert example_sdnsubscriber.cpus == cpus
    assert example_sdnsubscriber.execution_mode == execution_mode
    assert example_sdnsubscriber.ignore_timeout_error == ignore_timeout_error
    assert example_sdnsubscriber.interface == interface
    assert example_sdnsubscriber.internal_timeout == internal_timeout
    assert example_sdnsubscriber.timeout == timeout
    assert example_sdnsubscriber.topic == topic
    assert example_sdnsubscriber.output_signals == output_signals

    # Assert Serializations
    assert example_sdnsubscriber.serialize()['configuration_name'] == configuration_name
    assert example_sdnsubscriber.serialize()['parameters']['cpus'] == cpus
    assert example_sdnsubscriber.serialize()['parameters']['execution_mode'] == execution_mode
    assert example_sdnsubscriber.serialize()['parameters']['ignore_timeout_error'] == ignore_timeout_error
    assert example_sdnsubscriber.serialize()['parameters']['interface'] == interface
    assert example_sdnsubscriber.serialize()['parameters']['internal_timeout'] == internal_timeout
    assert example_sdnsubscriber.serialize()['parameters']['timeout'] == timeout
    assert example_sdnsubscriber.serialize()['parameters']['topic'] == topic

    # Assert Deserialization
    new_sdnsubscriber = SDNSubscriber().deserialize(example_sdnsubscriber.serialize())
    assert new_sdnsubscriber.configuration_name.lstrip('+') == configuration_name
    assert new_sdnsubscriber.cpus == cpus
    assert new_sdnsubscriber.execution_mode == execution_mode
    assert new_sdnsubscriber.ignore_timeout_error == ignore_timeout_error
    assert new_sdnsubscriber.interface == interface
    assert new_sdnsubscriber.internal_timeout == internal_timeout
    assert new_sdnsubscriber.timeout == timeout
    assert new_sdnsubscriber.topic == topic
    assert new_sdnsubscriber.output_signals == output_signals

    # Assert config written
    example_sdnsubscriber.write(setup_writer)
    test_writer = write_datasource_signals_section(output_signals)

    cpu_mask = cpus
    if isinstance(cpu_mask, str):
        if 'x' in cpu_mask:
            cpu_mask = cpu_mask
        else:
            cpu_mask =  hex(int(cpu_mask))
    else:
        cpu_mask = hex(cpu_mask)

    atimeout = timeout
    timeout = f'Timeout = {timeout}'
    if(execution_mode == "RealTimeThread"):
        timeout = f'InternalTimeout = {internal_timeout}'
    
    assert str(setup_writer) == f'''+{configuration_name} = {{
    Class = SDNSubscriber
    Topic = "{topic}"
    Interface = "{interface}"
    IgnoreTimeoutError = "{ignore_timeout_error}"
    ExecutionMode = "{execution_mode}"
    {timeout}
    CPUs = {cpu_mask}
{str(test_writer)}\n}}'''

    example_sdnsubscriber.loadParameters(load_parameters, GAMNode(example_sdnsubscriber))

    classes = [QLabel, QLineEdit, QPushButton, QWidget, QLabel, QLineEdit, QLabel, QLineEdit, QLabel, QComboBox, QLabel, QLineEdit, QLabel, QComboBox, QLabel, QLineEdit, QLabel, QLineEdit]
    default_text = ['Number of output signals: ', str(len(output_signals)), 'Configure Signals', False, 'Topic: ', topic, 'Interface: ', interface, 'Execution mode: ', False, 'Timeout: ', str(atimeout), 'Ignore timeout error: ', False, 'Internal timeout: ', str(internal_timeout), 'CPU mask: ', cpu_mask]
    assert len(load_parameters.configbarBox) == len(classes)
    for i in range(len(classes)):
        assert load_parameters.configbarBox.itemAt(i).widget().__class__ == classes[i]
        if not(classes[i] == QWidget or classes[i] == QComboBox):
            assert load_parameters.configbarBox.itemAt(i).widget().text() == default_text[i]

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('SDNSubscriber') == SDNSubscriber
