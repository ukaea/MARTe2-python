import pytest

from martepy.marte2.gams import SSMGAM
from martepy.marte2.gams.ssm_gam import initialize
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget, QComboBox

from ...utilities import *

@pytest.mark.parametrize(
    "configuration_name, feedthroughmatrix, inputmatrix, outputmatrix, resetineachstate, samplefrequency, statematrix, input_signals, output_signals",
    [
        ("dummyvalue", "{{{{0 1}}}}", "{{{{1 1}}{{0 1}}}}", "{{{{1 0}}}}", "1", "0.0001", "{{{{0.5 0.5}}{{1.0 2.0}}}}",[('Constant',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32','NumberOfElements':'1','NumberOfDimensions':'1'}})],[('Constanti',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})]),
        ("dummyvalue1", "{{{{50 12}}}}", "{{{{1 13}}{{6 10}}}}", "{{{{3 19}}}}", 0, "0.01", "{{{{0.3 0.9}}{{1.7 3.0}}}}",[('Hello',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}}),('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float64','Alias':'HW'}})],[('Helloout',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint64'}}),('Worldout',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','Alias':'HW'}})]),
        ("dummyvalue2", "{{{{5 12}}}}", "{{{{41 134}}{{670 12}}}}", "{{{{7 18}}}}", 1, "2", "{{{{0.7 0.2}}{{1.6 7.0}}}}",[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3}})],[('dout',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint64','NumberOfElements':3}})]),
        ("dummyvalue2", "{{{{0 1}}}}", "{{{{51 1}}{{50 41}}}}", "{{{{10 10}}}}", "1", 5, "{{{{0.8 0.4}}{{1.4 2.6}}}}",[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3,'NumberOfDimensions':'1'}})],[('small_int',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint8','NumberOfElements':3,'NumberOfDimensions':'1'}})])
    ]
)
def test_SSMGAM(configuration_name, feedthroughmatrix, inputmatrix, outputmatrix, resetineachstate, samplefrequency, statematrix, input_signals, output_signals, load_parameters):
    setup_writer = marteconfig.StringConfigWriter()
    example_ssmgam = SSMGAM(configuration_name, feedthroughmatrix=feedthroughmatrix, input_matrix=inputmatrix, output_matrix=outputmatrix, reset_each_state=resetineachstate, samplefreq=samplefrequency, state_matrix=statematrix, input_signals=input_signals, output_signals=output_signals)
    
    # Assert attributes
    assert example_ssmgam.configuration_name == configuration_name
    assert example_ssmgam.feedthroughmatrix == feedthroughmatrix
    assert example_ssmgam.inputmatrix == inputmatrix
    assert example_ssmgam.outputmatrix == outputmatrix
    assert example_ssmgam.resetineachstate == resetineachstate
    assert example_ssmgam.samplefrequency == samplefrequency
    assert example_ssmgam.statematrix == statematrix
    assert example_ssmgam.output_signals == output_signals
    assert example_ssmgam.input_signals == input_signals

    # Assert Serializations
    assert example_ssmgam.serialize()['configuration_name'] == configuration_name
    assert example_ssmgam.serialize()['parameters']['feedthroughmatrix'] == feedthroughmatrix
    assert example_ssmgam.serialize()['parameters']['inputmatrix'] == inputmatrix
    assert example_ssmgam.serialize()['parameters']['outputmatrix'] == outputmatrix
    assert example_ssmgam.serialize()['parameters']['resetineachstate'] == int(resetineachstate)
    assert example_ssmgam.serialize()['parameters']['samplefrequency'] == float(samplefrequency)
    assert example_ssmgam.serialize()['parameters']['statematrix'] == statematrix
    assert example_ssmgam.serialize()['inputsb'] == input_signals
    assert example_ssmgam.serialize()['outputsb'] == output_signals

    # Assert Deserialization
    new_ssmgam = SSMGAM().deserialize(example_ssmgam.serialize())
    assert new_ssmgam.configuration_name.lstrip('+') == configuration_name
    assert new_ssmgam.feedthroughmatrix == feedthroughmatrix
    assert new_ssmgam.inputmatrix == inputmatrix
    assert new_ssmgam.outputmatrix == outputmatrix
    assert new_ssmgam.resetineachstate == int(resetineachstate)
    assert new_ssmgam.samplefrequency == float(samplefrequency)
    assert new_ssmgam.statematrix == statematrix
    assert new_ssmgam.output_signals == output_signals
    assert new_ssmgam.input_signals == input_signals

    # Assert config written
    example_ssmgam.write(setup_writer)
    test_writer = writeSignals_section(input_signals, output_signals)

    assert str(setup_writer) == f'''+{configuration_name} = {{\n    Class = SSMGAM
    StateMatrix = {statematrix}
    InputMatrix = {inputmatrix}
    OutputMatrix = {outputmatrix}
    FeedthroughMatrix = {feedthroughmatrix}
    ResetInEachState = {resetineachstate}
    SampleFrequency = {samplefrequency}
{str(test_writer)}\n}}'''

    example_ssmgam.loadParameters(load_parameters, GAMNode(example_ssmgam))

    
    classes = [QLabel, QLineEdit, QPushButton, QLabel, QLineEdit, QPushButton,
           QLabel, QLineEdit, QLabel, QLineEdit, QLabel, QLineEdit, QLabel, QLineEdit,
           QLabel, QComboBox, QLabel, QLineEdit]
    default_text = ['Number of input signals: ', str(len(input_signals)), 'Configure Signals', 'Number of output signals: ', str(len(output_signals)), 'Configure Signals',
                    'StateMatrix: ', statematrix,'InputMatrix: ',inputmatrix,'OutputMatrix: ',outputmatrix,'Feed through Matrix: ',
                    feedthroughmatrix, 'Reset in each State:', str(resetineachstate), 'Sample Frequency: ', str(float(samplefrequency))]
    test_text = [True, True, True, True, True, True, True, True, True, True,True, True, True, True,True, False, True, True]
    assert len(load_parameters.configbarBox) == len(classes)
    for i in range(len(classes)):
        assert load_parameters.configbarBox.itemAt(i).widget().__class__ == classes[i]
        if test_text[i]:
            assert load_parameters.configbarBox.itemAt(i).widget().text() == default_text[i]

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('SSMGAM') == SSMGAM
