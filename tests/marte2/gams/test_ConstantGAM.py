import pytest

from martepy.marte2.gams import ConstantGAM
from martepy.marte2.gams.constant_gam import initialize
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig
from martepy.marte2.config_object import MARTe2ConfigObject

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget

from ...utilities import *

@pytest.mark.parametrize(
    "configuration_name, output_signals",
    [
        ("value",[('Constant',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32','Default':'2'}})]),
        ("Constant",[('Hello',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32','Default':'2'}}),('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float64','Alias':'HW','Default':'3.141'}})]),
        ("HelloWorld",[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3,'Default':'{3.2,6.4,7.5}'}})]),
        ("HelloWorld",[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3,'NumberOfDimensions':'1','Default':'{3.2,6.4,7.5}'}})])
    ]
)
def test_ConstantGAM(configuration_name, output_signals, load_parameters):
    setup_writer = marteconfig.StringConfigWriter()
    example_constantgam = ConstantGAM(configuration_name, output_signals=output_signals)
    
    # Assert attributes
    assert example_constantgam.configuration_name == configuration_name
    assert example_constantgam.output_signals == output_signals

    # Assert Serializations
    assert example_constantgam.serialize()['configuration_name'] == configuration_name
    assert example_constantgam.serialize()['outputsb'] == output_signals
    assert example_constantgam.serialize()['inputsb'] == []

    # Assert Deserialization
    new_constantgam = ConstantGAM().deserialize(example_constantgam.serialize())
    assert new_constantgam.configuration_name.lstrip('+') == configuration_name
    assert example_constantgam.output_signals == output_signals
    assert example_constantgam.input_signals == []

    # Assert config written
    example_constantgam.write(setup_writer)
    test_writer = marteconfig.StringConfigWriter()
    test_writer.tab += 2
    MARTe2ConfigObject.writeSignals(output_signals, test_writer)

    assert str(setup_writer) == f'+{configuration_name} = {{\n    Class = ConstantGAM\n    OutputSignals = {{\n{str(test_writer)}\n    }}\n}}'

    example_constantgam.loadParameters(load_parameters, GAMNode(example_constantgam))

    assert len(load_parameters.configbarBox) == 4
    classes = [QLabel, QLineEdit, QPushButton, QWidget]
    default_text = ['Number of output signals: ', str(len(example_constantgam.output_signals)), 'Configure Signals']
    test_text = [True, True, True, False]
    for i in range(4):
        assert load_parameters.configbarBox.itemAt(i).widget().__class__ == classes[i]
        if test_text[i]:
            assert load_parameters.configbarBox.itemAt(i).widget().text() == default_text[i]

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('ConstantGAM') == ConstantGAM
