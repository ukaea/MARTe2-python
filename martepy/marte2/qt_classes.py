'''
This module is a collection of classes used in the MARTe2 Python repository 
and GUI associated with MARTe2.
'''
import copy

from PyQt5.QtCore import QEvent, QTimer, Qt, pyqtSignal
from PyQt5.QtWidgets import (QCompleter,
                             QHBoxLayout,
                             QLineEdit,
                             QListWidget,
                             QPushButton,
                             QScrollArea,
                             QSizePolicy,
                             QSplitter,
                             QVBoxLayout,
                             QWidget)

from PyQt5.QtWidgets import (
    QGridLayout, QGroupBox, QMessageBox, QMainWindow
)
from martepy.functions.extra_functions import getname
from martepy.marte2.objects import MARTe2Message, MARTe2ConfigurationDatabase
from martepy.marte2.qt_functions import (createGridComboEdit,
                                         createGridLineEdit,
                                         generateUniqueName)

class AddRemoveHBtn(QWidget):
    ''' A generic QWidget for Add, Remove Buttons'''
    def __init__(self, parent=None):
        # We expose the add and remove btn's for the user to then create the connected
        # operations
        super().__init__(parent)
        self.hlayout = QHBoxLayout()
        self.setLayout(self.hlayout)
        self.add_btn = QPushButton("Add")
        self.remove_btn = QPushButton("Remove")
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.hlayout.addWidget(spacer)
        self.hlayout.addWidget(self.add_btn)
        self.hlayout.addWidget(self.remove_btn)

# Define a custom event type
class CustomEvent(QEvent): # pylint: disable=R0903
    ''' A Custom Event override '''
    def __init__(self, event_type):
        super().__init__(QEvent.User)
        self.event_type = event_type

class AutoCompleteLineEdit(QLineEdit):
    ''' This is an autocompleting line edittor for use in the TypeDB '''
    mouse_clicked = pyqtSignal()
    def __init__(self, window, items, app):
        super().__init__()
        self.app = app
        self.window = window
        self.items = items
        self.previous_text = ''
        self.initUI()

    def initUI(self):
        ''' Initialise our UI components '''
        self.completer = QCompleter(self.items)
        self.setCompleter(self.completer)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)

        self.previous_text = ""
        self.mouse_clicked.connect(self.validateInput)
        # Connect textChanged signal to validation slot
        self.textChanged.connect(self.validateInput)

    def mousePressEvent(self, event):
        ''' User is inputting data '''
        if event.button() == Qt.LeftButton:
            # Handle the left mouse button click event
            # Create a custom event and post it to the application
            custom_event = CustomEvent("CustomEventType")
            self.app.postEvent(self.window, custom_event)
        super().mousePressEvent(event)

    # Override the customEvent method to handle custom events
    def customEvent(self, event):
        ''' Override our custom event handler to handle the user input and autocomplete '''
        if event.type() == QEvent.User:
            if event.event_type == "CustomEventType":
                self.completer.complete()

    def validateInput(self):
        ''' Check our input is correct and autocomplete if so. '''
        text = self.text()
        if not text:
            self.completer.complete()
            return

        valid = False
        for item in self.items:
            if text in item:
                valid = True
                break

        if not valid:
            self.setText(self.previous_text)
        else:
            self.previous_text = text

class PanelledListConfig(QWidget):
    ''' This is a generic class widget which splits a window into two sections and 
    create a list object on the left hand panel, leaving the right hand panel open for the user '''
    def __init__(self, parent=None, left_proportion=0.2, right_proportion=0.8, make_list=True):
        super().__init__(parent)
        # VLayout is the top level layout, if you use
        # this in a window and want say, save and close buttons underneath, add it to vlayout.
        self.v_layout = QVBoxLayout()
        self.setLayout(self.v_layout)
        self.splitter = QSplitter()
        self.v_layout.addWidget(self.splitter)
        # Now we have our splitter we need to create our two
        # widgets which will store the layouts for our left and right side panels

        self.left_panel = QWidget()
        self.left_panel_vlayout = QVBoxLayout()
        self.left_panel.setLayout(self.left_panel_vlayout)
        if make_list:
            self.left_list = QListWidget()
            self.left_list.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.left_panel_vlayout.addWidget(self.left_list)
            self.left_list.itemSelectionChanged.connect(self.scheduleEnsureSelection)
        self.splitter.addWidget(self.left_panel)
        # Right panel
        # We leave this blank with a VBoxLayout, the user should primarily interact with
        # the layout however can use the widget to replace it
        self.scroll_area = QScrollArea()
        self.right_panel_wgt = QWidget()
        self.right_panel_vlayout = QVBoxLayout()
        self.right_panel_wgt.setLayout(self.right_panel_vlayout)
        self.right_panel_wgt.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.right_panel_wgt)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.splitter.addWidget(self.scroll_area)
        self.splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Now set user defined proportions
        self.setProportions(left_proportion, right_proportion)

    def scheduleEnsureSelection(self):
        ''' Left list item has changed - most users override this method. '''
        # Use QTimer.singleShot to defer the ensure_selection method
        QTimer.singleShot(0, self.ensureSelection)

    def ensureSelection(self):
        ''' Make sure an actual item is selected and if not, select the first item. '''
        if not self.left_list.selectedItems():
            # If no items are selected, select the first item
            if self.left_list.count() > 0:
                self.left_list.setCurrentRow(0)

    def setProportions(self, left_proportion=0.2, right_proportion=0.8):
        ''' Setup the proportions of our splitter '''
        total_width = self.splitter.width()
        size1 = int(left_proportion * total_width)
        size2 = int(right_proportion * total_width)
        self.splitter.setSizes([size1,size2])

class MsgInfoWidget(QWidget):
    ''' Simplification of the MsgConfigWindow, QWidget which holds the Msg Info. '''
    def __init__(self, parent, msg_namechg, dest_chg, func_chg, mode_chg, wait_chg):
        super().__init__(parent)
        grid_layout = QGridLayout()
        self.setLayout(grid_layout)

        self.msg_name = createGridLineEdit(grid_layout, 0, 'Message Name:', msg_namechg,
                                            finished=True,space=True)
        self.msg_dest = createGridLineEdit(grid_layout, 1, 'Destination:', dest_chg,
                                            space=True)
        self.func = createGridLineEdit(grid_layout, 2, 'Function:', func_chg, space=True)
        self.mode = createGridComboEdit(grid_layout, 3, 'Mode:', mode_chg,
                                        ['ExpectsReply', 'ExpectsIndirectReply'], space=True)
        self.maxwait = createGridLineEdit(grid_layout, 4, 'MaxWait:', wait_chg,
                                            finished=True, space=True)

class MessageConfigWindow(QMainWindow):
    ''' The General Message Config Window which is used in multiple places
    to configure messages in the GUI '''
    def __init__(self, application, app, original, origin, title, close_inst=None,# pylint: disable=R0914, R0915
                 conversion_func=None, sizes=[0.25,0.25,0.5,0.5]) -> None:
        super().__init__()
        self.application = application
        self.app = app
        self.messages = []
        self.setWindowModality(Qt.ApplicationModal)
        self.close_inst = close_inst
        self.conversion_func = conversion_func
        # Set Window Size
        self.setSize(sizes[0],sizes[1],sizes[2],sizes[3])
        self.original = original
        self.origin = origin

        self.setWindowTitle(title)
        self.main_wgt = PanelledListConfig(self, 0.25, 0.75)
        self.central_layout = self.main_wgt.v_layout
        self.setCentralWidget(self.main_wgt)

        self.add_remmsg = AddRemoveHBtn(self.main_wgt.left_panel)
        self.main_wgt.left_panel_vlayout.addWidget(self.add_remmsg)
        self.add_remmsg.add_btn.clicked.connect(self.addMsg)
        self.add_remmsg.remove_btn.clicked.connect(self.remMsg)
        msg_box = QGroupBox("Message")
        # Create a layout for the QGroupBox
        msg_box_layout = QVBoxLayout(msg_box)
        # Set the layout of the QGroupBox
        msg_box.setLayout(msg_box_layout)
        msg_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_wgt.right_panel_vlayout.addWidget(msg_box)

        # Populate msg_box section
        self.grid_wgt = MsgInfoWidget(self, self.msgNameChg, self.destChg, self.funcChg,
                                      self.modeChg, self.waitChg)

        msg_box_layout.addWidget(self.grid_wgt)

        params_box = QGroupBox("Parameters")
        params_box_layout = QVBoxLayout(msg_box)

        params_box.setLayout(params_box_layout)

        self.param_config = PanelledListConfig(params_box,0.25,0.75)
        params_box_layout.addWidget(self.param_config)
        self.param_btns = AddRemoveHBtn()
        self.param_config.left_panel_vlayout.addWidget(self.param_btns)
        self.param_btns.add_btn.clicked.connect(self.addParam)
        self.param_btns.remove_btn.clicked.connect(self.remParam)
        # Right section
        grid_wgt = QWidget()
        grid_layout = QGridLayout()
        grid_wgt.setLayout(grid_layout)

        self.paramname = createGridLineEdit(grid_layout, 0, 'Parameter Name:',
                                               self.paramNameChg, finished=True, space=True)
        self.paramval = createGridLineEdit(grid_layout, 1, 'Parameter Value:',
                                              self.paramValChg, space=True)
        vspacer = QWidget()
        vspacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.param_config.right_panel_vlayout.addWidget(grid_wgt)
        self.param_config.right_panel_vlayout.addWidget(vspacer)

        msg_box_layout.addWidget(params_box)

        vspacer = QWidget()
        vspacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        msg_box_layout.addWidget(vspacer)

        btn_holder = QWidget()
        btn_hlayout = QHBoxLayout()
        btn_holder.setLayout(btn_hlayout)
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        btn_hlayout.addWidget(spacer)
        self.save_btn.clicked.connect(self.save)
        self.cancel_btn.clicked.connect(self.close)
        btn_hlayout.addWidget(self.save_btn)
        btn_hlayout.addWidget(self.cancel_btn)

        self.main_wgt.right_panel_vlayout.addWidget(btn_holder)

        self.param_config.left_list.currentItemChanged.connect(self.paramChanged)
        self.main_wgt.left_list.currentItemChanged.connect(self.msgChanged)
        self.loadMessages(copy.deepcopy(self.original))
        self.ignore_close_event = False
        self.show()

    def save(self):
        ''' Save the current status of the messages '''
        if self.conversion_func:
            self.conversion_func(self.origin, self.messages)
        else:
            self.origin.clear()
            self.origin += self.messages
        self.ignore_close_event = True
        self.close()
        self.close_inst = None

    def setSize(self,x_pos=0.4,y_pos=0.3,width=0.3,height=0.2):
        """Set the Window Size
        """
        # Set Window Size
        self.screen = self.app.primaryScreen()
        self.size = self.screen.size()
        self.setGeometry(
            int(self.size.width() * x_pos),
            int(self.size.height() * y_pos),
            int(self.size.width() * width),
            int(self.size.height() * height),
        )
        self.setCentralWidget(QWidget(self))

    def closeEvent(self, event) -> None:
        ''' Interrupt the close event, prompt the user if they want to save changes '''
        # Prompt user that we should save
        if self.ignore_close_event:
            return
        if not self.original == self.messages:
            buttons = QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            reply = QMessageBox.question(self, 'Save Changes',
                                         "Do you want to save changes?",
                                         buttons,
                                         QMessageBox.Save)
            if reply == QMessageBox.Save:
                self.save()
            elif reply == QMessageBox.Discard:
                self.close_inst = None
            elif reply == QMessageBox.Cancel:
                event.ignore()

    def loadMessages(self, messages):
        ''' Load up the current messages provided '''
        list_widget = self.main_wgt.left_list
        # Message format is:
        # Assume these are defined as Msg Objects
        self.messages = messages
        list_widget.clear()
        for message in messages:
            list_widget.addItem(getname(message))

        list_widget.setCurrentRow(0)

    def msgChanged(self, item):
        ''' The user may have selected a different message to configure, 
        first ensure it is a legitimate item. '''
        if item:
            try:
                selected_msg = next(a for a in self.messages if getname(a) == item.text())
                self.displayMsg(selected_msg)
            except StopIteration:
                pass
        else:
            self.grid_wgt.msg_name.setText('')
            self.grid_wgt.msg_dest.setText('')
            self.grid_wgt.func.setText('')
            self.grid_wgt.maxwait.setText('')
            self.grid_wgt.mode.setCurrentText('ExpectsReply')
            self.param_config.left_list.clear()

    def paramChanged(self, item):
        ''' User has changed the parameter name '''
        list_widget = self.main_wgt.left_list
        list_item = list_widget.currentItem()
        try:
            if list_item:
                selected_msg = next(a for a in self.messages if getname(a) == list_item.text())
                if item:
                    key = next(a for a in list(selected_msg.parameters.objects.keys()) if
                               a == item.text())
                    self.displayParameter(key, selected_msg.parameters.objects[key])
                    return
            self.paramname.setText('')
            self.paramval.setText('')
        except StopIteration:
            pass

    def addParam(self):
        ''' User has added a parameter '''
        list_widget = self.param_config.left_list
        existing_names = [list_widget.item(index).text() for index in range(list_widget.count())]
        new_name = generateUniqueName(existing_names, 'func')
        try:
            msg_list_widget = self.main_wgt.left_list
            list_item = msg_list_widget.currentItem()
            selected_msg = next(a for a in self.messages if getname(a) == list_item.text())
            list_widget.addItem(new_name)
            selected_msg.parameters.objects[new_name] = '1'
            self.param_config.left_list.setCurrentRow(self.param_config.left_list.count()-1)
        except StopIteration:
            pass

    def remParam(self):
        ''' User has removed a parameter '''
        list_widget = self.main_wgt.left_list
        list_item = list_widget.currentItem()
        try:
            selected_msg = next(a for a in self.messages if getname(a) == list_item.text())
            list_widget = self.param_config.left_list
            del selected_msg.parameters.objects[list_widget.currentItem().text()]
            list_widget.takeItem(list_widget.row(list_widget.currentItem()))
        except StopIteration:
            pass

    def addMsg(self):
        ''' Add a new message '''
        list_widget = self.main_wgt.left_list
        existing_names = [list_widget.item(index).text() for index in range(list_widget.count())]
        new_name = generateUniqueName(existing_names, 'Message')
        new_msg = MARTe2Message('+' + new_name)
        new_msg.parameters = MARTe2ConfigurationDatabase(objects={})
        self.messages += [new_msg]
        list_widget.addItem(new_msg.configuration_name.replace('+', ''))
        list_widget.setCurrentRow(list_widget.count()-1)

    def displayMsg(self, msg):
        ''' Display the provided message in our QMessage widget '''
        self.grid_wgt.msg_name.setText(msg.configuration_name.replace('+', ''))
        self.grid_wgt.msg_dest.setText(msg.destination)
        self.grid_wgt.func.setText(msg.function)
        self.grid_wgt.maxwait.setText(str(msg.maxwait))
        self.grid_wgt.mode.setCurrentText(msg.mode)
        self.param_config.left_list.clear()
        for key, _ in msg.parameters.objects.items():
            self.param_config.left_list.addItem(key)
        self.param_config.left_list.setCurrentRow(0)


    def displayParameter(self, key, value):
        ''' Display the current parameter '''
        self.paramname.setText(key)
        self.paramval.setText(value)

    def remMsg(self):
        ''' Remove the currently selected message '''
        list_widget = self.main_wgt.left_list
        list_item = list_widget.currentItem()
        try:
            if list_item:
                selected_msg = next(a for a in self.messages if getname(a) == list_item.text())
                self.messages = [a for a in self.messages if not getname(a) == list_item.text()]
                del selected_msg
                list_widget.takeItem(list_widget.row(list_item))
        except StopIteration:
            pass

    def msgNameChg(self):
        ''' Change the message name '''
        list_widget = self.main_wgt.left_list
        list_item = list_widget.currentItem()
        try:
            if list_item:
                selected_msg = next(a for a in self.messages if getname(a) == list_item.text())
                selected_msg.configuration_name = '+' + self.grid_wgt.msg_name.text()
                list_item.setText(self.grid_wgt.msg_name.text())
        except StopIteration:
            pass

    def destChg(self):
        ''' Change to the destination of the message '''
        list_widget = self.main_wgt.left_list
        list_item = list_widget.currentItem()
        try:
            if list_item:
                selected_msg = next(a for a in self.messages if getname(a) == list_item.text())
                selected_msg.destination = self.grid_wgt.msg_dest.text()
        except StopIteration:
            pass

    def funcChg(self):
        ''' Change the function of the message '''
        list_widget = self.main_wgt.left_list
        list_item = list_widget.currentItem()
        try:
            if list_item:
                selected_msg = next(a for a in self.messages if getname(a) == list_item.text())
                selected_msg.function = self.grid_wgt.func.text()
        except StopIteration:
            pass

    def modeChg(self):
        ''' Change the mode of the message '''
        list_widget = self.main_wgt.left_list
        list_item = list_widget.currentItem()
        try:
            if list_item:
                selected_msg = next(a for a in self.messages if getname(a) == list_item.text())
                selected_msg.mode = self.grid_wgt.mode.currentText()
        except StopIteration:
            pass

    def waitChg(self):
        ''' Change the wait time of the message - note, -1 is infinite time '''
        list_widget = self.main_wgt.left_list
        list_item = list_widget.currentItem()
        try:
            if list_item:
                selected_msg = next(a for a in self.messages if getname(a) == list_item.text())
                selected_msg.maxwait = self.grid_wgt.maxwait.text()
        except StopIteration:
            pass

    def paramNameChg(self):
        ''' The parameter name has been changed '''
        list_widget = self.main_wgt.left_list
        list_item = list_widget.currentItem()
        try:
            if list_item:
                selected_msg = next(a for a in self.messages if getname(a) == list_item.text())
                list_widget = self.param_config.left_list.currentItem()
                if list_widget:
                    value = copy.copy(selected_msg.parameters.objects[list_widget.text()])
                    del selected_msg.parameters.objects[list_widget.text()]
                    selected_msg.parameters.objects[self.paramname.text()] = value
                    self.param_config.left_list.currentItem().setText(self.paramname.text())
        except StopIteration:
            pass

    def paramValChg(self):
        ''' Parameter value has been changed '''
        list_widget = self.main_wgt.left_list
        list_item = list_widget.currentItem()
        try:
            if list_item:
                selected_msg = next(a for a in self.messages if getname(a) == list_item.text())
                list_widget = self.param_config.left_list.currentItem()
                if list_widget:
                    selected_msg.parameters.objects[list_widget.text()] = self.paramval.text()
        except StopIteration:
            pass
