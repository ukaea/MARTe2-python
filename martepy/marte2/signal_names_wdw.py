''' The window in the XMARTe2 GUI that loads to configure signals, exists here as is 
launched from the GAM itself. '''

from functools import partial
import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDesktopWidget,
    QWidget,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMainWindow
)
from qtpy.QtGui import QIcon

from martepy.marte2.datasource import MARTe2DataSource
from martepy.functions.extra_functions import getname


class SignalWdw(QMainWindow):
    ''' The configurable signal window where the user can configure signals in XMARTe2. '''
    def __init__(self, parent=None, node=None, hasdefault=False, epics=False,
                 samples=False, io='output', buses=False):
        if node is None:
            raise ValueError("Node cannot be null")
        super().__init__(parent)
        self.node = node
        self.to_delete = []
        self.epics = epics
        self.bus = buses
        self.samples = samples
        self.io = io
        self.app = node.application.app
        self.setWindowTitle("Signal Configuration")
        # Setup our geometry
        self.setSize()
        self.setCentralWidget(QWidget(self))
        self.vlayout = QVBoxLayout()
        self.default = hasdefault
        self.centralWidget().setLayout(self.vlayout)
        # Section which defines input signals and their options selected
        self.signal_tbl = QTableWidget()
        self.vlayout.addWidget(self.signal_tbl, stretch=1)
        signals = node.outputsb if self.io == 'output' else node.inputsb
        self.signal_tbl.setRowCount(len(signals))
        headers = ["Signal Name", "Datasource", "Type",
                   "NumberOfDimensions", "NumberOfElements", 'Alias']

        self.is_datasource = isinstance(self.node.application.API.toGAM(self.node),
                                                       MARTe2DataSource)
        self.signal_tbl.setColumnCount(7 + self.handleAdditionalHeaders(headers))
        headers += ['Delete']
        self.signal_tbl.setHorizontalHeaderLabels(headers)

        # Connect the itemChanged signal to the handleItemChanged function
        self.signal_tbl.itemChanged.connect(self.handleItemChanged)
        for row_num, signal in enumerate(signals):
            self.createSignalRow(signal, self.is_datasource, row_num)

        self.handleSamples()

        self.handleIo()

        self.defineSaveCancelButtons(self.vlayout)
        self.resize(self.signal_tbl.horizontalHeader().length() + 80, self.height())
        self.show()
        # Center the window on the screen
        self.center()

    def handleSamples(self):
        ''' Handles whether our signal supports the samples attribute '''
        colcount = self.signal_tbl.columnCount()
        if self.samples and self.io == 'input':
            # For a MuxGAM we only want to expose the ability to set the number of samples
            for row in range(self.signal_tbl.rowCount()):
                for i in range(0,colcount):
                    item = self.signal_tbl.item(row, i)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item = self.signal_tbl.item(row, colcount-1)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)

    def handleIo(self):
        ''' Handle whether our signal is an input and therefore the user cannot 
        change the alias '''
        if self.io == 'input':
            # Make column 5 read-only
            for row in range(self.signal_tbl.rowCount()):
                item = self.signal_tbl.item(row, 5)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if self.is_datasource:
                    item = self.signal_tbl.item(row, 1)
                    if item:
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)


    def handleAdditionalHeaders(self, headers):
        ''' Handle whether we need additional headers '''
        header_cnt = 0
        if self.bus:
            # Remove the last item in-place instead of slicing
            headers.append('Bus')
            header_cnt += 1
        if self.default:
            headers.append('Default')
            header_cnt += 1
        if self.epics:
            headers.append('PVName')
            header_cnt += 1
        if self.samples:
            headers.append('Samples')
            header_cnt += 1
        return header_cnt

    def createSignalRow(self, signal, is_datasource, row_num): # pylint: disable=R0914
        ''' Given a signal, add it to our table '''
        def getSetKey(key, default_val):
            ''' Check that a key exists and if not, create it '''
            if key not in list(signal[1]['MARTeConfig'].keys()):
                signal[1]['MARTeConfig'][key] = default_val
            return signal[1]['MARTeConfig'][key]

        self.signal_tbl.setItem(row_num, 0, QTableWidgetItem(signal[0]))

        if is_datasource:
            signal[1]['MARTeConfig']['DataSource'] = getname(self.node)
        datasource = getSetKey('DataSource', None)
        sgl_type = getSetKey('Type', None)
        self.signal_tbl.setItem(row_num, 1, QTableWidgetItem(datasource))
        self.signal_tbl.setItem(row_num, 2, QTableWidgetItem(sgl_type))
        # - note in constantGAM's this could produce an issue so be wary
        # about changing the node itself unless this is itself changed!
        dimensions = getSetKey('NumberOfDimensions', '1')
        elements = getSetKey('NumberOfElements', '1')
        self.signal_tbl.setItem(row_num, 3, QTableWidgetItem(dimensions))
        self.signal_tbl.setItem(row_num, 4, QTableWidgetItem(elements))
        # Set the alias
        alias = getSetKey('Alias', signal[0])
        self.signal_tbl.setItem(row_num, 5, QTableWidgetItem(alias))
        colcount = 6
        if self.bus:
            bus = getSetKey('Bus', signal[0])
            self.signal_tbl.setItem(row_num, colcount, QTableWidgetItem(bus))
            colcount += 1
        if self.default:
            default = getSetKey('Default', '{1}')
            self.signal_tbl.setItem(row_num, colcount, QTableWidgetItem(default))
            colcount += 1
        if self.epics:
            pv_name = getSetKey('PVName', signal[0])
            self.signal_tbl.setItem(row_num, colcount, QTableWidgetItem(pv_name))
            colcount += 1
        if self.samples:
            samples = getSetKey('Samples', signal[0])
            self.signal_tbl.setItem(row_num, colcount, QTableWidgetItem(samples))
            colcount += 1

        del_button = QPushButton()
        del_button.setIcon(QIcon(os.path.join('xmarte','qt5','icons','delete.png')))
        del_button.clicked.connect(partial(self.deleteRow, row_num))
        self.signal_tbl.setCellWidget(row_num, colcount, del_button)

    def center(self):
        ''' Centres our window in the screen '''
        # Get the geometry of the main window
        qr = self.frameGeometry()
        # Get the center point of the screen
        cp = QDesktopWidget().availableGeometry().center()
        # Move the center point of the main window to the center point of the screen
        qr.moveCenter(cp)
        # Set the top-left corner of the main window to the top-left corner of the qr geometry
        self.move(qr.topLeft())

    def handleItemChanged(self, item):
        ''' If an item has changed and it is the alias, and an output,
        then change the name as well to match '''
        if item.column() == 0 and self.io == 'output':  # Check if the modified item is in column 1
            row_number = item.row()  # Get the row number of the modified item
            column_1_text = item.text()  # Get the text of the modified item in column 1

            # Modify the item in column 7 of the same row to match the text contents of column 1
            self.signal_tbl.setItem(row_number, 5, QTableWidgetItem(column_1_text))

    def deleteRow(self, row):
        ''' Set the current signal to be deleted unless the window is not saved when closed '''
        # update row count to account for previously deleted rows
        tblrow = self.signal_tbl.rowCount() -1 if row >= self.signal_tbl.rowCount() else row
        self.signal_tbl.removeRow(tblrow)
        socket_list = self.node.outputs if self.io == 'output' else self.node.inputs
        socket_to_delete = socket_list[row]
        self.to_delete += [(row,socket_to_delete)]


    def defineSaveCancelButtons(self, layout):
        """Add the generic save and cancel buttons to a given window layout and use self
        for referencing the given expected function names to connect to the button signals.
        """
        spacer = QWidget(self)
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(spacer)

        # Now save and cancel buttons
        buttons = QWidget(self)
        hbox = QHBoxLayout()
        button_spacer = QWidget(self)
        button_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        hbox.addWidget(button_spacer)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save)
        hbox.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel)
        hbox.addWidget(self.cancel_button)

        buttons.setLayout(hbox)
        layout.addWidget(buttons)

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

    def save(self):  # pylint: disable=R0914, R0915, R0912
        ''' Save our changes - quite complex as we handle our buffered deletions and delete
        these from the node '''
        if self.to_delete:
            sockets_to_remove = set()
            positions_to_remove = set()

            for position, socket in self.to_delete:
                sockets_to_remove.add(socket)
                socket.delete()
                positions_to_remove.add(position)

            if self.io == 'output':
                self.node.outputs = [
                    sock for sock in self.node.outputs if sock not in sockets_to_remove
                ]
            else:
                self.node.inputs = [
                    sock for sock in self.node.inputs if sock not in sockets_to_remove
                ]

            signal_list = self.node.outputsb if self.io == 'output' else self.node.inputsb
            for pos in sorted(positions_to_remove, reverse=True):
                if 0 <= pos < len(signal_list):
                    signal_list.pop(pos)
        signals = self.node.outputsb if self.io == 'output' else self.node.inputsb
        for row in range(len(signals)): # pylint:disable=C0200
            new_tuple = None
            name = self.signal_tbl.item(row, 0).text()
            config = {'MARTeConfig':{'DataSource': self.signal_tbl.item(row, 1).text()}}
            config['MARTeConfig']['Type'] = self.signal_tbl.item(row, 2).text()
            config['MARTeConfig']['NumberOfDimensions'] = self.signal_tbl.item(row, 3).text()
            config['MARTeConfig']['NumberOfElements'] = self.signal_tbl.item(row, 4).text()
            config['MARTeConfig']['Alias'] = self.signal_tbl.item(row, 5).text()
            colcount = 6
            if self.bus:
                config['MARTeConfig']['Bus'] = self.signal_tbl.item(row, colcount).text()
                colcount += 1
            if self.default:
                config['MARTeConfig']['Default'] = self.signal_tbl.item(row, colcount).text()
                colcount += 1
            if self.epics:
                config['MARTeConfig']['PVName'] = self.signal_tbl.item(row, colcount).text()
                colcount += 1
            if self.samples:
                config['MARTeConfig']['Samples'] = self.signal_tbl.item(row, colcount).text()
            sockets = self.node.outputs if self.io == 'output' else self.node.inputs
            for edge in sockets[row].edges:
                try:
                    socket_idx = edge.end_socket.node.inputs.index(edge.end_socket)
                    inputsb = edge.end_socket.node.inputsb[socket_idx]
                    inputsb[1]['MARTeConfig']['Alias'] = self.signal_tbl.item(row, 0).text()
                    inputsb[1]['MARTeConfig']['DataSource'] = self.signal_tbl.item(row, 1).text()
                    inputsb[1]['MARTeConfig']['Type'] = self.signal_tbl.item(row, 2).text()
                    edge.end_socket.node.updateSocketPositions()
                except AttributeError:
                    pass
            new_tuple = (name,config)
            signals[row] = new_tuple
            sockets[row].label = name
        self.node.updateSocketPositions()
        try:
            self.node.grNode.updateDim()
        except AttributeError:
            pass  # continue without resizing
        application = self.node.application
        self.node.resetParameterbar()
        self.node.onDoubleClicked(None)
        app = application.API.buildApplication()
        application.API.errorCheck(app)
        self.close()
        application.newwindow = None

    def cancel(self):
        ''' Close the window without doing anything '''
        application = self.node.application
        self.close()
        application.newwindow = None
