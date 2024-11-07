import pytest, pdb

from martepy.marte2.gams import MessageGAM
from martepy.marte2.gams.message_gam import MFactory
from martepy.marte2.objects.referencecontainer import MARTe2ReferenceContainer
from martepy.marte2.objects.statemachine.eventtrigger import MARTe2EventConditionTrigger
from martepy.marte2.objects.configuration_database import MARTe2ConfigurationDatabase
from martepy.marte2.objects.message import MARTe2Message
from martepy.marte2.gams.message_gam import initialize
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget, QComboBox

from ...utilities import *

events = MARTe2ReferenceContainer('Events',[])

msgs = [MARTe2Message('GOTOERROR','StateMachine','StopCurrentStateExecution')]
conditiontrigger = MARTe2EventConditionTrigger(eventtriggers={'Command1':'1'},msgs=msgs)
events.objects = [conditiontrigger]

@pytest.mark.parametrize(
    "configuration_name, events, triggeron, input_signals, output_signals",
    [
        ("dummyvalue", events, "1",[],[('Constant',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})]),
        ("dummyvalue1", events, "0",[('Command1',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}}),('Command2',{'MARTeConfig':{'DataSource':'DDB0','Type':'float64','Alias':'HW'}})],[('PendingMessages1',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}}),('PendingMessages2',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32','Alias':'HW'}})]),
        ("dummyvalue2", events, 1,[],[('Signal1',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3}})]),
        ("dummyvalue2", events, 0,[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3,'NumberOfDimensions':'1'}})],[('PendingMessages1',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})])
    ]
)
def test_MessageGAM(configuration_name, events, triggeron, input_signals, output_signals, load_parameters):
    setup_writer = marteconfig.StringConfigWriter()
    example_messagegam = MessageGAM(configuration_name, triggeron=triggeron,events=events, input_signals=input_signals, output_signals=output_signals)
    
    # Assert attributes
    assert example_messagegam.configuration_name == configuration_name
    assert example_messagegam.triggeron == triggeron
    assert example_messagegam.events == events
    assert example_messagegam.output_signals == output_signals
    assert example_messagegam.input_signals == input_signals

    # Assert Serializations
    assert example_messagegam.serialize()['configuration_name'] == configuration_name
    assert example_messagegam.serialize()['parameters']['triggeron'] == triggeron
    assert example_messagegam.serialize()['parameters']['events'] == events.serialize()
    assert example_messagegam.serialize()['inputsb'] == input_signals
    assert example_messagegam.serialize()['outputsb'] == output_signals

    # Assert Deserialization
    new_messagegam = MessageGAM().deserialize(example_messagegam.serialize())
    assert new_messagegam.configuration_name.lstrip('+') == configuration_name
    assert new_messagegam.triggeron == triggeron
    assert new_messagegam.events == events
    assert new_messagegam.output_signals == output_signals
    assert new_messagegam.input_signals == input_signals

    # Assert config written
    example_messagegam.write(setup_writer)
    event_writer = marteconfig.StringConfigWriter()
    event_writer.tab += 1
    example_messagegam.events.write(event_writer)
    test_writer = writeSignals_section(input_signals, output_signals)

    assert str(setup_writer) == f'''+{configuration_name} = {{\n    Class = MessageGAM
    TriggerOnChange = {triggeron}
{str(event_writer)}\n{str(test_writer)}\n}}'''

    example_messagegam.loadParameters(load_parameters, GAMNode(example_messagegam))

    classes = [QLabel, QLineEdit, QPushButton, QWidget, QLabel, QComboBox, QPushButton, QWidget]
    default_text = ['Number of input signals: ', str(len(input_signals)), 'Configure Signals', '', 'Trigger on Change: ',str(triggeron), 'Configure Events','']
    test_text = [True, True, True, False, True, False, True, False]
    assert len(load_parameters.configbarBox) == len(classes)
    for i in range(len(classes)):
        assert load_parameters.configbarBox.itemAt(i).widget().__class__ == classes[i]
        if test_text[i]:
            assert load_parameters.configbarBox.itemAt(i).widget().text() == default_text[i]

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('MessageGAM') == MessageGAM

def test_mfactory():
    factory = MFactory()
    assert factory.create('EventConditionTrigger') == MARTe2EventConditionTrigger
    assert factory.create('ReferenceContainer') == MARTe2ReferenceContainer
    assert factory.create('ConfigurationDatabase') == MARTe2ConfigurationDatabase
    assert factory.create('Message') == MARTe2Message
    with pytest.raises(Exception) as excinfo:
        factory.create('Fakeobj')
    assert str(excinfo.value) == f"Object type not found in factory for MessageGAM,\n this is a bespoke factory class, check the message_gam.py. Name not found: Fakeobj"

def test_messageGAM_GUI(qapp, load_parameters):
    
    test_gam = MessageGAM('test_message_gam', triggeron=1,events=events, input_signals=[('Command1',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3}})], output_signals=[])
    load_parameters.parent = QWidget()
    load_parameters.parent.app = qapp
    node = GAMNode(test_gam)
    node.inputs = [emptyObject()]
    node.inputs[0].label = 'Signal1'
    test_gam.loadParameters(load_parameters, node)
    load_parameters.configbarBox.itemAt(6).widget().clicked.emit()

    event_wdw = load_parameters.parent.newwindow

    assert event_wdw.main_wgt.left_list.item(0).text() == 'NewEvent'
    assert event_wdw.main_wgt.left_list.count() == 1
    assert event_wdw.trig_panel_wgt.left_list.currentItem().text() == 'Command1'
    assert event_wdw.trig_val.text() == '1'

