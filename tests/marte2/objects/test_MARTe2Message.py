import pytest

from martepy.marte2.objects.message import MARTe2Message, initialize
from martepy.marte2.objects.configuration_database import MARTe2ConfigurationDatabase
from martepy.functions.extra_functions import isint, isfloat
import martepy.marte2.configwriting as marteconfig
from martepy.marte2.factory import Factory

from ...utilities import *



@pytest.mark.parametrize(
    "configuration_name, destination, function, maxwait, mode, parameters",
    [
        ("dummyvalue", "StateMachine", "GOTOERROR", "-1", "ExpectsReply", MARTe2ConfigurationDatabase()),
        ("dummyvalue1", "EPICSCAInterface", "Start", "100", "ExpectsIndirectReply", MARTe2ConfigurationDatabase()),
        ("dummyvalue2", "App", "PrepareNextState", -1, "ExpectsIndirectReply", MARTe2ConfigurationDatabase(objects={'param1':'Idle'})),
        ("dummyvalue2", "EPICSCAInterface.PV_STATUS", "CAPut", 100, "ExpectsReply", MARTe2ConfigurationDatabase(objects={'param1':1}))
    ]
)
def test_MARTe2Message(configuration_name, destination, function, maxwait, mode, parameters):
    setup_writer = marteconfig.StringConfigWriter()
    example_marte2message = MARTe2Message(configuration_name=configuration_name, destination=destination, function=function, maxwait=maxwait, mode=mode, parameters=parameters)
    
    assert not example_marte2message == list([])
    # Assert attributes
    assert example_marte2message.configuration_name == configuration_name
    assert example_marte2message.destination == destination
    assert example_marte2message.function == function
    assert example_marte2message.maxwait == maxwait
    assert example_marte2message.mode == mode
    assert example_marte2message.parameters == parameters

    # Assert Serializations
    assert example_marte2message.serialize()['configuration_name'] == configuration_name
    assert example_marte2message.serialize()['destination'] == destination
    assert example_marte2message.serialize()['function'] == function
    assert example_marte2message.serialize()['maxwait'] == maxwait
    assert example_marte2message.serialize()['mode'] == mode
    if parameters:
        assert example_marte2message.serialize()['parameters'] == parameters.serialize()

    # Assert Deserialization
    new_marte2message = MARTe2Message().deserialize(example_marte2message.serialize())
    assert new_marte2message.configuration_name.lstrip('+') == configuration_name
    assert new_marte2message.destination == destination
    assert new_marte2message.function == function
    assert new_marte2message.maxwait == maxwait
    assert new_marte2message.mode == mode
    assert new_marte2message.parameters == parameters

    new_marte2message.maxwait = 1000
    assert not new_marte2message == example_marte2message
    del new_marte2message.maxwait
    assert not new_marte2message == example_marte2message
    # Assert config written
    example_marte2message.write(setup_writer)
    string_content = []
    if parameters.objects:
        string_content.append('''\n    +Parameters = {
        Class = ConfigurationDatabase''')
        for key, value in parameters.objects.items():
            value = value if isint(value) or isfloat(value) else f'"{value}"'
            string_content.append(f'        {key} = {value}')
        string_content.append('''    }''')
    string_content = '\n'.join(string_content)

    assert str(setup_writer) == f'''+{configuration_name} = {{
    Class = Message
    Destination = "{destination}"
    Function = "{function}"
    MaxWait = "{maxwait}"
    Mode = "{mode}"{string_content}
}}'''

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('Message') == MARTe2Message