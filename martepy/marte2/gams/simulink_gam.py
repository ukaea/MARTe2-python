''' Pythonic representation of the Simulink GAM'''
from collections import defaultdict
from functools import partial
import copy

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QComboBox, QAbstractItemView
)
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QGuiApplication

from martepy.marte2.gam import MARTe2GAM
from martepy.marte2.qt_functions import (addInputSignalsSection, addOutputSignalsSection,
                                         addComboEdit, addLineEdit, getSetKey)
from martepy.functions.extra_functions import normalizeSignal

class SimulinkGAM(MARTe2GAM):
    ''' Pythonic representation of the Simulink GAM'''
    def __init__(self,
                    configuration_name: str = 'SimulinkWrapperGAM',
                    input_signals: list = [],
                    output_signals: list = [],
                    library: str = '',
                    symbolprefix: str = '',
                    Verbosity: int = 0,
                    skipinvalidtunableparams: int = 0,
                    EnforceModelSignalCoverage: int = 0,
                    TunableParamExternalSource: str = '',
                    NonVirtualBusMode: str = 'Structured',
                ):
        self.library = library
        self.symbolprefix = symbolprefix
        self.verbosity = Verbosity
        self.skipinvalidtunableparams = skipinvalidtunableparams
        self.enforcemodelsignalcoverage = EnforceModelSignalCoverage
        self.tunableparamexternalsource = TunableParamExternalSource
        self.nonvirtualbusmode = NonVirtualBusMode
        self.parameters = []
        super().__init__(
                configuration_name = configuration_name,
                class_name = 'SimulinkWrapperGAM',
                input_signals = input_signals,
                output_signals = output_signals,
            )

    def writeGamConfig(self, config_writer):
        ''' Write the GAM configuration - i.e. the expression '''
        config_writer.writeNode('Library', f'"{self.library}"')
        config_writer.writeNode('SymbolPrefix', f'"{self.symbolprefix}"')
        config_writer.writeNode('Verbosity', f'"{self.verbosity}"')
        config_writer.writeNode('SkipInvalidTunableParams', f'"{self.skipinvalidtunableparams}"')
        config_writer.writeNode('EnforceModelSignalCoverage',
                                f'"{self.enforcemodelsignalcoverage}"')
        if self.parameters:
            config_writer.writeNode('TunableParamExternalSource',
                                    f'"{self.tunableparamexternalsource}"')
        config_writer.writeNode('NonVirtualBusMode', f'"{self.nonvirtualbusmode}"')

    # Groups our signals by bus for outputting
    def groupByBus(self, items):
        ''' Group signals together who have the same bus '''
        grouped = defaultdict(list)

        for name, info in items:
            bus = getSetKey(info, 'Bus', '')
            grouped[bus].append((name, info))

        result = []
        for bus in sorted(grouped.keys(), key=str):
            result.extend(grouped[bus])

        return result

    def writeBuses(self, config_writer, ordered_by_bus):
        ''' If using bus, write as a bus into the config '''
        if not ordered_by_bus:
            return  # nothing to process

        current_bus = None

        for _, (name, info) in enumerate(ordered_by_bus):
            bus = getSetKey(info, 'Bus', '')

            if bus != current_bus:
                if current_bus is not None:
                    config_writer.endSection(current_bus)
                config_writer.startSection(bus)
                current_bus = bus

            config_writer.startSection(name)
            signal_details = normalizeSignal(copy.deepcopy(info))

            for key, value in signal_details['MARTeConfig'].items():
                if not key == 'Bus':
                    config_writer.writeNode(key, value)
            config_writer.endSection(name)

        # After loop, end the last section
        if current_bus is not None:
            config_writer.endSection(current_bus)
    # May want to override this function to allow bus definitions and parameters

    def write(self, config_writer):
        ''' Write the total GAM configuration '''
        config_writer.startClass('+' + self.configuration_name.lstrip('+'), self.class_name)
        self.writeGamConfig(config_writer)
        if self.input_signals:
            config_writer.startSection('InputSignals')
            if self.nonvirtualbusmode == 'Structured':
                ordered_by_bus = self.groupByBus(self.input_signals)
                self.writeBuses(config_writer, ordered_by_bus)
            else:
                self.writeSignals(self.input_signals, config_writer)
            config_writer.endSection('InputSignals')
        if self.output_signals:
            config_writer.startSection('OutputSignals')
            if self.nonvirtualbusmode == 'Structured':
                ordered_by_bus = self.groupByBus(self.output_signals)
                self.writeBuses(config_writer, ordered_by_bus)
            else:
                self.writeSignals(self.output_signals, config_writer)
            config_writer.endSection('OutputSignals')

        # Print parameters section as Ref container
        if self.parameters:
            config_writer.startSection('Parameters')
            for param in self.parameters:
                # param.get('parameter_name', ''), param.get('type', ''), param.get('presets', '')
                config_writer.writeNode(
                    f"{param['parameter_name']}",
                    f"({param['type']}) {param['presets']}"
                )
            config_writer.endSection('Parameters')

        config_writer.endSection('+' + self.configuration_name.lstrip('+'))

    def serialize(self):
        ''' Serialize the object '''
        res = super().serialize()
        res['parameters']['library'] = self.library
        res['parameters']['symbolprefix'] = self.symbolprefix
        res['parameters']['verbosity'] = self.verbosity
        res['parameters']['skipinvalidtunableparams'] = self.skipinvalidtunableparams
        res['parameters']['enforcemodelsignalcoverage'] = self.enforcemodelsignalcoverage
        res['parameters']['tunableparamexternalsource'] = self.tunableparamexternalsource
        res['parameters']['nonvirtualbusmode'] = self.nonvirtualbusmode
        res['parameters']['Class name'] = 'SimulinkWrapperGAM'
        res['parameters']['parameters'] = self.parameters
        res['label'] = "SimulinkWrapperGAM"
        res['block_type'] = 'SimulinkWrapperGAM'
        res['class_name'] = 'SimulinkWrapperGAM'
        res['title'] = f"{self.configuration_name} (SimulinkWrapperGAM)"
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True) -> bool:
        ''' Deserialize the given object to our class instance '''
        res = super().deserialize(data, hashmap, restore_id)
        self.library = data['parameters']["library"]
        self.symbolprefix = data['parameters']["symbolprefix"]
        self.verbosity = data['parameters']["verbosity"]
        self.skipinvalidtunableparams = data['parameters']["skipinvalidtunableparams"]
        self.enforcemodelsignalcoverage = data['parameters']["enforcemodelsignalcoverage"]
        self.tunableparamexternalsource = data['parameters']["tunableparamexternalsource"]
        self.nonvirtualbusmode = data['parameters']["nonvirtualbusmode"]
        self.parameters = data['parameters']['parameters']
        return res

    @staticmethod
    def openDefineParametersDialog(node):
        ''' Called from xMARTe to define the parameters via a dialog '''
        dialog = DefineParametersDialog(node)
        dialog.exec_()

    @staticmethod
    def loadParameters(mainpanel_instance, node):
        """This function is intended to be for the GUI where it can
        call the static instance of the class directly to generate
        the appropriate parameter modifier for the node in XMARTe2.
        """
        app_def = mainpanel_instance.parent.API.getServiceByName('ApplicationDefinition')
        datasource = app_def.configuration['misc']['gamsources'][0]
        addInputSignalsSection(mainpanel_instance, node, False, buses=True)

        addOutputSignalsSection(mainpanel_instance, node, 3, False,
                                datasource=datasource, buses=True)


        # Define Parameters

        addLineEdit(mainpanel_instance, node, "Library: ", 'library', 3, 0)
        addLineEdit(mainpanel_instance, node, "SymbolPrefix: ", 'symbolprefix', 3, 2)

        addComboEdit(mainpanel_instance, node, "Verbosity:",
                     "verbosity", 4, 0, ['2', '1', '0'])
        addComboEdit(mainpanel_instance, node, "skipinvalidtunableparamsTunableParams:",
                     "skipinvalidtunableparams", 4, 2, ['1', '0'])
        addComboEdit(mainpanel_instance, node, "EnforceModelSignalCoverage:",
                     "enforcemodelsignalcoverage", 5, 0, ['1', '0'])

        addLineEdit(mainpanel_instance, node, "TunableParamExternalSource: ",
                    'tunableparamexternalsource', 5, 2)

        addComboEdit(mainpanel_instance, node, "NonVirtualnonvirtualbusmode:",
                     "nonvirtualbusmode", 6, 0, ['ByteArray', 'Structured'])

        btn_define_params = QPushButton("Define Parameters")
        btn_define_params.clicked.connect(partial(SimulinkGAM.openDefineParametersDialog,
                                                  node))
        mainpanel_instance.configbarBox.addWidget(btn_define_params, 6, 2)

def initialize(factory, plugin_datastore) -> None:
    ''' Initialize the object with the factory '''
    factory.registerBlock("SimulinkGAM", SimulinkGAM, plugin_datastore)
    factory.registerBlock("SimulinkWrapperGAM", SimulinkGAM, plugin_datastore)

class DefineParametersDialog(QDialog):
    ''' Dialog box for setting model parameters '''
    TYPE_OPTIONS = ['uint8', 'int8', 'uint16', 'int16', 'uint32', 'int32', 'float32', 'float64']

    def __init__(self, node):
        ''' Dialog box for setting model parameters '''
        super().__init__()
        self.node = node
        self.setWindowTitle("Define Parameters")
        self.initUI()
        self.loadExistingParameters()

    def initUI(self):
        ''' Setup the UI '''
        self.setMinimumSize(QSize(int(self.screenWidth() * 0.3),
                                  int(self.screenHeight() * 0.5)))
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Top bar with Add and Delete
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        self.btn_add = QPushButton("Add")
        self.btn_delete = QPushButton("Delete")
        top_bar.addWidget(self.btn_add)
        top_bar.addWidget(self.btn_delete)
        layout.addLayout(top_bar)

        # Table
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(['Parameter Name', 'Type', 'Presets'])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        # Bottom bar with Cancel and Apply
        bottom_bar = QHBoxLayout()
        bottom_bar.addStretch()
        self.btn_cancel = QPushButton("Cancel")
        self.btn_apply = QPushButton("Apply")
        bottom_bar.addWidget(self.btn_cancel)
        bottom_bar.addWidget(self.btn_apply)
        layout.addLayout(bottom_bar)

        # Connections
        self.btn_add.clicked.connect(self.addRow)
        self.btn_delete.clicked.connect(self.deleteSelectedRow)
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_apply.clicked.connect(self.applyChanges)

    def screenWidth(self):
        ''' Get screen width '''
        return QGuiApplication.primaryScreen().geometry().width()

    def screenHeight(self):
        ''' Get screen height '''
        return QGuiApplication.primaryScreen().geometry().height()

    def loadExistingParameters(self):
        ''' Load the previous set of parameters and display '''
        self.table.setRowCount(0)
        param_list = self.node.parameters.get('parameters', [])
        for param in param_list:
            self.addRow(param.get('parameter_name', ''),
                         param.get('type', ''),
                         param.get('presets', ''))

    def addRow(self, name='', type_str='uint8', presets=''):
        ''' Add another parameter for row '''
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(name))

        combo = QComboBox()
        combo.addItems(self.TYPE_OPTIONS)
        if type_str in self.TYPE_OPTIONS:
            combo.setCurrentText(type_str)
        self.table.setCellWidget(row, 1, combo)

        self.table.setItem(row, 2, QTableWidgetItem(presets))

    def deleteSelectedRow(self):
        ''' Delete the selected row '''
        selected = self.table.selectionModel().selectedRows()
        for index in sorted(selected, reverse=True):
            self.table.removeRow(index.row())

    def applyChanges(self):
        ''' Save parameters to the GAM config '''
        self.node.parameters['parameters'] = []
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 0)
            presets_item = self.table.item(row, 2)
            type_widget = self.table.cellWidget(row, 1)

            name = name_item.text() if name_item else ''
            presets = presets_item.text() if presets_item else ''
            type_str = type_widget.currentText() if type_widget else 'uint8'

            param_dict = {
                'parameter_name': name,
                'type': type_str,
                'presets': presets
            }
            self.node.parameters['parameters'].append(param_dict)

        self.accept()
