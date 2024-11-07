import pytest

from martepy.marte2.datasources import LinuxTimer
from martepy.marte2.datasources.linux_timer import initialize
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget, QComboBox

from ...utilities import *

@pytest.mark.parametrize(
    "configuration_name, cpu_mask, execution_mode, frequency, sleep_nature, sleep_percentage, phase",
    [
        ("dummyvalue", "0", "IndependentThread", "1000", "Default", 0, 0),
        ("dummyvalue1", "0x2", "IndependentThread", "0x500", "Busy", 0.1, 45),
        ("dummyvalue2", 0x256, "RealTimeThread", 45, "Default", 0.5, 90),
        ("dummyvalue2", 512, "RealTimeThread", 0x90, "Busy", 0.8, 180)
    ]
)
def test_LinuxTimer(configuration_name, cpu_mask, execution_mode, frequency, sleep_nature, sleep_percentage, phase, load_parameters):
    setup_writer = marteconfig.StringConfigWriter()
    example_linuxtimer = LinuxTimer(configuration_name=configuration_name, cpu_mask=cpu_mask, execution_mode=execution_mode, frequency=frequency, sleep_nature=sleep_nature, sleep_percentage=sleep_percentage, phase=phase)
    
    const_output = [('Counter',{'MARTeConfig':{'Type': 'uint32', 'NumberOfDimensions': '1', 'NumberOfElements':'1'}}),
                    ('Time',{'MARTeConfig':{'Type': 'uint32', 'Frequency': frequency, 'NumberOfDimensions': '1', 'NumberOfElements':'1'}}),
                    ('AbsoluteTime',{'MARTeConfig':{'Type': 'uint64', 'NumberOfDimensions': '1', 'NumberOfElements':'1'}}),
                    ('DeltaTime',{'MARTeConfig':{'Type': 'uint64', 'NumberOfDimensions': '1', 'NumberOfElements':'1'}}),
                        ('TrigRephase',{'MARTeConfig':{'Type': 'uint8', 'NumberOfDimensions': '1', 'NumberOfElements':'1'}})]

    # Assert attributes
    assert example_linuxtimer.configuration_name == configuration_name
    assert example_linuxtimer.cpu_mask == cpu_mask
    assert example_linuxtimer.execution_mode == execution_mode
    assert example_linuxtimer.frequency == frequency
    assert example_linuxtimer.sleep_nature == sleep_nature
    assert example_linuxtimer.output_signals == const_output

    # Assert Serializations
    assert example_linuxtimer.serialize()['configuration_name'] == configuration_name
    assert example_linuxtimer.serialize()['parameters']['cpu_mask'] == cpu_mask
    assert example_linuxtimer.serialize()['parameters']['execution_mode'] == execution_mode
    assert example_linuxtimer.serialize()['parameters']['frequency'] == frequency
    assert example_linuxtimer.serialize()['parameters']['sleep_nature'] == sleep_nature
    assert example_linuxtimer.serialize()['parameters']['sleep_percentage'] == sleep_percentage
    assert example_linuxtimer.serialize()['parameters']['phase'] == phase

    # Assert Deserialization
    new_linuxtimer = LinuxTimer().deserialize(example_linuxtimer.serialize())
    assert new_linuxtimer.configuration_name.lstrip('+') == configuration_name
    assert new_linuxtimer.cpu_mask == cpu_mask
    assert new_linuxtimer.execution_mode == execution_mode
    assert new_linuxtimer.frequency == frequency
    assert new_linuxtimer.sleep_nature == sleep_nature
    assert new_linuxtimer.sleep_percentage == sleep_percentage
    assert new_linuxtimer.phase == phase

    # Assert config written
    example_linuxtimer.write(setup_writer)
    test_writer = write_datasource_signals_section(const_output)

    cpu_mask = cpu_mask
    if isinstance(cpu_mask, str):
        if 'x' in cpu_mask:
            cpu_mask = cpu_mask
        else:
            cpu_mask =  hex(int(cpu_mask))
    else:
        cpu_mask = hex(cpu_mask)

    assert str(setup_writer) == f'''+{configuration_name} = {{
    Class = LinuxTimer
    SleepNature = "{sleep_nature}"
    ExecutionMode = "{execution_mode}"
    CPUMask = {cpu_mask}
    Phase = {phase}
    SleepPercentage = {sleep_percentage}
{str(test_writer)}\n}}'''

    example_linuxtimer.loadParameters(load_parameters, GAMNode(example_linuxtimer))

    classes = [QWidget, QLabel, QLineEdit, QWidget]
    default_text = ['', 'Frequency: ', str(frequency), '']
    assert len(load_parameters.configbarBox) == len(classes)
    for i in range(len(classes)):
        assert load_parameters.configbarBox.itemAt(i).widget().__class__ == classes[i]
        if not(classes[i] == QWidget or classes[i] == QComboBox):
            assert load_parameters.configbarBox.itemAt(i).widget().text() == default_text[i]

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('LinuxTimer') == LinuxTimer
