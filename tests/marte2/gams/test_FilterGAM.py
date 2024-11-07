import pytest

from martepy.marte2.gams import FilterGAM
from martepy.marte2.gams.filter import initialize
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget, QComboBox

from ...utilities import *

@pytest.mark.parametrize(
    "configuration_name, den, num, resetineachstate, input_signals, output_signals",
    [
        ("dummyvalue",'{1}','{0.5 0.5}', 1,[('Constantf',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32'}})], [('Constanti',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})]),
        ("dummyvalue1",'{3}','{0.5 0.25}', '1',[('Hello',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}}),('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float64','Alias':'HW'}})],[('Helloout',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint64'}}),('Worldout',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','Alias':'HW'}})]),
        ("dummyvalue2",'{7}','{0.75 0.5}', 0,[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3}})],[('dout',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint64','NumberOfElements':3}})]),
        ("dummyvalue2",'{2}','{0.4 0.9}', '0',[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3,'NumberOfDimensions':'1'}})],[('small_int',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint8','NumberOfElements':3,'NumberOfDimensions':'1'}})])
    ]
)
def test_FilterGAM(configuration_name, den, num, resetineachstate, input_signals, output_signals, load_parameters):
    setup_writer = marteconfig.StringConfigWriter()
    example_filtergam = FilterGAM(configuration_name, den=den, num=num, resetineachstate=resetineachstate, input_signals=input_signals, output_signals=output_signals)
    
    # Assert attributes
    assert example_filtergam.configuration_name == configuration_name
    assert example_filtergam.den == den
    assert example_filtergam.num == num
    assert example_filtergam.resetineachstate == resetineachstate
    assert example_filtergam.output_signals == output_signals

    # Assert Serializations
    assert example_filtergam.serialize()['configuration_name'] == configuration_name
    assert example_filtergam.serialize()['parameters']['den'] == den
    assert example_filtergam.serialize()['parameters']['num'] == num
    assert example_filtergam.serialize()['parameters']['resetineachstate'] == resetineachstate

    # Assert Deserialization
    new_filtergam = FilterGAM().deserialize(example_filtergam.serialize())
    assert new_filtergam.configuration_name.lstrip('+') == configuration_name
    assert new_filtergam.den == den
    assert new_filtergam.num == num
    assert new_filtergam.resetineachstate == resetineachstate
    assert new_filtergam.output_signals == output_signals

    # Assert config written
    example_filtergam.write(setup_writer)
    test_writer = writeSignals_section(input_signals, output_signals)

    assert str(setup_writer) == f'''+{configuration_name} = {{\n    Class = FilterGAM
    Num = {num}
    Den = {den}
    ResetInEachState = {resetineachstate}
{str(test_writer)}\n}}'''

    example_filtergam.loadParameters(load_parameters, GAMNode(example_filtergam))

    classes = [QLabel, QLineEdit, QPushButton, QLabel, QLineEdit, QPushButton, QLabel, QLineEdit, QLabel, QLineEdit, QLabel, QComboBox]
    assert len(load_parameters.configbarBox) == len(classes)
    default_text = ['Number of input signals: ', str(len(example_filtergam.input_signals)), 'Configure Signals',
                    'Number of output signals: ', str(len(example_filtergam.output_signals)), 'Configure Signals',
                    'Amplitude: ', num, 'Frequency: ', den, 'Reset in Each State: ', str(resetineachstate)]
    test_text = [True, True, True, True, True, True, True, True, True, True, True, False]
    for i in range(len(classes)):
        assert load_parameters.configbarBox.itemAt(i).widget().__class__ == classes[i]
        if test_text[i]:
            assert load_parameters.configbarBox.itemAt(i).widget().text() == default_text[i]

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('FilterGAM') == FilterGAM
