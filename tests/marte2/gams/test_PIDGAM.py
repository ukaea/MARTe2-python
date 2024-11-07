import pytest

from martepy.marte2.gams import PIDGAM
from martepy.marte2.gams.pid import initialize
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget, QComboBox

from ...utilities import *

@pytest.mark.parametrize(
    "configuration_name, kd, ki, kp, maxoutput, minoutput, samplefrequency, input_signals, output_signals",
    [
        ("dummyvalue",10.0,1,2,50,2,5,[('Constantf',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32'}})], [('Constanti',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})]),
        ("dummyvalue1",'10.0','1.0','2.0','50','2','5',[('Hello',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}}),('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float64','Alias':'HW'}})],[('Helloout',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint64'}}),('Worldout',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','Alias':'HW'}})]),
        ("dummyvalue2",'10.0','1.0',2,'50',2,5,[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3}})],[('dout',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint64','NumberOfElements':3}})]),
        ("dummyvalue2",10,'1.4','2.3',3.4,59,21,[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3,'NumberOfDimensions':'1'}})],[('small_int',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint8','NumberOfElements':3,'NumberOfDimensions':'1'}})])
    ]
)
def test_PIDGAM(configuration_name, kd, ki, kp, maxoutput, minoutput, samplefrequency, input_signals, output_signals, load_parameters):
    setup_writer = marteconfig.StringConfigWriter()
    example_pidgam = PIDGAM(configuration_name, kd=kd, ki=ki, kp=kp, maxoutput=maxoutput, minoutput=minoutput, samplefrequency=samplefrequency, input_signals=input_signals,output_signals=output_signals)
    
    # Assert attributes
    assert example_pidgam.configuration_name == configuration_name
    assert example_pidgam.kd == kd
    assert example_pidgam.ki == ki
    assert example_pidgam.kp == kp
    assert example_pidgam.maxoutput == maxoutput
    assert example_pidgam.minoutput == minoutput
    assert example_pidgam.samplefrequency == samplefrequency
    assert example_pidgam.output_signals == output_signals
    assert example_pidgam.input_signals == input_signals

    # Assert Serializations
    assert example_pidgam.serialize()['configuration_name'] == configuration_name
    assert example_pidgam.serialize()['parameters']['kd'] == kd
    assert example_pidgam.serialize()['parameters']['ki'] == ki
    assert example_pidgam.serialize()['parameters']['kp'] == kp
    assert example_pidgam.serialize()['parameters']['maxoutput'] == maxoutput
    assert example_pidgam.serialize()['parameters']['minoutput'] == minoutput
    assert example_pidgam.serialize()['parameters']['samplefrequency'] == samplefrequency
    assert example_pidgam.serialize()['inputsb'] == input_signals
    assert example_pidgam.serialize()['outputsb'] == output_signals

    # Assert Deserialization
    new_pidgam = PIDGAM().deserialize(example_pidgam.serialize())
    assert new_pidgam.configuration_name.lstrip('+') == configuration_name
    assert new_pidgam.kd == kd
    assert new_pidgam.ki == ki
    assert new_pidgam.kp == kp
    assert new_pidgam.maxoutput == maxoutput
    assert new_pidgam.minoutput == minoutput
    assert new_pidgam.samplefrequency == samplefrequency
    assert new_pidgam.output_signals == output_signals
    assert new_pidgam.input_signals == input_signals

    # Assert config written
    example_pidgam.write(setup_writer)
    test_writer = writeSignals_section(input_signals, output_signals)

    assert str(setup_writer) == f'''+{configuration_name} = {{\n    Class = PIDGAM
    kp = {kp}
    ki = {ki}
    kd = {kd}
    sampleFrequency = {samplefrequency}
    maxOutput = {maxoutput}
    minOutput = {minoutput}
{str(test_writer)}\n}}'''

    example_pidgam.loadParameters(load_parameters, GAMNode(example_pidgam))

    classes = [QLabel, QLineEdit, QPushButton, QLabel, QLineEdit, QPushButton,
           QLabel, QLineEdit, QLabel, QLineEdit, QLabel, QLineEdit, QLabel, QLineEdit,
           QLabel, QLineEdit, QLabel, QLineEdit]
    default_text = ['Number of input signals: ', str(len(example_pidgam.input_signals)), 'Configure Signals',
                    'Number of output signals: ', str(len(example_pidgam.output_signals)), 'Configure Signals',
                    'Kp: ', str(kp), 'Ki: ', str(ki), 'Kd: ', str(kd), 'Sample Frequency: ', str(samplefrequency),
                    'Max Output: ', str(maxoutput), 'Min Output: ', str(minoutput)]
    test_text = [True] * len(classes)
    assert len(load_parameters.configbarBox) == len(classes)
    for i in range(len(classes)):
        assert load_parameters.configbarBox.itemAt(i).widget().__class__ == classes[i]
        if test_text[i]:
            assert load_parameters.configbarBox.itemAt(i).widget().text() == default_text[i]

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('PIDGAM') == PIDGAM
