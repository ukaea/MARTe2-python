''' Pythonic representation of the Message GAM'''

import copy

from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QWidget,
    QSizePolicy,
)
from qtpy.QtWidgets import QVBoxLayout

from martepy.marte2.gam import MARTe2GAM
from martepy.marte2.objects.message import MARTe2Message
from martepy.marte2.qt_classes import AddRemoveHBtn, PanelledListConfig, MessageConfigWindow
from martepy.marte2.objects.referencecontainer import MARTe2ReferenceContainer
from martepy.marte2.qt_functions import (addComboEdit,
                                         addInputSignalsSection,
                                         createComboEdit,
                                         createLineEdit,
                                         defineSaveCancelButtons,
                                         generateUniqueName,
                                         recursivelySetEnabled,
                                         setSize,
                                         showErrorDialog,
                                         textExistsInListWidget)
from martepy.marte2.objects.configuration_database import MARTe2ConfigurationDatabase
from martepy.functions.extra_functions import getname, findIndexByDictKey
from martepy.marte2.objects.statemachine.eventtrigger import MARTe2EventConditionTrigger

class MFactory(): # pylint: disable=R0903
    ''' Basic hard wired factory for the MessageGAMs sub components '''
    def create(self, name='EventConditionTrigger'):
        ''' Create function for building the class '''
        if name == 'EventConditionTrigger':
            return MARTe2EventConditionTrigger
        if name == 'ReferenceContainer':
            return MARTe2ReferenceContainer
        if name == 'ConfigurationDatabase':
            return MARTe2ConfigurationDatabase
        if name == 'Message':
            return MARTe2Message
        raise ValueError(f"""Object type not found in factory for MessageGAM,
 this is a bespoke factory class, check the message_gam.py. Name not found: {name}""")

class MessageGAM(MARTe2GAM):
    ''' Pythonic representation of the Message GAM'''
    def __init__(self,
                    configuration_name: str = 'MessageGAM',
                    input_signals: list = [],
                    output_signals: list = [],
                    triggeron: int = 1,
                    events = None,
                ):
        self.triggeron = triggeron
        self.mfactory = MFactory()
        self.events = events # Should be a reference container object
        if not self.events:
            self.events = MARTe2ReferenceContainer('+Events')

        #assert all(('Default' in d['MARTeConfig'] for n, d in output_signals))
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'MessageGAM',
                input_signals = input_signals,
                output_signals = output_signals,
            )

    def writeGamConfig(self, config_writer):
        ''' Basic GAM Configuration Write up '''
        config_writer.writeNode("TriggerOnChange",self.triggeron)
        self.events.write(config_writer)

    def serialize(self):
        ''' Serialize the object '''
        res: dict = super().serialize()
        res['parameters']['triggeron'] = self.triggeron
        # Need to serialize this
        if self.events:
            res['parameters']['events'] = self.events.serialize()
        res['label'] = "MessageGAM"
        res['block_type'] = 'MessageGAM'
        res['class_name'] = 'MessageGAM'
        res['title'] = f"{self.configuration_name} (MessageGAM)"
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True) -> bool:
        ''' Deserialize the object '''
        super().deserialize(data, hashmap, restore_id)
        self.triggeron = data['parameters']["triggeron"]
        # Need to convert our events objects to messages and parameters
        self.events = MARTe2ReferenceContainer().deserialize(data['parameters']["events"],
                                                             factory=self.mfactory)
        return self

    @staticmethod
    def loadParameters(mainpanel_instance, node):
        """This function is intended to be for the GUI where it can call the
        static instance of the class directly to generate
        the appropriate parameter modifier for the node in XMARTe2.
        """
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        addInputSignalsSection(mainpanel_instance, node, False, False)
        mainpanel_instance.configbarBox.addWidget(spacer, 0, 2)

        addComboEdit(mainpanel_instance, node, 'Trigger on Change: ',
                     'triggeron', 2, 0, ['1','0'])

        def runWindow():
            mainpanel_instance.parent.newwindow = EventsWindow(mainpanel_instance.parent, node)
        config_btn = QPushButton("Configure Events")
        config_btn.clicked.connect(runWindow)
        mainpanel_instance.configbarBox.addWidget(config_btn, 2, 2)
        mainpanel_instance.configbarBox.addWidget(spacer, 2, 3)

class EventsWindow(QMainWindow):
    ''' Event Configuration window for the MessageGAM '''
    def __init__(self, parent=None, node=None):
        super().__init__(parent)
        self.node = node
        self.events = copy.deepcopy(self.node.parameters['events'])
        self.setWindowTitle(f"Events configuration for: {getname(self.node)}")

        self.msg_window = None
        setSize(self, self.parent().app, 0.225,0.25,0.55,0.5)

        self.main_wgt = PanelledListConfig(self, 0.25, 0.75)

        top_layout = self.main_wgt.v_layout
        self.setCentralWidget(self.main_wgt)

        # Organise left panel
        for event in self.events['objects']:
            # Need to get name from event and define how it is defined
            newitem = QListWidgetItem(event["configuration_name"].strip('+'))
            self.main_wgt.left_list.addItem(newitem)

        self.left_btns = AddRemoveHBtn()
        self.main_wgt.left_panel_vlayout.addWidget(self.left_btns)
        self.left_btns.add_btn.clicked.connect(self.addEvent)
        self.main_wgt.left_list.itemSelectionChanged.connect(self.selectedEventChanged)
        self.left_btns.remove_btn.clicked.connect(self.removeEvent)
        defineSaveCancelButtons(top_layout, self.save, self.cancel)

        # Now organise right hand panel
        self.eventname = createLineEdit(self.main_wgt.right_panel_vlayout,
                                        'Event Name:', self.eventNameChg)

        trigger_box = self.defineTriggerBox()

        self.msg_wgt = QWidget()
        hlayout = QHBoxLayout()
        self.msg_wgt.setLayout(hlayout)
        spacerb = QWidget()
        spacerb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        hlayout.addWidget(spacerb)
        self.config_msgs = QPushButton("Configure Messages")
        self.config_msgs.clicked.connect(self.openMsgs)
        hlayout.addWidget(self.config_msgs)

        self.main_wgt.right_panel_vlayout.addWidget(trigger_box)
        self.main_wgt.right_panel_vlayout.addWidget(self.msg_wgt)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_wgt.right_panel_vlayout.addWidget(spacer)

        if len(self.events) == 0:
            recursivelySetEnabled(self.main_wgt.right_panel_vlayout, False)
        else:
            self.main_wgt.left_list.setCurrentRow(0)
        self.show()

    def defineTriggerBox(self):
        ''' Reduction of statements in init - builds the trigger box '''
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Now add group box for defining the event trigger
        trigger_box = QGroupBox("Event Trigger:")
        trig_grp_layout = QVBoxLayout()
        trigger_box.setLayout(trig_grp_layout)

        self.trig_panel_wgt = PanelledListConfig(trigger_box, 0.3, 0.7)
        trig_grp_layout.addWidget(self.trig_panel_wgt)

        self.trig_btns = AddRemoveHBtn()
        self.trig_btns.add_btn.clicked.connect(self.addTrigger)
        self.trig_btns.remove_btn.clicked.connect(self.remTrigger)
        self.trig_panel_wgt.left_panel_vlayout.addWidget(self.trig_btns)
        signal_names = [a.label for a in self.node.inputs]
        self.trig_sig = createComboEdit(self.trig_panel_wgt.right_panel_vlayout,
                                        'Signal Name:', self.trigNameChg, signal_names)
        self.trig_val = createLineEdit(self.trig_panel_wgt.right_panel_vlayout,
                                       'Trigger Value:', self.trigValChg)
        self.trig_panel_wgt.left_list.itemSelectionChanged.connect(self.selectedTrigChanged)
        self.trig_panel_wgt.right_panel_vlayout.addWidget(spacer)
        return trigger_box

    def eventNameChg(self, value):
        ''' Event Name has changed '''
        selected_item = self.main_wgt.left_list.currentItem()
        event = selected_item.text()
        selected_item.setText(value)
        index = findIndexByDictKey(self.events['objects'], 'configuration_name', event)
        self.events['objects'][index]['configuration_name'] = '+' + value

    def openMsgs(self):
        ''' Open the Message Window '''
        selected_item = self.main_wgt.left_list.currentItem()
        if selected_item:
            event = selected_item.text()
            index = findIndexByDictKey(self.events['objects'], 'configuration_name', event)
            msgs = self.events["objects"][index]['objects']
            actual_msgs = [MARTe2Message().deserialize(a) for a in msgs]
            origin = self.events["objects"][index]['objects']
            self.msg_window = None
            self.msg_window = MessageConfigWindow(self.node.application,
                                                  self.node.application.app,
                                                  actual_msgs, origin,
                                                  f"Configure Event Messages for event {event}",
                                                  self.msg_window,
                                                  self.convert)

    def convert(self, original, msgs):
        ''' Convert the messages to the GUI acceptable format '''
        # Convert from MARTe2Message to a serialized method so we can
        # save this in .xmt format without changing external code in the GUI
        original.clear()
        original += [a.serialize() for a in msgs]

    def save(self):
        ''' Save our changes '''
        self.node.parameters['events'] = copy.deepcopy(self.events)
        self.close()

    def cancel(self):
        ''' Close without saving '''
        self.close()

    def trigNameChg(self, new_trig_idx):
        ''' Selected trigger has changed '''
        new_trig_name = self.trig_sig.itemText(new_trig_idx)
        found_items = self.trig_panel_wgt.left_list.findItems("*", QtCore.Qt.MatchWildcard)
        if new_trig_name not in [item.text() for item in found_items]:
            selected_item = self.main_wgt.left_list.currentItem()
            if selected_item:
                event = selected_item.text()
                index = findIndexByDictKey(self.events['objects'], 'configuration_name', event)
                trig_name = self.trig_panel_wgt.left_list.currentItem()
                if trig_name:
                    old_trig_name = trig_name.text()
                    try:
                        value = self.events['objects'][index]['eventtriggers'][old_trig_name]
                        del self.events['objects'][index]['eventtriggers'][old_trig_name]
                        self.events['objects'][index]['eventtriggers'][new_trig_name] = value
                        trig_name.setText(new_trig_name)
                    except (AttributeError, ValueError):
                        pass
        else:
            showErrorDialog("""This signal is already in use, you cannot
 have multiple triggers set to the same signal input.""")
            self.trig_sig.currentIndexChanged.disconnect()
            self.trig_sig.setCurrentText(self.trig_panel_wgt.left_list.currentItem().text())
            self.trig_sig.currentIndexChanged.connect(self.trigNameChg)

    def trigValChg(self, value):
        ''' Trigger value has changed '''
        selected_item = self.main_wgt.left_list.currentItem()
        if selected_item:
            event = selected_item.text()
            index = findIndexByDictKey(self.events['objects'], 'configuration_name', event)
            trig_name = self.trig_panel_wgt.left_list.currentItem()
            if trig_name:
                trig_name = trig_name.text()
                self.events['objects'][index]['eventtriggers'][trig_name] = value

    def addTrigger(self):
        ''' Add a trigger to our message '''
        event = self.eventname.text()
        index = findIndexByDictKey(self.events['objects'], 'configuration_name', event)
        if not self.events['objects'][index]['eventtriggers']:
            recursivelySetEnabled(self.trig_panel_wgt.right_panel_vlayout, True)
        try:
            # In future this should get the next unique label name -
            # for now, just gives the first one
            count = 0
            defaultsignal = None
            while count < len(self.node.inputs):
                if textExistsInListWidget(self.trig_panel_wgt.left_list,
                                          self.node.inputs[count].label):
                    count += 1
                    continue
                defaultsignal = self.node.inputs[count].label

            if defaultsignal is None:
                showErrorDialog("All available signals have defined triggers")
                return
        except (AttributeError, ValueError):
            showErrorDialog("""No signals available in the MessageGAM
 to select as the trigger source.""")
            return
        new_trigger = QListWidgetItem(defaultsignal)
        self.trig_panel_wgt.left_list.addItem(new_trigger)
        self.trig_panel_wgt.left_list.setCurrentItem(new_trigger)
        self.events['objects'][index]['eventtriggers'][defaultsignal] = '0'
        # Now set the lineedit values
        index = self.trig_sig.findText(defaultsignal)
        self.trig_sig.currentIndexChanged.disconnect()
        self.trig_sig.setCurrentIndex(index)
        self.trig_sig.currentIndexChanged.connect(self.trigNameChg)
        self.trig_val.setText('0')

    def remTrigger(self):
        ''' Remove the trigger '''
        event = self.eventname.text()
        index = findIndexByDictKey(self.events['objects'], 'configuration_name', event)
        selected_item = self.trig_panel_wgt.left_list.currentItem()
        if selected_item:
            del self.events['objects'][index]['eventtriggers'][selected_item.text()]
            currentRow = self.trig_panel_wgt.left_list.currentRow()
            self.trig_panel_wgt.left_list.takeItem(currentRow)
            if currentRow > 0:
                self.trig_panel_wgt.left_list.setCurrentRow(currentRow - 1)
            else:
                self.trig_panel_wgt.left_list.setCurrentRow(0)
        if not self.events['objects'][index]['eventtriggers']:
            recursivelySetEnabled(self.trig_panel_wgt.right_panel_vlayout, False)

    def addEvent(self):
        ''' Add the event '''
        if len(self.events) == 0:
            recursivelySetEnabled(self.main_wgt.right_panel_vlayout, True)
        newevent = self.defaultEvent()
        current_item = QListWidgetItem(newevent['configuration_name'].lstrip('+'))
        self.main_wgt.left_list.addItem(current_item)
        self.main_wgt.left_list.setCurrentItem(current_item)
        self.eventname.textChanged.disconnect()
        self.eventname.setText(newevent['configuration_name'].lstrip('+'))
        self.eventname.textChanged.connect(self.eventNameChg)
        self.events['objects'] += [newevent]
        recursivelySetEnabled(self.trig_panel_wgt.right_panel_vlayout, False)

    def selectedEventChanged(self):
        ''' User has selected a different event case '''
        # We can probably reuse the event change state easily here
        # by activating the selected trig change and selected msg change
        # if those lists have length, select the first index.
        selected_item = self.main_wgt.left_list.currentItem()
        if selected_item:
            event = selected_item.text()
            index = findIndexByDictKey(self.events['objects'], 'configuration_name', event)
            self.eventname.textChanged.disconnect()
            self.eventname.setText(event)
            self.eventname.textChanged.connect(self.eventNameChg)
            # Remove all previous items from left lists for trig and msg
            self.trig_panel_wgt.left_list.clear()
            if index != -1:
                trig_names = list(self.events['objects'][index]['eventtriggers'])
                self.trig_panel_wgt.left_list.addItems(trig_names)
                self.trig_panel_wgt.left_list.update()
                # Now activate those
                if len(trig_names) > 0:
                    self.trig_panel_wgt.left_list.setCurrentRow(0)
                    recursivelySetEnabled(self.trig_panel_wgt.right_panel_vlayout, True)
                else:
                    recursivelySetEnabled(self.trig_panel_wgt.right_panel_vlayout, False)

    def selectedTrigChanged(self):
        ''' User has changed the trigger selected '''
        selected_item = self.main_wgt.left_list.currentItem()
        if selected_item:
            # Hotfix for badly displayed error during population
            self.trig_sig.currentIndexChanged.disconnect()
            event = selected_item.text()
            index = findIndexByDictKey(self.events['objects'], 'configuration_name', event)
            trig_name = self.trig_panel_wgt.left_list.currentItem()
            try:
                if trig_name:
                    trig_name = trig_name.text()
                    index = self.trig_sig.findText(trig_name)
                    self.trig_sig.setCurrentIndex(index)
                    self.trig_val.setText(self.events['objects'][index]['eventtriggers'][trig_name])
            except (AttributeError, ValueError):
                pass
            self.trig_sig.currentIndexChanged.connect(self.trigNameChg)

    def defaultEvent(self):
        ''' Return a default event configuration '''
        existing_names = [d['configuration_name'].lstrip('+') for d in self.events['objects']]
        new_name = generateUniqueName(existing_names, 'NewEvent')
        return MARTe2EventConditionTrigger('+' + new_name, eventtriggers={}, msgs=[]).serialize()

    def removeEvent(self):
        ''' Remove the current event '''
        selected_item = self.main_wgt.left_list.currentItem()

        def isObj(d):
            return d['configuration_name'].lstrip('+') != selected_item.text()

        if selected_item:
            self.events['objects'] = [d for d in self.events['objects'] if isObj(d)]
            currentRow = self.main_wgt.left_list.currentRow()
            self.main_wgt.left_list.takeItem(currentRow)
            if currentRow > 0:
                self.main_wgt.left_list.setCurrentRow(currentRow-1)
            else:
                self.main_wgt.left_list.setCurrentRow(0)
            if len(self.events) == 0:
                recursivelySetEnabled(self.main_wgt.right_panel_vlayout, False)


def initialize(factory, plugin_datastore) -> None:
    ''' Initialize the object with the factory '''
    factory.registerBlock("MessageGAM", MessageGAM, plugin_datastore)
