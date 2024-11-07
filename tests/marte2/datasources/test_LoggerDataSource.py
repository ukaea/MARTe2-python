import pytest

from martepy.marte2.datasources import LoggerDataSource
from martepy.marte2.datasources.logger_datasource import initialize
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
def test_LoggerDataSource(configuration_name, load_parameters):
    setup_writer = marteconfig.StringConfigWriter()
    example_loggerdatasource = LoggerDataSource(configuration_name=configuration_name)
    
    # Assert attributes
    assert example_loggerdatasource.configuration_name == configuration_name

    # Assert Serializations
    assert example_loggerdatasource.serialize()['configuration_name'] == configuration_name

    # Assert Deserialization
    new_loggerdatasource = LoggerDataSource().deserialize(example_loggerdatasource.serialize())
    assert new_loggerdatasource.configuration_name.lstrip('+') == configuration_name

    # Assert config written
    example_loggerdatasource.write(setup_writer)

    assert str(setup_writer) == f'''+{configuration_name} = {{
    Class = LoggerDataSource\n}}'''

    example_loggerdatasource.loadParameters(load_parameters, GAMNode(example_loggerdatasource))

    classes = [QLabel, QLineEdit, QWidget]
    default_text = ['Number of signals: ', '0']
    assert len(load_parameters.configbarBox) == len(classes)
    for i in range(len(classes)):
        assert load_parameters.configbarBox.itemAt(i).widget().__class__ == classes[i]
        if not(classes[i] == QWidget or classes[i] == QComboBox):
            assert load_parameters.configbarBox.itemAt(i).widget().text() == default_text[i]

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('LoggerDataSource') == LoggerDataSource