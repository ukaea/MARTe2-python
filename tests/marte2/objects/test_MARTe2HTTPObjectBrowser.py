import pytest

from martepy.marte2.objects.http.objectbrowser import MARTe2HTTPObjectBrowser, initialize
from martepy.marte2.gams.message_gam import MARTe2Message
from martepy.marte2.objects.http.directoryresource import MARTe2HttpDirectoryResource
from martepy.marte2.objects.http.messageinterface import MARTe2HttpMessageInterface
import martepy.marte2.configwriting as marteconfig
from martepy.marte2.factory import Factory
from ...utilities import *

@pytest.mark.parametrize(
    "configuration_name, objects, possible_objects, root",
    [
        ("dummyvalue", [], [], "/"),
        ("dummyvalue1", [], [], "/root/"),
        ("dummyvalue2", [], [], "/"),
        ("dummyvalue2", [], [], "/root/")
    ]
)
def test_MARTe2HTTPObjectBrowser(configuration_name, objects, possible_objects, root):
    setup_writer = marteconfig.StringConfigWriter()
    example_marte2httpobjectbrowser = MARTe2HTTPObjectBrowser(configuration_name=configuration_name, objects=objects, root=root)
    
    # Assert attributes
    assert example_marte2httpobjectbrowser.configuration_name == configuration_name
    assert example_marte2httpobjectbrowser.objects == objects
    assert example_marte2httpobjectbrowser.possible_objects == {'HttpObjectBrowser': MARTe2HTTPObjectBrowser,
                    'HttpDirectoryResource': MARTe2HttpDirectoryResource,
                    'HttpMessageInterface': MARTe2HttpMessageInterface,
                    'Message': MARTe2Message}
    assert example_marte2httpobjectbrowser.root == root

    # Assert Serializations
    assert example_marte2httpobjectbrowser.serialize()['configuration_name'] == configuration_name
    assert example_marte2httpobjectbrowser.serialize()['objects'] == objects
    assert example_marte2httpobjectbrowser.serialize()['root'] == root

    # Assert Deserialization
    new_marte2httpobjectbrowser = MARTe2HTTPObjectBrowser().deserialize(example_marte2httpobjectbrowser.serialize())
    assert new_marte2httpobjectbrowser.configuration_name.lstrip('+') == configuration_name
    assert new_marte2httpobjectbrowser.objects == objects
    assert new_marte2httpobjectbrowser.possible_objects == {'HttpObjectBrowser': MARTe2HTTPObjectBrowser,
                    'HttpDirectoryResource': MARTe2HttpDirectoryResource,
                    'HttpMessageInterface': MARTe2HttpMessageInterface,
                    'Message': MARTe2Message}
    assert new_marte2httpobjectbrowser.root == root

    # Assert config written
    example_marte2httpobjectbrowser.write(setup_writer)

    assert str(setup_writer) == f'''+{configuration_name} = {{
    Class = HttpObjectBrowser\n    Root = "{root}"\n}}'''

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('HttpObjectBrowser') == MARTe2HTTPObjectBrowser