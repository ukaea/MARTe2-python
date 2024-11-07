import pytest

from martepy.marte2.gams import WaveformSinGAM
from martepy.marte2.gams.waveform_sin import initialize
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget, QComboBox

from ...utilities import *

@pytest.mark.parametrize(
    "amplitude, configuration_name, frequency, offset, phase, starttriggertime, stoptriggertime, input_signals, output_signals",
    [
        ("10", "dummyvalue", "1.0", 10, "45", "{0.1 0.3 0.5 1.8}", "{0.2 0.4 0.6}",[('Constantf',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32'}})], [('Constanti',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})]),
        ("12.3", "dummyvalue1", "8.7", 12.3, "90", [0.1, 0.3, 0.5, 1.8], "{0.2 0.4 0.6}",[('Hello',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}}),('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float64','Alias':'HW'}})],[('Helloout',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint64'}}),('Worldout',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','Alias':'HW'}})]),
        (32, "dummyvalue2", "87", "32", 0, "{0.1 0.3 0.5 1.8}", [0.2, 0.4, 0.6],[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3}})],[('dout',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint64','NumberOfElements':3}})]),
        (37.8, "dummyvalue2", 43, "37.8", 180, "{0.1 0.3 0.5 1.8}", "{0.2 0.4 0.6}",[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3,'NumberOfDimensions':'1'}})],[('small_int',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint8','NumberOfElements':3,'NumberOfDimensions':'1'}})])
    ]
)
def test_WaveformSinGAM(amplitude, configuration_name, frequency, offset, phase, starttriggertime, stoptriggertime, input_signals, output_signals, load_parameters):
    setup_writer = marteconfig.StringConfigWriter()
    example_waveformsingam = WaveformSinGAM(configuration_name, amplitude=amplitude, frequency=frequency, offset=offset, phase=phase, starttriggertime=starttriggertime, stoptriggertime=stoptriggertime, input_signals=input_signals,output_signals=output_signals)
    
    starttriggertimeb = starttriggertime
    stoptriggertimeb = stoptriggertime

    # Assert attributes
    assert example_waveformsingam.amplitude == amplitude
    assert example_waveformsingam.configuration_name == configuration_name
    assert example_waveformsingam.frequency == frequency
    assert example_waveformsingam.offset == offset
    assert example_waveformsingam.phase == phase
    assert example_waveformsingam.starttriggertime == starttriggertime
    assert example_waveformsingam.stoptriggertime == stoptriggertime
    assert example_waveformsingam.output_signals == output_signals
    assert example_waveformsingam.input_signals == input_signals

    # Assert Serializations
    assert example_waveformsingam.serialize()['parameters']['amplitude'] == amplitude
    assert example_waveformsingam.serialize()['configuration_name'] == configuration_name
    assert example_waveformsingam.serialize()['parameters']['frequency'] == frequency
    assert example_waveformsingam.serialize()['parameters']['offset'] == offset
    assert example_waveformsingam.serialize()['parameters']['phase'] == phase
    assert example_waveformsingam.serialize()['parameters']['starttriggertime'] == starttriggertime
    assert example_waveformsingam.serialize()['parameters']['stoptriggertime'] == stoptriggertime
    assert example_waveformsingam.serialize()['inputsb'] == input_signals
    assert example_waveformsingam.serialize()['outputsb'] == output_signals

    # Assert Deserialization
    new_waveformsingam = WaveformSinGAM().deserialize(example_waveformsingam.serialize())
    assert new_waveformsingam.amplitude == amplitude
    assert new_waveformsingam.configuration_name.lstrip('+') == configuration_name
    assert new_waveformsingam.frequency == frequency
    assert new_waveformsingam.offset == offset
    assert new_waveformsingam.phase == phase
    assert new_waveformsingam.starttriggertime == starttriggertime
    assert new_waveformsingam.stoptriggertime == stoptriggertime
    assert new_waveformsingam.input_signals == input_signals
    assert new_waveformsingam.output_signals == output_signals

    # Assert config written
    example_waveformsingam.write(setup_writer)
    test_writer = writeSignals_section(input_signals, output_signals)
    if isinstance(starttriggertime, list):
        starttriggertime = '{' + ' '.join([str(a) for a in starttriggertime]) + '}'
    if isinstance(stoptriggertime, list):
        stoptriggertime = '{' + ' '.join([str(a) for a in stoptriggertime]) + '}'

    assert str(setup_writer) == f'''+{configuration_name} = {{\n    Class = WaveformGAM::WaveformSin
    Amplitude = {amplitude}
    Frequency = {frequency}
    Phase = {phase}
    Offset = {offset}
    StartTriggerTime = {starttriggertime}
    StopTriggerTime = {stoptriggertime}
{str(test_writer)}\n}}'''

    example_waveformsingam.starttriggertime = starttriggertimeb
    example_waveformsingam.stoptriggertime = stoptriggertimeb

    example_waveformsingam.loadParameters(load_parameters, GAMNode(example_waveformsingam))

    classes = [QLabel, QLineEdit, QPushButton, QLabel, QLineEdit, QPushButton,
           QLabel, QLineEdit, QLabel, QLineEdit, QLabel, QLineEdit, QLabel, QLineEdit,
           QLabel, QLineEdit, QLabel, QLineEdit]
    default_text = ['Number of input signals: ', str(len(example_waveformsingam.input_signals)), 'Configure Signals',
                    'Number of output signals: ', str(len(example_waveformsingam.output_signals)), 'Configure Signals',
                    'Amplitude: ', str(amplitude), 'Frequency: ', str(frequency), 'Phase: ', str(phase),
                    'Offset: ', str(offset), 'Start Trigger Time: ', starttriggertime, 'Stop Trigger Time: ', stoptriggertime]
    test_text = [True] * len(classes)
    assert len(load_parameters.configbarBox) == len(classes)
    for i in range(len(classes)):
        assert load_parameters.configbarBox.itemAt(i).widget().__class__ == classes[i]
        if test_text[i]:
            assert load_parameters.configbarBox.itemAt(i).widget().text() == default_text[i]

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('WaveformSinGAM') == WaveformSinGAM
