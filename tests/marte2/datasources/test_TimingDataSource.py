import pytest

from martepy.marte2.datasources import TimingDataSource
from martepy.marte2.datasources.timing_datasource import initialize
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
def test_TimingDataSource(configuration_name, load_parameters):
    setup_writer = marteconfig.StringConfigWriter()
    example_timingdatasource = TimingDataSource(configuration_name=configuration_name)
    
    # Assert attributes
    assert example_timingdatasource.configuration_name == configuration_name

    # Assert Serializations
    assert example_timingdatasource.serialize()['configuration_name'] == configuration_name

    # Assert Deserialization
    new_timingdatasource = TimingDataSource().deserialize(example_timingdatasource.serialize())
    assert new_timingdatasource.configuration_name.lstrip('+') == configuration_name

    # Assert config written
    example_timingdatasource.write(setup_writer)

    assert str(setup_writer) == f'''+{configuration_name} = {{
    Class = TimingDataSource\n}}'''

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('TimingDataSource') == TimingDataSource
