import pytest

from martepy.marte2.objects.real_time_state import MARTe2RealTimeState, initialize
from martepy.marte2.objects.real_time_thread import MARTe2RealTimeThread
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
    "configuration_name, threads",
    [
        ("dummyvalue",MARTe2ReferenceContainer(configuration_name='Threads', objects=[MARTe2RealTimeThread('+Thread1', '86',[const])])),
        ("dummyvalue1",MARTe2ReferenceContainer(configuration_name='Threads', objects=[MARTe2RealTimeThread('+Error', 86,[const, iogamtimer])])),
        ("dummyvalue2",MARTe2ReferenceContainer(configuration_name='Threads', objects=[MARTe2RealTimeThread('+Running', 0x56,[const, iogamtimer, iogamlogger])])),
        ("dummyvalue2",MARTe2ReferenceContainer(configuration_name='Threads', objects=[]))
    ]
)
def test_MARTe2RealTimeState(configuration_name, threads):
    setup_writer = marteconfig.StringConfigWriter()
    factory = TFactory()
    example_marte2realtimestate = MARTe2RealTimeState(configuration_name=configuration_name, threads=threads)
    
    # Assert attributes
    assert example_marte2realtimestate.configuration_name == configuration_name
    assert example_marte2realtimestate.threads == threads

    # Assert Serializations
    assert example_marte2realtimestate.serialize()['configuration_name'] == configuration_name
    assert example_marte2realtimestate.serialize()['threads'] == threads.serialize()


    # Assert Deserialization
    new_marte2realtimestate = MARTe2RealTimeState().deserialize(example_marte2realtimestate.serialize(), factory=factory)
    assert new_marte2realtimestate.configuration_name.lstrip('+') == configuration_name
    assert new_marte2realtimestate.threads == threads

    # Assert config written
    example_marte2realtimestate.write(setup_writer)
    test_writer = marteconfig.StringConfigWriter()
    test_writer.setTab(1)
    threads.write(test_writer)
    
    string_content = str(repr(test_writer))
    
    assert str(setup_writer) == f'''+{configuration_name} = {{
    Class = RealTimeState\n{string_content}\n}}'''

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('RealTimeState') == MARTe2RealTimeState