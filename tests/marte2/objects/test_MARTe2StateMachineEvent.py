import pytest

from martepy.marte2.objects.statemachine.event import MARTe2StateMachineEvent, initialize
from martepy.marte2.objects.message import MARTe2Message
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from ...utilities import *

msg = MARTe2Message('GOTOERROR','StateMachine','StopCurrentStateExecution')

@pytest.mark.parametrize(
    "configuration_name, messages, nextstate, nextstateerror, timeout",
    [
        ("dummyvalue", [msg], "error", "error", "0"),
        ("dummyvalue1", [msg, msg], "Idle", "ERROR", 10),
        ("dummyvalue2", [], "RUNNING", "Error", -1)
    ]
)
def test_MARTe2StateMachineEvent(configuration_name, messages, nextstate, nextstateerror, timeout):
    setup_writer = marteconfig.StringConfigWriter()
    factory = TFactory()
    example_marte2statemachineevent = MARTe2StateMachineEvent(configuration_name=configuration_name, messages=messages, nextstate=nextstate, nextstateerror=nextstateerror, timeout=timeout)
    

    assert not example_marte2statemachineevent == list([])
    # Assert attributes
    assert example_marte2statemachineevent.configuration_name == configuration_name.upper()
    assert example_marte2statemachineevent.messages == messages
    assert example_marte2statemachineevent.nextstate == nextstate.upper()
    assert example_marte2statemachineevent.nextstateerror == nextstateerror.upper()
    assert example_marte2statemachineevent.timeout == timeout

    # Assert Serializations
    assert example_marte2statemachineevent.serialize()['configuration_name'] == configuration_name.upper()
    assert example_marte2statemachineevent.serialize()['messages'] == [a.serialize() for a in messages]
    assert example_marte2statemachineevent.serialize()['nextstate'] == nextstate.upper()
    assert example_marte2statemachineevent.serialize()['nextstateerror'] == nextstateerror.upper()
    assert example_marte2statemachineevent.serialize()['timeout'] == timeout

    # Assert Deserialization
    new_marte2statemachineevent = MARTe2StateMachineEvent().deserialize(example_marte2statemachineevent.serialize(), factory=factory)
    assert new_marte2statemachineevent.configuration_name.lstrip('+') == configuration_name.upper()
    assert new_marte2statemachineevent.messages == messages
    assert new_marte2statemachineevent.nextstate == nextstate.upper()
    assert new_marte2statemachineevent.nextstateerror == nextstateerror.upper()
    assert new_marte2statemachineevent.timeout == timeout
    
    new_marte2statemachineevent.timeout = 100
    assert not new_marte2statemachineevent == example_marte2statemachineevent
    # Assert config written
    example_marte2statemachineevent.write(setup_writer)
    test_writer = marteconfig.StringConfigWriter()
    test_writer.setTab(1)

    string_content = ''
    if messages:
        for a  in messages:
            a.write(test_writer)
        string_content = str(repr(test_writer)) + '\n'
    assert str(setup_writer) == f'''+{configuration_name.upper()} = {{
    Class = StateMachineEvent
    NextState = "{nextstate.upper()}"
    NextStateError = "{nextstateerror.upper()}"
    Timeout = {int(timeout)}
{string_content}}}'''

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('StateMachineEvent') == MARTe2StateMachineEvent