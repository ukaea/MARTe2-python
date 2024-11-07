import pytest

from martepy.marte2.gams import ConversionGAM
from martepy.marte2.gams.conversion import initialize
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget

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
def test_ConversionGAM(configuration_name, input_signals, output_signals, load_parameters):
    setup_writer = marteconfig.StringConfigWriter()
    example_conversiongam = ConversionGAM(configuration_name, input_signals=input_signals,output_signals=output_signals)
    
    # Assert attributes
    assert example_conversiongam.configuration_name == configuration_name
    assert example_conversiongam.output_signals == output_signals
    assert example_conversiongam.input_signals == input_signals

    # Assert Serializations
    assert example_conversiongam.serialize()['configuration_name'] == configuration_name
    assert example_conversiongam.serialize()['outputsb'] == output_signals
    assert example_conversiongam.serialize()['inputsb'] == input_signals
    # Assert Deserialization
    new_conversiongam = ConversionGAM().deserialize(example_conversiongam.serialize())
    assert new_conversiongam.configuration_name.lstrip('+') == configuration_name
    assert new_conversiongam.output_signals == output_signals
    assert new_conversiongam.input_signals == input_signals

    # Assert config written
    example_conversiongam.write(setup_writer)
    test_writer = writeSignals_section(input_signals, output_signals)

    assert str(setup_writer) == f'+{configuration_name} = {{\n    Class = ConversionGAM\n{str(test_writer)}\n}}'

    example_conversiongam.loadParameters(load_parameters, GAMNode(example_conversiongam))

    assert len(load_parameters.configbarBox) == 6
    classes = [QLabel, QLineEdit, QPushButton, QLabel, QLineEdit, QPushButton]
    default_text = ['Number of input signals: ', str(len(example_conversiongam.input_signals)), 'Configure Signals',
                    'Number of output signals: ', str(len(example_conversiongam.output_signals)), 'Configure Signals']
    test_text = [True, True, True, True, True, True]
    for i in range(6):
        assert load_parameters.configbarBox.itemAt(i).widget().__class__ == classes[i]
        if test_text[i]:
            assert load_parameters.configbarBox.itemAt(i).widget().text() == default_text[i]

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('ConversionGAM') == ConversionGAM
