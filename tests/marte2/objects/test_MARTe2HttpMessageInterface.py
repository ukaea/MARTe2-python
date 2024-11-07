import pytest

from martepy.marte2.objects.http.messageinterface import MARTe2HttpMessageInterface, initialize
from martepy.marte2.objects.message import MARTe2Message
from martepy.marte2.gams.message_gam import MFactory
import martepy.marte2.configwriting as marteconfig
from martepy.marte2.factory import Factory

from ...utilities import *

msg = MARTe2Message('GOTOERROR','StateMachine','StopCurrentStateExecution')

@pytest.mark.parametrize(
    "configuration_name, objects",
    [
        ("dummyvalue", []),
        ("dummyvalue1", [msg]),
        ("dummyvalue2", []),
        ("dummyvalue2", [msg, msg])
    ]
)
def test_MARTe2HttpMessageInterface(configuration_name, objects):
    setup_writer = marteconfig.StringConfigWriter()
    factory = MFactory()
    example_marte2httpmessageinterface = MARTe2HttpMessageInterface(configuration_name=configuration_name, objects=objects)
    
    # Assert attributes
    assert example_marte2httpmessageinterface.configuration_name == configuration_name
    assert example_marte2httpmessageinterface.objects == objects

    # Assert Serializations
    assert example_marte2httpmessageinterface.serialize()['configuration_name'] == configuration_name
    assert example_marte2httpmessageinterface.serialize()['objects'] == [a.serialize() for a in objects]

    # Assert Deserialization
    new_marte2httpmessageinterface = MARTe2HttpMessageInterface().deserialize(example_marte2httpmessageinterface.serialize(),factory=factory)
    assert new_marte2httpmessageinterface.configuration_name.lstrip('+') == configuration_name
    assert new_marte2httpmessageinterface.objects == objects

    # Assert config written
    example_marte2httpmessageinterface.write(setup_writer)

    test_writer = marteconfig.StringConfigWriter()
    test_writer.setTab(1)
    # We assume Messages write correctly as we test that more directly elsewhere
    for object in objects:
        object.write(test_writer)
    newline = '\n'
    if str(repr(test_writer)) == '':
        newline = ''

    assert str(setup_writer) == f'''+{configuration_name} = {{
    Class = HttpMessageInterface\n{str(repr(test_writer))}{newline}}}'''

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('HttpMessageInterface') == MARTe2HttpMessageInterface