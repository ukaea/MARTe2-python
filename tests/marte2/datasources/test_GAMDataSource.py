import pytest

from martepy.marte2.datasources import GAMDataSource
from martepy.marte2.datasources.gam_datasource import initialize
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget, QComboBox

from ...utilities import *

@pytest.mark.parametrize(
    "configuration_name",
    [
        ("dummyvalue"),
        ("dummyvalue1"),
        ("dummyvalue2"),
        ("dummyvalue2")
    ]
)
def test_GAMDataSource(configuration_name, load_parameters):
    setup_writer = marteconfig.StringConfigWriter()
    example_gamdatasource = GAMDataSource(configuration_name=configuration_name)
    
    # Assert attributes
    assert example_gamdatasource.configuration_name == configuration_name

    # Assert Serializations
    assert example_gamdatasource.serialize()['configuration_name'] == configuration_name

    # Assert Deserialization
    new_gamdatasource = GAMDataSource().deserialize(example_gamdatasource.serialize())
    assert new_gamdatasource.configuration_name.lstrip('+') == configuration_name

    # Assert config written
    example_gamdatasource.write(setup_writer)

    assert str(setup_writer) == f'''+{configuration_name} = {{
    Class = GAMDataSource\n}}'''

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('GAMDataSource') == GAMDataSource
