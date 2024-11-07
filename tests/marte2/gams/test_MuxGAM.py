import pytest

from martepy.marte2.gams import MuxGAM
from martepy.marte2.gams.mux import initialize
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget, QComboBox

from ...utilities import * 

@pytest.mark.parametrize(
    "configuration_name, input_signals, output_signals",
    [
        ("dummyvalue",[('Constantf',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32'}})], [('Constanti',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})]),
        ("dummyvalue1",[('Hello',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}}),('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float64','Alias':'HW'}})],[('Helloout',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint64'}}),('Worldout',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','Alias':'HW'}})]),
        ("dummyvalue2",[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3}})],[('dout',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint64','NumberOfElements':3}})]),
        ("dummyvalue2",[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3,'NumberOfDimensions':'1'}})],[('small_int',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint8','NumberOfElements':3,'NumberOfDimensions':'1'}})])
    ]
)
def test_MuxGAM(configuration_name, input_signals, output_signals, load_parameters):
    setup_writer = marteconfig.StringConfigWriter()
    example_muxgam = MuxGAM(configuration_name, input_signals=input_signals, output_signals=output_signals)
    
    # Assert attributes
    assert example_muxgam.configuration_name == configuration_name
    assert example_muxgam.input_signals == input_signals
    assert example_muxgam.output_signals == output_signals

    # Assert Serializations
    assert example_muxgam.serialize()['configuration_name'] == configuration_name
    assert example_muxgam.serialize()['inputsb'] == input_signals
    assert example_muxgam.serialize()['outputsb'] == output_signals

    # Assert Deserialization
    new_muxgam = MuxGAM().deserialize(example_muxgam.serialize())
    assert new_muxgam.configuration_name.lstrip('+') == configuration_name
    assert new_muxgam.input_signals == input_signals
    assert new_muxgam.output_signals == output_signals

    # Assert config written
    example_muxgam.write(setup_writer)
    test_writer = writeSignals_section(input_signals, output_signals)

    assert str(setup_writer) == f'+{configuration_name} = {{\n    Class = MuxGAM\n{str(test_writer)}\n}}'

    example_muxgam.loadParameters(load_parameters, GAMNode(example_muxgam))

    
    classes = [QLabel, QLineEdit, QPushButton, QLabel, QLineEdit, QPushButton]
    default_text = ['Number of input signals: ', str(len(input_signals)), 'Configure Signals', 'Number of output signals: ', str(len(output_signals)), 'Configure Signals']
    test_text = [True, True, True, True, True, True]
    assert len(load_parameters.configbarBox) == len(classes)
    for i in range(len(classes)):
        assert load_parameters.configbarBox.itemAt(i).widget().__class__ == classes[i]
        if test_text[i]:
            assert load_parameters.configbarBox.itemAt(i).widget().text() == default_text[i]

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('MuxGAM') == MuxGAM
