'''
This module is a collection of useful functions throughout the GUI aspects
of the MARTe2 Python repository.
'''
import copy
from functools import partial

from PyQt5.QtWidgets import (QComboBox,
                             QHBoxLayout,
                             QLabel,
                             QLayout,
                             QLineEdit,
                             QMessageBox,
                             QPushButton,
                             QSizePolicy,
                             QWidget,
                             QTextEdit)
from martepy.marte2.objects.configuration_database import MARTe2ConfigurationDatabase
from martepy.marte2.objects.message import MARTe2Message
from martepy.marte2.signal_names_wdw import SignalWdw


def textChangeOut(wdgt, node, default, epics, type_input, datasource=None, # pylint: disable=R0914
        samples=None):
    ''' This function is used to handle when a item has changed for a signal definition
    in a table item. '''
    # Get current number of outputs and add the missing ones or remove.
    if wdgt.text().isdigit():
        if not datasource:  # determine if the node is a datasource itself
            datasource = '' if type_input else node.configuration_name
        orig_sig = node.inputsb if type_input else node.outputsb
        existing_node_names = [a[0] for a in orig_sig]
        existing_app_names = node.application.API.getAliases(node.application)
        name = 'newsignal'
        default_new_sgl = (
            name, {'MARTeConfig': {
                'DataSource': datasource,
                'Type': 'uint32',
                'NumberOfDimensions': '1',
                'NumberOfElements': '1',
                'Alias': name
            }}
        )
        if default:
            default_new_sgl[1]['MARTeConfig']['Default'] = '{0}'
        if epics:
            default_new_sgl[1]['MARTeConfig']['PVName'] = ''
        if samples:
            default_new_sgl[1]['MARTeConfig']['Samples'] = '1'
        try:
            orig = len(node.inputs) if type_input else len(node.outputs)
            change: int = int(wdgt.text()) - orig
        except ValueError:
            change = 0

        shadow = node.inputs if type_input else node.outputs
        endpoint = node.inputsb if type_input else node.outputsb
        if change > 0:

            position = node.input_socket_position if type_input else node.output_socket_position
            multi_edges = node.input_multi_edged if type_input else node.output_multi_edged
            count = len(shadow) - 1
            for i in range(change):
                unique_name = generateUniqueName(existing_app_names + existing_node_names,
                                                   'newsignal')
                existing_node_names.append(unique_name)
                socket = node.__class__.Socket_class(
                    node=node, index=count + i + 1, position=position,
                    socket_type=0, multi_edges=multi_edges,
                    count_on_this_node_side=len(shadow), is_input=type_input, label=unique_name
                )
                shadow += [socket]
                default_new_sgl = (unique_name, default_new_sgl[1])
                default_new_sgl[1]['MARTeConfig']['Alias'] = unique_name
                endpoint += [copy.deepcopy(default_new_sgl)]

        elif change < 0:
            for _ in range(-change):
                del endpoint[-1]
                node.scene.grScene.removeItem(shadow[-1].grSocket)
                for edge in shadow[-1].edges:
                    edge.remove()
                shadow[-1].delete()
                del shadow[-1]

        node.content.updateDim()
        node.updateSocketPositions()

def getSetKey(signal, key, default_val):
    ''' Check that a key exists and if not, create it '''
    if key not in list(signal['MARTeConfig'].keys()):
        signal['MARTeConfig'][key] = default_val
    return signal['MARTeConfig'][key]

def paraChange(value, node, parameter) -> None:
    ''' Update our parameter when there has been a change, this should be connected
    to line edit/comboedit items that are used in the GUI representation of a node. '''
    def updateParameter(text, node, parameter) -> None:
        if isinstance(node.parameters[parameter], int):
            try:
                node.parameters[parameter] = int(text)
            except ValueError:
                pass
        else:
            node.parameters[parameter] = text
    if isinstance(value, QLineEdit):
        updateParameter(value.text(), node, parameter)
    elif isinstance(value, QComboBox):
        updateParameter(value.currentText(), node, parameter)
    elif isinstance(value, QTextEdit):
        updateParameter(value.toPlainText(), node, parameter)

def addLineEdit(mainpanel_instance, node, lbl_name, para_name, row, col_start):
    ''' Adds a line edit item to a node panel '''
    wgt_label = QLabel(lbl_name)
    wgt_field = QLineEdit(mainpanel_instance)
    wgt_field.setText(str(node.parameters[para_name]))
    wgt_field.textChanged.connect(partial(paraChange, wgt_field, node, para_name))
    mainpanel_instance.configbarBox.addWidget(wgt_label, row, col_start)
    mainpanel_instance.configbarBox.addWidget(wgt_field, row, col_start+1)

def addComboEdit(mainpanel_instance, node, lbl_name, para_name, row, col_start, items):
    ''' Add a combo edit item to a node panel '''
    wgt_label = QLabel(lbl_name)
    wgt_field = QComboBox(mainpanel_instance)
    wgt_field.addItems(items)
    wgt_field.setCurrentText(str(node.parameters[para_name]))
    wgt_field.currentIndexChanged.connect(partial(paraChange, wgt_field, node, para_name))
    mainpanel_instance.configbarBox.addWidget(wgt_label, row, col_start)
    mainpanel_instance.configbarBox.addWidget(wgt_field, row, col_start+1)

def fixSignals(node):
    ''' This function fixes a signal issue by detecting whether a socket
    has a corresponding signal definition, if not, all are deleted. '''
    modified = False

    expected_count = len(node.inputsb)

    if len(node.inputs) > expected_count:
        # Delete the extra objects
        for obj in node.inputs[expected_count:]:
            obj.delete()
        # Trim the object_list
        del node.inputs[expected_count:]
        modified = True

    expected_count = len(node.outputsb)

    if len(node.outputs) > expected_count:
        # Delete the extra objects
        for obj in node.outputs[expected_count:]:
            obj.delete()
        # Trim the object_list
        del node.outputs[expected_count:]
        modified = True

    if modified:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Corrupted Signals")
        msg.setText(
            "The following node had corrupted signals defined for its sockets.\n\n"
            "As a result, the signals had to be deleted. "
            "Please review the node and readjust as needed.\n\n"
            f"The node was: {node.configuration_name}"
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

def addSignalsSection(mainpanel_instance, node, default=False,
                      epics=False, type_input=False, buses=False):
    ''' Adds a generic signal selection section to a node panel '''
    lbl_wgt = QLabel("Number of signals: ")
    no_signals_wgt = QLineEdit(mainpanel_instance)
    length = len(node.inputsb) if type_input else len(node.outputsb)
    no_signals_wgt.setText(str(length))
    no_signals_wgt.resize(230, 80)
    no_signals_wgt.editingFinished.connect(partial(textChangeOut,
                                               no_signals_wgt,
                                               node,
                                               default,
                                               epics,
                                               type_input))
    mainpanel_instance.configbarBox.addWidget(lbl_wgt, 1, 0)
    mainpanel_instance.configbarBox.addWidget(no_signals_wgt, 1, 1)
    colcount = 2
    if not type_input:
        def runWindow():
            bus = False
            if buses:
                # Now we need to check the actual configuration
                # this is specifically for the SimulinkWrapperGAM
                if node.parameters["nonvirtualbusmode"] == 'Structured':
                    # Then we need to change the signal window to be a bus configuration window
                    bus = True
            fixSignals(node)
            config_signals = SignalWdw(mainpanel_instance, node, default, epics, buses=bus)
            node.application.newwindow = config_signals
            config_signals.show()
        config_btn = QPushButton("Configure Signals")
        config_btn.clicked.connect(runWindow)
        mainpanel_instance.configbarBox.addWidget(config_btn, 1, colcount)
        colcount += 1
    spacerwgt = QWidget(mainpanel_instance)
    spacerwgt.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
    mainpanel_instance.configbarBox.addWidget(spacerwgt, 1, colcount)

def addInputSignalsSection(mainpanel_instance, node, pack=True, samples=False,
                           datasource=None, epics=False, buses=False):
    ''' Add an input signal selection item to a node panel '''
    lbl_wgt = QLabel("Number of input signals: ")
    no_signals_wgt = QLineEdit(mainpanel_instance)
    length = len(node.inputsb)
    no_signals_wgt.setText(str(length))
    no_signals_wgt.resize(230, 80)
    no_signals_wgt.editingFinished.connect(partial(textChangeOut, no_signals_wgt,
                                               node, False, epics, True, datasource, samples))
    mainpanel_instance.configbarBox.addWidget(lbl_wgt, 1, 0)
    mainpanel_instance.configbarBox.addWidget(no_signals_wgt, 1, 1)
    # Default means we're probably a constant GAM
    def runWindow():
        bus = False
        if buses:
            # Now we need to check the actual configuration
            # this is specifically for the SimulinkWrapperGAM
            if node.parameters["nonvirtualbusmode"] == 'Structured':
                # Then we need to change the signal window to be a bus configuration window
                bus = True
        fixSignals(node)
        config_signals = SignalWdw(mainpanel_instance, node, False,
                                   epics, samples,'input', buses=bus)
        node.application.newwindow = config_signals
        config_signals.show()

    config_btn = QPushButton("Configure Signals")
    config_btn.clicked.connect(runWindow)
    mainpanel_instance.configbarBox.addWidget(config_btn, 1, 2)
    if pack:
        spacerwgt = QWidget(mainpanel_instance)
        spacerwgt.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        mainpanel_instance.configbarBox.addWidget(spacerwgt, 1, 2)

def addOutputSignalsSection(mainpanel_instance, node, start = 0, pack=True, datasource=None, # pylint: disable=R0914
                            samples=False, default=False, epics=False, buses=False):
    ''' Add an output signal selection item to a node panel. '''
    # Note if samples is set, we'll start from row 2 for cleanliness
    lbl_wgt = QLabel("Number of output signals: ")
    no_signals_wgt = QLineEdit(mainpanel_instance)
    length = len(node.outputsb)
    no_signals_wgt.setText(str(length))
    no_signals_wgt.resize(230, 80)
    no_signals_wgt.editingFinished.connect(partial(textChangeOut, no_signals_wgt,
                                               node, default, epics, False, datasource, samples))
    rowstart = 1
    mainpanel_instance.configbarBox.addWidget(lbl_wgt, rowstart, start)
    mainpanel_instance.configbarBox.addWidget(no_signals_wgt, rowstart, start+1)
    def runWindow():
        bus = False
        if buses:
            # Now we need to check the actual configuration
            # this is specifically for the SimulinkWrapperGAM
            if node.parameters["nonvirtualbusmode"] == 'Structured':
                # Then we need to change the signal window to be a bus configuration window
                bus = True
        config_signals = SignalWdw(mainpanel_instance, node, default, epics, samples, buses=bus)
        node.application.newwindow = config_signals
        config_signals.show()
    config_btn = QPushButton("Configure Signals")
    config_btn.clicked.connect(runWindow)
    mainpanel_instance.configbarBox.addWidget(config_btn, rowstart, start+2)
    if pack:
        spacerwgt = QWidget(mainpanel_instance)
        spacerwgt.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        mainpanel_instance.configbarBox.addWidget(spacerwgt, rowstart, start+3)

def spacer():
    ''' Creates a generic spacer widget '''
    spacerWgt = QWidget()
    spacerWgt.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
    return spacerWgt

def createLineEdit(layout, label, func, finished=False, space=False):
    ''' Creates the actual line edit item used in node panels. '''
    wgt = QWidget()
    hlayout = QHBoxLayout()
    wgt.setLayout(hlayout)
    lbl = QLabel(label)
    edit = QLineEdit()
    if finished:
        edit.editingFinished.connect(func)
    else:
        edit.textChanged.connect(func)
    hlayout.addWidget(lbl)
    hlayout.addWidget(edit)
    if space:
        hlayout.addWidget(spacer())
    layout.addWidget(wgt)
    return edit

def createComboEdit(layout, label, func, items, space=False):
    ''' Creates the actual combobox edit item used in node panels. '''
    wgt = QWidget()
    hlayout = QHBoxLayout()
    wgt.setLayout(hlayout)
    lbl = QLabel(label)
    edit = QComboBox()
    edit.addItems(items)
    edit.currentIndexChanged.connect(func)
    hlayout.addWidget(lbl)
    hlayout.addWidget(edit)
    if space:
        hlayout.addWidget(spacer())
    layout.addWidget(wgt)
    return edit

def createGridLineEdit(layout, row, label, func, finished=False, space=False):
    ''' Creates a line edit item to fit into a grid layout '''
    lbl = QLabel(label)
    edit = QLineEdit()
    if finished:
        edit.editingFinished.connect(func)
    else:
        edit.textChanged.connect(func)
    layout.addWidget(lbl, row, 0)
    layout.addWidget(edit, row, 1)
    if space:
        layout.addWidget(spacer(), row, 2)
    return edit

def createGridComboEdit(layout, row, label, func, items, space=False):
    ''' Creates a combobox item to fit into a grid layout. '''
    lbl = QLabel(label)
    edit = QComboBox()
    edit.addItems(items)
    edit.currentIndexChanged.connect(func)
    layout.addWidget(lbl, row, 0)
    layout.addWidget(edit, row, 1)
    if space:
        layout.addWidget(spacer(), row, 2)
    return edit

def defineSaveCancelButtons(layout, save_func, cancel_func):
    """Add the generic save and cancel buttons to a given window layout and use self
    for referencing the given expected function names to connect to the button signals.
    """
    # Now save and cancel buttons
    buttons = QWidget()
    hbox = QHBoxLayout()
    button_spacer = QWidget()
    button_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
    hbox.addWidget(button_spacer)

    save_button = QPushButton("Save")
    save_button.clicked.connect(save_func)
    hbox.addWidget(save_button)

    cancel_button = QPushButton("Cancel")
    cancel_button.clicked.connect(cancel_func)
    hbox.addWidget(cancel_button)

    buttons.setLayout(hbox)
    layout.addWidget(buttons)

def setSize(window,app,x_pos=0.4,y_pos=0.3,width=0.3,height=0.2):
    """Set the Window Size
    """
    # Set Window Size
    screen = app.primaryScreen()
    size = screen.size()
    window.setGeometry(
        int(size.width() * x_pos),
        int(size.height() * y_pos),
        int(size.width() * width),
        int(size.height() * height),
    )

def recursivelySetEnabled(layout, enable):
    ''' Recursively enable widgets or disable them '''
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if isinstance(item, QLayout):
            recursivelySetEnabled(item, enable)
        elif isinstance(item.widget(), QWidget):
            item.widget().setEnabled(enable)

def generateUniqueName(existing_names, base_name):
    """Generate a unique name based on the existing names in the list.
    """
    if base_name not in existing_names:
        return base_name

    i = 1
    while True:
        new_name = f"{base_name}{i}"
        if new_name not in existing_names:
            return new_name
        i += 1

def generateUniqueGamName(existing_names):
    """Generate a unique name based on the existing names in the list.
    """
    i = 1
    while True:
        new_name = f"DDB{i}"
        if new_name not in existing_names:
            return new_name
        i += 1


def genNextStateMsgs(state_name, app_name):
    ''' Generate a set of messages based on the state name and application name '''
    params = MARTe2ConfigurationDatabase(objects = {"param1": state_name})
    prepare = MARTe2Message(f"+PrepareChangeTo{state_name}Msg", app_name,
                            "PrepareNextState", params)
    defaultmessages = [MARTe2Message("+StopCurrentStateExecutionMsg",
                                     app_name, "StopCurrentStateExecution"),
                        prepare,
                        MARTe2Message("+StartNextStateExecutionMsg",
                                      app_name, "StartNextStateExecution")]
    return defaultmessages

def showErrorDialog(message):
    ''' Show an error dialog messagebox. '''
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setText("Error")
    msg_box.setInformativeText(message)
    msg_box.setWindowTitle("Error")
    msg_box.exec_()

def textExistsInListWidget(list_widget, text):
    ''' Check whether list items exist in a list widget '''
    for index in range(list_widget.count()):
        item = list_widget.item(index)
        if item.text() == text:
            return True
    return False

def deleteChildren(layout):
    ''' Delete all the children in a layout '''
    # Remove all widgets from layout
    for i in reversed(range(layout.count())):
        widget = layout.itemAt(i).widget()
        if widget:
            widget.deleteLater()
