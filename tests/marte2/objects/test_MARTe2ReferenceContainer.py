import pytest

from martepy.marte2.objects.referencecontainer import MARTe2ReferenceContainer, initialize
from martepy.marte2.objects.message import MARTe2Message
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from ...utilities import *

msg = MARTe2Message('GOTOERROR','StateMachine','StopCurrentStateExecution')

@pytest.mark.parametrize(
    "configuration_name, objects",
    [
        ("dummyvalue", [msg]),
        ("dummyvalue1", [msg, msg]),
        ("dummyvalue2", [])
    ]
)
def test_MARTe2ReferenceContainer(configuration_name, objects):
    setup_writer = marteconfig.StringConfigWriter()
    factory = TFactory()
    example_marte2referencecontainer = MARTe2ReferenceContainer(configuration_name=configuration_name, objects=objects)
    
    assert not example_marte2referencecontainer == list([])

    # Assert attributes
    assert example_marte2referencecontainer.configuration_name == configuration_name
    assert example_marte2referencecontainer.objects == objects

    # Assert Serializations
    assert example_marte2referencecontainer.serialize()['configuration_name'] == configuration_name
    assert example_marte2referencecontainer.serialize()['objects'] == [a.serialize() for a in objects]

    # Assert Deserialization
    new_marte2referencecontainer = MARTe2ReferenceContainer().deserialize(example_marte2referencecontainer.serialize(), factory=factory)
    assert new_marte2referencecontainer.configuration_name.lstrip('+') == configuration_name
    assert new_marte2referencecontainer.objects == objects

    # Assert config written
    example_marte2referencecontainer.write(setup_writer)
    test_writer = marteconfig.StringConfigWriter()
    test_writer.setTab(1)

    string_content = ''
    if objects:
        for a  in objects:
            a.write(test_writer)
        string_content = str(repr(test_writer)) + '\n'
    assert str(setup_writer) == f'''+{configuration_name} = {{
    Class = ReferenceContainer\n{string_content}}}'''

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('ReferenceContainer') == MARTe2ReferenceContainer