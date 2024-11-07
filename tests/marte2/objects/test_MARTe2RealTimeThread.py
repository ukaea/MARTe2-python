import pytest

from martepy.marte2.objects.real_time_thread import MARTe2RealTimeThread, initialize
from martepy.marte2.gams.constant_gam import ConstantGAM
from martepy.marte2.gams.iogam import IOGAM
from martepy.marte2.objects.referencecontainer import MARTe2ReferenceContainer
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from ...utilities import *

const = ConstantGAM('+Constants1')
iogamlogger = IOGAM('+logger')
iogamtimer = IOGAM('+Timer')

@pytest.mark.parametrize(
    "configuration_name, cpu_mask, functions",
    [
        ("dummyvalue", "0x76", [const]),
        ("dummyvalue1", 0x76, [const, iogamtimer]),
        ("dummyvalue2", "56", [const, iogamtimer, iogamlogger]),
        ("dummyvalue2", 56, [])
    ]
)
def test_MARTe2RealTimeThread(configuration_name, cpu_mask, functions):
    setup_writer = marteconfig.StringConfigWriter()
    factory = TFactory()
    example_marte2realtimethread = MARTe2RealTimeThread(configuration_name=configuration_name, cpu_mask=cpu_mask, functions=functions)
    
    assert not example_marte2realtimethread == list([])

    # Assert attributes
    assert example_marte2realtimethread.configuration_name == configuration_name
    assert example_marte2realtimethread.cpu_mask == cpu_mask
    assert example_marte2realtimethread.functions == functions

    # Assert Serializations
    assert example_marte2realtimethread.serialize()['configuration_name'] == configuration_name
    assert example_marte2realtimethread.serialize()['cpu_mask'] == cpu_mask
    assert example_marte2realtimethread.serialize()['functions'] == [a.serialize() for a in functions]

    # Assert Deserialization
    new_marte2realtimethread = MARTe2RealTimeThread().deserialize(example_marte2realtimethread.serialize(), factory=factory)
    assert new_marte2realtimethread.configuration_name.lstrip('+') == configuration_name
    assert new_marte2realtimethread.cpu_mask == cpu_mask
    assert new_marte2realtimethread.functions == functions
    
    new_marte2realtimethread.functions = [iogamlogger]
    assert not new_marte2realtimethread.functions == example_marte2realtimethread
    # Assert config written
    example_marte2realtimethread.write(setup_writer)

    cpu_mask = cpu_mask
    if isinstance(cpu_mask, str):
        if 'x' in cpu_mask:
            cpu_mask = cpu_mask
        else:
            cpu_mask =  hex(int(cpu_mask))
    else:
        cpu_mask = hex(cpu_mask)

    assert str(setup_writer) == f'''+{configuration_name} = {{
    Class = RealTimeThread\n    CPUs = {cpu_mask}\n    Functions = {{ {' '.join([a.configuration_name.lstrip('+') for a in functions])} }}\n}}'''

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('RealTimeThread') == MARTe2RealTimeThread