''' Pythonic representative class of the AsyncBridge Datasource '''

import copy
from functools import partial

from PyQt5.QtWidgets import (
    QLabel,
    QComboBox
)

from martepy.marte2.datasource import MARTe2DataSource
from martepy.marte2.qt_functions import addSignalsSection, addLineEdit, addComboEdit


class Synchronisation(MARTe2DataSource):
    ''' Pythonic representation of the AsyncBridge '''
    def __init__(self,
                    configuration_name: str = 'RealTimeThreadSynchronisation',
                    waitfornext = 1,
                    printoverwrite = 'Default',
                    timeout = -1,
                    input_signals = [],
                    output_signals = [],
                    inputs = False
                ):
        super().__init__(
                 configuration_name = configuration_name,
                 class_name = 'RealTimeThreadSynchronisation',
                 input_signals = input_signals,
            )
        if not inputs:
            self.output_signals = self.input_signals
            self.input_signals = []
        self.waitfornext = waitfornext
        self.printoverwrite = printoverwrite
        self.timeout = timeout
        self.input = inputs

    def writeDatasourceConfig(self, config_writer):
        ''' Write the datasource configuration to the cfg. '''
        config_writer.writeNode('Timeout', '"{}"'.format(self.timeout))
        config_writer.writeNode('PrintOverwrite', '"{}"'.format(self.printoverwrite))
        config_writer.writeNode('WaitForNext', '"{}"'.format(self.waitfornext))

    def serialize(self):
        ''' Serialize the datasource object '''
        res: dict = super().serialize()
        res['parameters']['timeout'] = self.timeout
        res['parameters']['printoverwrite'] = self.printoverwrite
        res['parameters']['waitfornext'] = self.waitfornext
        res['parameters']['input'] = self.input

        # Override name
        res['label'] = "Synchronisation"
        res['block_type'] = 'Synchronisation'
        res['class_name'] = 'Synchronisation'
        res['title'] = f"{self.configuration_name} (Synchronisation)"
        return res

    # We need to override this to make an exception for the fact that we have
    # self.input for GUI purposes but actually this is the same datasource
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            myself = copy.deepcopy(self.serialize())
            theother = copy.deepcopy(other.serialize())
            if not myself['configuration_name'] == theother['configuration_name']:
                return False
            del myself['parameters']['input']
            del theother['parameters']['input']
            if not myself['parameters'] == theother['parameters']:
                return False
            return True
        return False

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True) -> bool:
        ''' Deserialize the datasource object. '''
        res = super().deserialize(data, hashmap, restore_id)
        self.timeout = data['parameters']["timeout"]
        self.printoverwrite = data['parameters']["printoverwrite"]
        self.input = data['parameters']['input']
        self.waitfornext = data['parameters']["waitfornext"]
        return res

    @staticmethod
    def loadParameters(mainpanel_instance, node): # pylint: disable=R0915
        """This function is intended to be for the GUI where it can call the static
        instance of the class directly to generate
        the appropriate parameter modifier for the node in XMARTe2.
        """
        # This needs to be specialised, if the user selects to have this reading or writing
        # Then the sockets need to be switched

        def removeWidgetsExceptRow0(layout):
            for i in reversed(range(layout.count())):
                item = layout.itemAt(i)
                row_span = layout.getItemPosition(i)[3]
                column_span = layout.getItemPosition(i)[2]
                if row_span == 1 and column_span == 1:
                    layout.removeItem(item)
                    widget = item.widget()
                    if widget is not None:
                        widget.setParent(None)
                    del item

        def inputChanged(wgt_field, mainpanel_instance, node, _):
            # Switch socket positions
            prev = node.scene.large_import
            node.scene.large_import = True
            merged_list = node.inputsb + node.outputsb
            type_input = False
            if wgt_field.currentText() == 'Read':
                node.inputsb = merged_list
                node.outputsb = []
                type_input = True
                for socket in node.outputs:
                    for edge in socket.edges:
                        edge.remove()
                sockets = copy.copy(node.outputs)
                for socket in sockets:
                    socket.is_input = True
                    socket.is_output = False
                    socket.position = 2
                    socket.node = node
                    socket.grSocket.setParentItem(None)
                    socket.node.scene.grScene.removeItem(socket.grSocket)
                    del socket.grSocket
                    socket.grSocket = socket.__class__.Socket_GR_Class(socket)
                    socket.setSocketPosition()
                node.inputs = sockets
                node.outputs = []
            else:
                # Is write
                node.inputsb = []
                node.outputsb = merged_list
                for socket in node.inputs:
                    for edge in socket.edges:
                        edge.remove()
                sockets = copy.copy(node.inputs)
                for socket in sockets:
                    socket.is_input = False
                    socket.is_output = True
                    socket.position = 5
                    socket.node = node
                    socket.grSocket.setParentItem(None)
                    socket.node.scene.grScene.removeItem(socket.grSocket)
                    del socket.grSocket
                    socket.grSocket = socket.__class__.Socket_GR_Class(socket)
                    socket.setSocketPosition()
                node.outputs = sockets
                node.inputs = []

            node.parameters['input'] = type_input
            node.updateSocketPositions()
            node.scene.large_import = prev
            # Redraw
            draw(mainpanel_instance, node, type_input)

        type_input = node.parameters['input']

        def draw(mainpanel_instance, node, type_input):
            removeWidgetsExceptRow0(mainpanel_instance.configbarBox)
            addSignalsSection(mainpanel_instance, node, type_input=not(node.parameters['input']))

            wgt_label = QLabel("Read/Write: ")
            wgt_field = QComboBox(mainpanel_instance)
            wgt_field.addItems(['Read', 'Write'])
            index = 0 if type_input else 1
            wgt_field.setCurrentIndex(index)
            wgt_field.currentIndexChanged.connect(partial(inputChanged, wgt_field,
                                                          mainpanel_instance, node))
            mainpanel_instance.configbarBox.addWidget(wgt_label, 2, 0)
            mainpanel_instance.configbarBox.addWidget(wgt_field, 2, 1)

            addLineEdit(mainpanel_instance, node,"Timeout: ", 'timeout', 3, 0)

            addComboEdit(mainpanel_instance, node,"Print Overwrite?: ", 'printoverwrite', 3, 2, ['yes', 'no'])

            addComboEdit(mainpanel_instance, node,"Wait For Next?: ", 'waitfornext', 4, 0, ['yes', 'no'])

        draw(mainpanel_instance, node, type_input)


def initialize(factory, plugin_datastore) -> None:
    ''' Initialize our object to the factory '''
    factory.registerBlock("RealTimeThreadSynchronisation", Synchronisation, plugin_datastore)
    factory.registerBlock("Synchronisation", Synchronisation, plugin_datastore)
