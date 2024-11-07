import pytest

from martepy.marte2.objects.configuration_database import MARTe2ConfigurationDatabase, initialize
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig
from martepy.functions.extra_functions import isint, isfloat

from ...utilities import *

@pytest.mark.parametrize(
    "configuration_name, objects",
    [
        ("dummyvalue", {"param1": "State1"}),
        ("dummyvalue1", {"param1": "State2", "param2": "40"}),
        ("dummyvalue2", {"param2": "1"}),
        ("dummyvalue2", {"param1" :"2","param2": "10", "param3": "57"})
    ]
)
def test_MARTe2ConfigurationDatabase(configuration_name, objects):
    setup_writer = marteconfig.StringConfigWriter()
    example_marte2configurationdatabase = MARTe2ConfigurationDatabase(configuration_name=configuration_name, objects=objects)
    
    # Assert attributes
    assert example_marte2configurationdatabase.configuration_name == configuration_name
    assert example_marte2configurationdatabase.objects == objects

    # Assert Serializations
    assert example_marte2configurationdatabase.serialize()['configuration_name'] == configuration_name
    assert example_marte2configurationdatabase.serialize()['objects'] == objects

    # Assert Deserialization
    new_marte2configurationdatabase = MARTe2ConfigurationDatabase().deserialize(example_marte2configurationdatabase.serialize())
    assert new_marte2configurationdatabase.configuration_name.lstrip('+') == configuration_name
    assert new_marte2configurationdatabase.objects == objects
    
    # Evaluate eqivuancy
    assert new_marte2configurationdatabase == example_marte2configurationdatabase
    new_marte2configurationdatabase.objects = []
    assert not new_marte2configurationdatabase == example_marte2configurationdatabase
    assert not example_marte2configurationdatabase == Factory
    # Assert config written
    example_marte2configurationdatabase.write(setup_writer)
    string_content = []
    for key, value in objects.items():
        value = value if isint(value) or isfloat(value) else f'"{value}"'
        string_content.append(f'    {key} = {value}')

    string_content = '\n'.join(string_content)

    assert str(setup_writer) == f'''+{configuration_name} = {{
    Class = ConfigurationDatabase\n{string_content}\n}}'''

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('ConfigurationDatabase') == MARTe2ConfigurationDatabase