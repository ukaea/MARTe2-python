import pytest

from martepy.marte2.gams import WaveformChirpGAM
from martepy.marte2.gams.waveform_chirp import initialize
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget, QComboBox

from ...utilities import *


@pytest.mark.parametrize(
    "configuration_name,amplitude, frequency1, frequency2, offset, phase, starttriggertime, stoptriggertime, input_signals, output_signals",
    [
        ("dummyvalue", "100.0", "1.0", "3787", "1.1", "45", "{0.1 0.3 0.5 1.8}", "{0.2 0.4 0.6}",[('Constantf',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32'}})], [('Constanti',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})]),
        ("dummyvalue1", "10.0", 3.4, 1.41, "6.8", "180", "{0.1 0.43 0.5 1.8}", "{0.2 0.4 0.6}",[('Hello',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})],[('Helloout',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint64'}}),('Worldout',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','Alias':'HW'}})]),
        ("dummyvalue2", 13, "7.8", "1.41", "10.8", "90", "{0.1 0.23 0.5 1.8}", "{0.2 0.4 0.6}",[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3}})],[('dout',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint64','NumberOfElements':3}})]),
        ("dummyvalue2", 57, 9.78, "142", 20, 210, [0.1, 0.3, 0.75, 1.8], [0.2, 0.4, 0.6],[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3,'NumberOfDimensions':'1'}})],[('small_int',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint8','NumberOfElements':3,'NumberOfDimensions':'1'}})])
    ]
)
def test_WaveformChirpGAM(amplitude, configuration_name, frequency1, frequency2, offset, phase, starttriggertime, stoptriggertime, input_signals, output_signals, load_parameters):
    setup_writer = marteconfig.StringConfigWriter()
    example_waveformchirpgam = WaveformChirpGAM(configuration_name, amplitude=amplitude,frequency1=frequency1, frequency2=frequency2, offset=offset, phase=phase, starttriggertime=starttriggertime, stoptriggertime=stoptriggertime, input_signals=input_signals, output_signals=output_signals)
    
    starttriggertimeb = starttriggertime
    stoptriggertimeb = stoptriggertime

    # Assert attributes
    assert example_waveformchirpgam.amplitude == amplitude
    assert example_waveformchirpgam.configuration_name == configuration_name
    assert example_waveformchirpgam.frequency1 == frequency1
    assert example_waveformchirpgam.frequency2 == frequency2
    assert example_waveformchirpgam.offset == offset
    assert example_waveformchirpgam.phase == phase
    assert example_waveformchirpgam.starttriggertime == starttriggertime
    assert example_waveformchirpgam.stoptriggertime == stoptriggertime
    assert example_waveformchirpgam.input_signals == input_signals
    assert example_waveformchirpgam.output_signals == output_signals

    # Assert Serializations
    assert example_waveformchirpgam.serialize()['parameters']['amplitude'] == amplitude
    assert example_waveformchirpgam.serialize()['configuration_name'] == configuration_name
    assert example_waveformchirpgam.serialize()['parameters']['frequency1'] == frequency1
    assert example_waveformchirpgam.serialize()['parameters']['frequency2'] == frequency2
    assert example_waveformchirpgam.serialize()['parameters']['offset'] == offset
    assert example_waveformchirpgam.serialize()['parameters']['phase'] == phase
    assert example_waveformchirpgam.serialize()['parameters']['starttriggertime'] == starttriggertime
    assert example_waveformchirpgam.serialize()['parameters']['stoptriggertime'] == stoptriggertime
    assert example_waveformchirpgam.serialize()['inputsb'] == input_signals
    assert example_waveformchirpgam.serialize()['outputsb'] == output_signals

    # Assert Deserialization
    new_waveformchirpgam = WaveformChirpGAM().deserialize(example_waveformchirpgam.serialize())
    assert new_waveformchirpgam.amplitude == amplitude
    assert new_waveformchirpgam.configuration_name.lstrip('+') == configuration_name
    assert new_waveformchirpgam.frequency1 == frequency1
    assert new_waveformchirpgam.frequency2 == frequency2
    assert new_waveformchirpgam.offset == offset
    assert new_waveformchirpgam.phase == phase
    assert new_waveformchirpgam.starttriggertime == starttriggertime
    assert new_waveformchirpgam.stoptriggertime == stoptriggertime
    assert new_waveformchirpgam.output_signals == output_signals

    # Assert config written
    example_waveformchirpgam.write(setup_writer)
    time_writer = marteconfig.StringConfigWriter()
    time_writer.tab += 1
    time_writer.startSection('Time')
    MARTe2ConfigObject.writeSignals(input_signals, time_writer)
    time_writer.endSection('Time')
    test_writer = writeSignals_section([], output_signals)
    if isinstance(starttriggertime, list):
        starttriggertime = '{' + ' '.join([str(a) for a in starttriggertime]) + '}'
    if isinstance(stoptriggertime, list):
        stoptriggertime = '{' + ' '.join([str(a) for a in stoptriggertime]) + '}'

    assert str(setup_writer) == f'''+{configuration_name} = {{\n    Class = WaveformGAM::WaveformChirp
    Amplitude = {amplitude}
    Frequency1 = {frequency1}
    Frequency2 = {frequency2}
    Phase = {phase}
    Offset = {offset}
    StartTriggerTime = {starttriggertime}
    StopTriggerTime = {stoptriggertime}
{str(time_writer)}
{str(test_writer)}\n}}'''

    example_waveformchirpgam.starttriggertime = starttriggertimeb
    example_waveformchirpgam.stoptriggertime = stoptriggertimeb

    example_waveformchirpgam.loadParameters(load_parameters, GAMNode(example_waveformchirpgam))

    classes = [QLabel, QLineEdit, QPushButton, QLabel, QLineEdit, QPushButton,
           QLabel, QLineEdit, QLabel, QLineEdit, QLabel, QLineEdit, QLabel, QLineEdit,
           QLabel, QLineEdit, QLabel, QLineEdit, QLabel, QLineEdit]
    default_text = ['Number of input signals: ', str(len(example_waveformchirpgam.input_signals)), 'Configure Signals',
                    'Number of output signals: ', str(len(example_waveformchirpgam.output_signals)), 'Configure Signals',
                    'Amplitude: ', str(amplitude), 'Frequency 1: ', str(frequency1), 'Frequency 2: ', str(frequency2),
                    'Phase: ', str(phase),'Offset: ', str(offset),
                    'Start Trigger Time: ', starttriggertime,'Stop Trigger Time: ', stoptriggertime]
    test_text = [True] * len(classes)
    assert len(load_parameters.configbarBox) == len(classes)
    for i in range(len(classes)):
        assert load_parameters.configbarBox.itemAt(i).widget().__class__ == classes[i]
        if test_text[i]:
            assert load_parameters.configbarBox.itemAt(i).widget().text() == default_text[i]

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('WaveformChirpGAM') == WaveformChirpGAM
