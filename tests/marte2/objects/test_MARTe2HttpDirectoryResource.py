import pytest

from martepy.marte2.objects.http.directoryresource import MARTe2HttpDirectoryResource, initialize
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from ...utilities import *

@pytest.mark.parametrize(
    "basedir, configuration_name",
    [
        ("dummyvalue", "dummyvalue"),
        ("dummyvalue1", "dummyvalue1"),
        ("dummyvalue2", "dummyvalue2"),
        ("dummyvalue2", "dummyvalue2")
    ]
)
def test_MARTe2HttpDirectoryResource(basedir, configuration_name):
    setup_writer = marteconfig.StringConfigWriter()
    example_marte2httpdirectoryresource = MARTe2HttpDirectoryResource(basedir=basedir, configuration_name=configuration_name)
    
    # Assert attributes
    assert example_marte2httpdirectoryresource.basedir == basedir
    assert example_marte2httpdirectoryresource.configuration_name == configuration_name

    # Assert Serializations
    assert example_marte2httpdirectoryresource.serialize()['basedir'] == basedir
    assert example_marte2httpdirectoryresource.serialize()['configuration_name'] == configuration_name

    # Assert Deserialization
    new_marte2httpdirectoryresource = MARTe2HttpDirectoryResource().deserialize(example_marte2httpdirectoryresource.serialize())
    assert new_marte2httpdirectoryresource.basedir == basedir
    assert new_marte2httpdirectoryresource.configuration_name.lstrip('+') == configuration_name

    # Assert config written
    example_marte2httpdirectoryresource.write(setup_writer)

    assert str(setup_writer) == f'''+{configuration_name} = {{
    Class = HttpDirectoryResource\n    BaseDir = "{basedir}"\n}}'''

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('HttpDirectoryResource') == MARTe2HttpDirectoryResource