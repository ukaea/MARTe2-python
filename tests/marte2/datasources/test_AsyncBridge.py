import pytest, pdb

from martepy.marte2.datasources import AsyncBridge
from martepy.marte2.datasources.async_bridge import initialize
from martepy.marte2.factory import Factory

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget, QComboBox

import martepy.marte2.configwriting as marteconfig

from ...utilities import *

@pytest.mark.parametrize(
    "blocking_mode, configuration_name, heapname, input, numbuffers, resetmsec_timeout, input_signals",
    [
        (0, "dummyvalue", "dummyvalue", True, 1, 0,[('Constant',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})]),
        (1, "dummyvalue1", "dummyvalue1", True, 2, -1,[('Hello',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}}),('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float64','Alias':'HW'}})]),
        (1, "dummyvalue2", "dummyvalue2", False, 2, 100,[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3}})]),
        (0, "dummyvalue2", "dummyvalue2", False, 56, -1,[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3,'NumberOfDimensions':'1'}})])
    ]
)
def test_AsyncBridge(blocking_mode, configuration_name, heapname, input, numbuffers, resetmsec_timeout, input_signals, load_parameters):
    setup_writer = marteconfig.StringConfigWriter()
    example_asyncbridge = AsyncBridge(blocking_mode=blocking_mode, configuration_name=configuration_name, heapname=heapname, inputs=input, numbuffers=numbuffers, resetmsec_timeout=resetmsec_timeout, input_signals=input_signals)
    
    # Assert attributes
    assert example_asyncbridge.blocking_mode == blocking_mode
    assert example_asyncbridge.configuration_name == configuration_name
    assert example_asyncbridge.heapname == heapname
    assert example_asyncbridge.input == input
    assert example_asyncbridge.numbuffers == numbuffers
    assert example_asyncbridge.resetmsec_timeout == resetmsec_timeout
    if input:
        assert example_asyncbridge.input_signals == input_signals
        assert example_asyncbridge.output_signals == []
    else:
        assert example_asyncbridge.output_signals == input_signals
        assert example_asyncbridge.input_signals == []

    # Assert Serializations
    assert example_asyncbridge.serialize()['parameters']['blocking_mode'] == blocking_mode
    assert example_asyncbridge.serialize()['configuration_name'] == configuration_name
    assert example_asyncbridge.serialize()['parameters']['heapname'] == heapname
    assert example_asyncbridge.serialize()['parameters']['input'] == input
    assert example_asyncbridge.serialize()['parameters']['numbuffers'] == numbuffers
    assert example_asyncbridge.serialize()['parameters']['resetmsec_timeout'] == resetmsec_timeout

    # Assert Deserialization
    new_asyncbridge = AsyncBridge().deserialize(example_asyncbridge.serialize())
    assert new_asyncbridge == example_asyncbridge
    assert new_asyncbridge.blocking_mode == blocking_mode
    assert new_asyncbridge.configuration_name.lstrip('+') == configuration_name
    assert new_asyncbridge.heapname == heapname
    assert new_asyncbridge.input == input
    assert new_asyncbridge.numbuffers == numbuffers
    assert new_asyncbridge.resetmsec_timeout == resetmsec_timeout
    if input:
        assert new_asyncbridge.input_signals == input_signals
        assert new_asyncbridge.output_signals == []
    else:
        assert new_asyncbridge.output_signals == input_signals
        assert new_asyncbridge.input_signals == []

    # Assert config written
    example_asyncbridge.write(setup_writer)
    test_writer = writeSignals_section(input_signals, [])

    assert str(setup_writer) == f'''+{configuration_name} = {{
    Class = RealTimeThreadAsyncBridge\n}}'''

    example_asyncbridge.loadParameters(load_parameters, GAMNode(example_asyncbridge))

    classes = [QLabel, QLineEdit, QWidget, QLabel, QComboBox, QLabel, QLineEdit, QLabel, QLineEdit, QLabel, QLineEdit, QLabel, QLineEdit]
    default_text = ['Number of signals: ', str(len(input_signals)), '', 'Read/Write: ', 'Read', 'Number of Buffers: ', 
                    str(numbuffers),'Heap Name: ', heapname, 'Blocking Mode: ', str(blocking_mode), 'Reset msec Timeout: ', str(resetmsec_timeout)]

    if not input:
        classes.insert(2,QPushButton)
        default_text.insert(2,"Configure Signals")

    assert len(load_parameters.configbarBox) == len(classes)
    for i in range(len(classes)):
        assert load_parameters.configbarBox.itemAt(i).widget().__class__ == classes[i]
        if not(classes[i] == QWidget or classes[i] == QComboBox):
            assert load_parameters.configbarBox.itemAt(i).widget().text() == default_text[i]
            
    inputbox = 4
    text = 'Write'
    if not input:
        inputbox = 5
        text = 'Read'
    load_parameters.configbarBox.itemAt(inputbox).widget().setCurrentText(text)
    # [a for a in range(load_parameters.configbarBox.count()) if load_parameters.configbarBox.itemAt(a).widget().__class__ == QComboBox]

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('AsyncBridge') == AsyncBridge
    assert factory.create('RealTimeThreadAsyncBridge') == AsyncBridge
