import pytest

from martepy.marte2.objects.statemachine.eventtrigger import MARTe2EventConditionTrigger, initialize
from martepy.functions.extra_functions import isint, isfloat
from martepy.marte2.objects.message import MARTe2Message
from martepy.marte2.gams.message_gam import MFactory
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from ...utilities import *

msg = MARTe2Message('GOTOERROR','StateMachine','StopCurrentStateExecution')

@pytest.mark.parametrize(
    "configuration_name, eventtriggers, objects",
    [
        ("dummyvalue", {"command1":1, "Signal1":2}, []),
        ("dummyvalue1", {"command1":"1", "Signal1":"2"}, [msg]),
        ("dummyvalue2", {"command1":"1"}, []),
        ("dummyvalue2", {"command1":1}, [msg,msg])
    ]
)
def test_MARTe2EventConditionTrigger(configuration_name, eventtriggers, objects):
    setup_writer = marteconfig.StringConfigWriter()
    factory = MFactory()
    example_marte2eventconditiontrigger = MARTe2EventConditionTrigger(configuration_name=configuration_name, eventtriggers=eventtriggers, msgs=objects)
    
    assert not example_marte2eventconditiontrigger == list([])
    # Assert attributes
    assert example_marte2eventconditiontrigger.configuration_name == configuration_name
    assert example_marte2eventconditiontrigger.eventtriggers == eventtriggers
    assert example_marte2eventconditiontrigger.objects == objects

    # Assert Serializations
    assert example_marte2eventconditiontrigger.serialize()['configuration_name'] == configuration_name
    assert example_marte2eventconditiontrigger.serialize()['eventtriggers'] == eventtriggers
    assert example_marte2eventconditiontrigger.serialize()['objects'] == [a.serialize() for a in objects]

    # Assert Deserialization
    new_marte2eventconditiontrigger = MARTe2EventConditionTrigger().deserialize(example_marte2eventconditiontrigger.serialize(),factory=factory)
    assert new_marte2eventconditiontrigger.configuration_name.lstrip('+') == configuration_name
    assert new_marte2eventconditiontrigger.eventtriggers == eventtriggers
    assert new_marte2eventconditiontrigger.objects == objects

    # Assert config written
    example_marte2eventconditiontrigger.write(setup_writer)

    string_content = []
    for key, value in eventtriggers.items():
        value = value if isint(value) or isfloat(value) else f'"{value}"'
        string_content.append(f'        {key} = {value}')

    string_content = '\n'.join(string_content)

    test_writer = marteconfig.StringConfigWriter()
    test_writer.setTab(1)
    # We assume Messages write correctly as we test that more directly elsewhere
    for object in objects:
        object.write(test_writer)
    newline = '\n'
    if str(repr(test_writer)) == '':
        newline = ''
    assert str(setup_writer) == f'''+{configuration_name} = {{
    Class = EventConditionTrigger
    EventTriggers = {{
{string_content}
    }}
{str(repr(test_writer))}{newline}}}'''

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('EventConditionTrigger') == MARTe2EventConditionTrigger