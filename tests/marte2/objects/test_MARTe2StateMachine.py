import pytest

from martepy.marte2.objects.statemachine.machine import MARTe2StateMachine, initialize
from martepy.marte2.objects.statemachine.event import MARTe2StateMachineEvent
from martepy.marte2.objects.referencecontainer import MARTe2ReferenceContainer
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from ...utilities import *

msg = MARTe2Message('GOTOERROR','StateMachine','StopCurrentStateExecution')

@pytest.mark.parametrize(
    "configuration_name, states",
    [
        ("StateMachine",[MARTe2ReferenceContainer(configuration_name='INITIAL', objects=[MARTe2StateMachineEvent(configuration_name='START', messages=[msg], nextstate='error', nextstateerror='error', timeout="0")])]),
        ("dummyvalue1",[MARTe2ReferenceContainer(configuration_name='RUNNING', objects=[MARTe2StateMachineEvent(configuration_name='GOTOERROR', messages=[msg, msg], nextstate='Idle', nextstateerror='Error', timeout=10)])]),
        ("dummyvalue2",[MARTe2ReferenceContainer(configuration_name='ERROR', objects=[MARTe2StateMachineEvent(configuration_name='RESET', messages=[msg], nextstate='ERROR', nextstateerror='ERROR', timeout=-1),
                                                          MARTe2StateMachineEvent(configuration_name='ENTER', messages=[], nextstate='ERROR', nextstateerror='ERROR', timeout=-1)])]),
        ("dummyvalue2",[MARTe2ReferenceContainer(configuration_name='IDLE', objects=[MARTe2StateMachineEvent(configuration_name='GOTORUNNING', messages=[msg], nextstate='RUNNING', nextstateerror='error', timeout="-1")]),
                        MARTe2ReferenceContainer(configuration_name='ERROR', objects=[MARTe2StateMachineEvent(configuration_name='GOTOERROR', messages=[msg], nextstate='RUNNING', nextstateerror='error', timeout="-1")])])
    ]
)
def test_MARTe2StateMachine(configuration_name, states):
    setup_writer = marteconfig.StringConfigWriter()
    factory = TFactory()
    example_marte2statemachine = MARTe2StateMachine(configuration_name=configuration_name, states=states)
    
    assert not example_marte2statemachine == list([])
    # Assert attributes
    assert example_marte2statemachine.configuration_name == configuration_name
    assert example_marte2statemachine.states == states

    # Assert Serializations
    assert example_marte2statemachine.serialize()['configuration_name'] == configuration_name
    assert example_marte2statemachine.serialize()['states'] == [a.serialize() for a in states]

    # Assert Deserialization
    new_marte2statemachine = MARTe2StateMachine().deserialize(example_marte2statemachine.serialize(), factory=factory)
    assert new_marte2statemachine.configuration_name.lstrip('+') == configuration_name
    assert new_marte2statemachine.states == states

    # Assert config written
    example_marte2statemachine.write(setup_writer)
    test_writer = marteconfig.StringConfigWriter()
    test_writer.setTab(1)

    string_content = ''
    if states:
        for a in states:
            a.write(test_writer)
        string_content = str(repr(test_writer)) + '\n'
    assert str(setup_writer) == f'''+{configuration_name} = {{
    Class = StateMachine\n{string_content}}}'''

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('StateMachine') == MARTe2StateMachine