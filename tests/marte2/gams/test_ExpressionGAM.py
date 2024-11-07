import pytest

from martepy.marte2.gams import ExpressionGAM
from martepy.marte2.gams.expression_gam import initialize
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget, QTextEdit

from ...utilities import *

@pytest.mark.parametrize(
    "configuration_name, expression, input_signals, output_signals",
    [
        ("dummyvalue",'Constantf = COnstanti * 8',[('Constantf',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32'}})], [('Constanti',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})]),
        ("dummyvalue1",'Helloout = Hello * World',[('Hello',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}}),('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float64','Alias':'HW'}})],[('Helloout',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint64'}})]),
        ("dummyvalue2",'dout = !!World',[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3}})],[('dout',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint64','NumberOfElements':3}})]),
        ("dummyvalue2",'small_int = !World',[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3,'NumberOfDimensions':'1'}})],[('small_int',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint8','NumberOfElements':3,'NumberOfDimensions':'1'}})])
    ]
)
def test_ExpressionGAM(configuration_name, expression, input_signals, output_signals, load_parameters):
    setup_writer = marteconfig.StringConfigWriter()
    example_expressiongam = ExpressionGAM(configuration_name, expression=expression, input_signals=input_signals, output_signals=output_signals)
    
    # Assert attributes
    assert example_expressiongam.configuration_name == configuration_name
    assert example_expressiongam.expression == expression
    assert example_expressiongam.output_signals == output_signals
    assert example_expressiongam.input_signals == input_signals

    # Assert Serializations
    assert example_expressiongam.serialize()['configuration_name'] == configuration_name
    assert example_expressiongam.serialize()['parameters']['expression'] == expression
    assert example_expressiongam.serialize()['outputsb'] == output_signals
    assert example_expressiongam.serialize()['inputsb'] == input_signals

    # Assert Deserialization
    new_expressiongam = ExpressionGAM().deserialize(example_expressiongam.serialize())
    assert new_expressiongam.configuration_name.lstrip('+') == configuration_name
    assert new_expressiongam.expression == expression
    assert new_expressiongam.output_signals == output_signals
    assert new_expressiongam.input_signals == input_signals

    # Assert config written
    example_expressiongam.write(setup_writer)
    test_writer = writeSignals_section(input_signals, output_signals)

    assert str(setup_writer) == f'+{configuration_name} = {{\n    Class = MathExpressionGAM\n    Expression = "{expression}"\n{str(test_writer)}\n}}'

    example_expressiongam.loadParameters(load_parameters, GAMNode(example_expressiongam))

    assert len(load_parameters.configbarBox) == 8
    classes = [QLabel, QLineEdit, QPushButton, QLabel, QLineEdit, QPushButton, QLabel, QTextEdit]
    default_text = ['Number of input signals: ', str(len(example_expressiongam.input_signals)), 'Configure Signals',
                    'Number of output signals: ', str(len(example_expressiongam.output_signals)), 'Configure Signals', 'Expression: ', '']
    test_text = [True, True, True, True, True, True, True, False]
    for i in range(8):
        assert load_parameters.configbarBox.itemAt(i).widget().__class__ == classes[i]
        if test_text[i]:
            assert load_parameters.configbarBox.itemAt(i).widget().text() == default_text[i]

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('ExpressionGAM') == ExpressionGAM
