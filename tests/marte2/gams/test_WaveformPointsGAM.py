import pytest

from martepy.marte2.gams import WaveformPointsGAM
from martepy.marte2.gams.waveform_points import initialize
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget, QComboBox

from ...utilities import *

@pytest.mark.parametrize(
    "configuration_name, points, starttriggertime, stoptriggertime, times, input_signals, output_signals",
    [
        ("dummyvalue", "{10.0 5.1 0.3 3}", "{0.1 0.3 0.5 1.8}", "{0.2 0.4 0.6}", "{0.0 2.1 3.2 4.5}",[('Time',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32'}})], [('Constanti',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})]),
        ("dummyvalue1", "{10.3 5.1 0.3 3}", "{0.12 0.33 0.5 1.8}", "{0.2 0.4 0.6}", "{9.0 21 3.2 85}",[('Hello',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})],[('Helloout',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint64'}}),('Worldout',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','Alias':'HW'}})]),
        ("dummyvalue2", "{15.0 8.1 0.8 3}", [0.7, 0.6, 0.5, 1.2], [0.2, 0.4, 0.6], [0.2, 2.1, 3.7, 4],[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3}})],[('dout',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint64','NumberOfElements':3}})]),
        ("dummyvalue2", [30.0, 6.1, 0.3, 8], "{0.8 0.9 1.3 1.8}", "{0.85 0.95 1.4}", "{0.9 2.1 3.2 95}",[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3,'NumberOfDimensions':'1'}})],[('small_int',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint8','NumberOfElements':3,'NumberOfDimensions':'1'}})])
    ]
)
def test_WaveformPointsGAM(configuration_name, points, starttriggertime, stoptriggertime, times, input_signals, output_signals, load_parameters):
    setup_writer = marteconfig.StringConfigWriter()
    example_waveformpointsgam = WaveformPointsGAM(configuration_name, points=points, starttriggertime=starttriggertime, stoptriggertime=stoptriggertime, times=times, input_signals=input_signals, output_signals=output_signals)
    pointsb = points
    starttriggertimeb = starttriggertime
    stoptriggertimeb = stoptriggertime
    timesb = times
    # Assert attributes
    assert example_waveformpointsgam.configuration_name == configuration_name
    assert example_waveformpointsgam.points == points
    assert example_waveformpointsgam.starttriggertime == starttriggertime
    assert example_waveformpointsgam.stoptriggertime == stoptriggertime
    assert example_waveformpointsgam.times == times
    assert example_waveformpointsgam.output_signals == output_signals
    assert example_waveformpointsgam.input_signals == input_signals

    # Assert Serializations
    assert example_waveformpointsgam.serialize()['configuration_name'] == configuration_name
    assert example_waveformpointsgam.serialize()['parameters']['points'] == points
    assert example_waveformpointsgam.serialize()['parameters']['starttriggertime'] == starttriggertime
    assert example_waveformpointsgam.serialize()['parameters']['stoptriggertime'] == stoptriggertime
    assert example_waveformpointsgam.serialize()['parameters']['times'] == times
    assert example_waveformpointsgam.serialize()['inputsb'] == input_signals
    assert example_waveformpointsgam.serialize()['outputsb'] == output_signals

    # Assert Deserialization
    new_waveformpointsgam = WaveformPointsGAM().deserialize(example_waveformpointsgam.serialize())
    assert new_waveformpointsgam.configuration_name.lstrip('+') == configuration_name
    assert new_waveformpointsgam.points == points
    assert new_waveformpointsgam.starttriggertime == starttriggertime
    assert new_waveformpointsgam.stoptriggertime == stoptriggertime
    assert new_waveformpointsgam.times == times
    assert new_waveformpointsgam.output_signals == output_signals
    assert new_waveformpointsgam.input_signals == input_signals

    # Assert config written
    example_waveformpointsgam.write(setup_writer)
    test_writer = writeSignals_section(input_signals, output_signals)
    if isinstance(starttriggertime, list):
        starttriggertime = '{' + ' '.join([str(a) for a in starttriggertime]) + '}'
    if isinstance(stoptriggertime, list):
        stoptriggertime = '{' + ' '.join([str(a) for a in stoptriggertime]) + '}'
    if isinstance(points, list):
        points = '{' + ' '.join([str(a) for a in points]) + '}'
    if isinstance(times, list):
        times = '{' + ' '.join([str(a) for a in times]) + '}'

    assert str(setup_writer) == f'''+{configuration_name} = {{\n    Class = WaveformGAM::WaveformPointsDef
    Points = {points}
    Times = {times}
    StartTriggerTime = {starttriggertime}
    StopTriggerTime = {stoptriggertime}
{str(test_writer)}\n}}'''

    example_waveformpointsgam.points = pointsb
    example_waveformpointsgam.starttriggertime = starttriggertimeb
    example_waveformpointsgam.stoptriggertime = stoptriggertimeb
    example_waveformpointsgam.times = timesb

    example_waveformpointsgam.loadParameters(load_parameters, GAMNode(example_waveformpointsgam))

    classes = [QLabel, QLineEdit, QPushButton, QLabel, QLineEdit, QPushButton,
           QLabel, QLineEdit, QLabel, QLineEdit, QLabel, QLineEdit, QLabel, QLineEdit]
    default_text = ['Number of input signals: ', str(len(example_waveformpointsgam.input_signals)), 'Configure Signals',
                    'Number of output signals: ', str(len(example_waveformpointsgam.output_signals)), 'Configure Signals',
                    'Points: ', points, 'Times: ', times, 'Start Trigger Time: ', starttriggertime,
                    'Stop Trigger Time: ', stoptriggertime]
    test_text = [True] * len(classes)
    assert len(load_parameters.configbarBox) == len(classes)
    for i in range(len(classes)):
        assert load_parameters.configbarBox.itemAt(i).widget().__class__ == classes[i]
        if test_text[i]:
            assert load_parameters.configbarBox.itemAt(i).widget().text() == default_text[i]

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('WaveformPointsGAM') == WaveformPointsGAM
