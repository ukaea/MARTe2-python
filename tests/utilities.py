import pytest

import copy
import sys
import os
import pdb
import gc

top_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, top_dir)

from nodeeditor.node_node import Node

import martepy.marte2.configwriting as marteconfig
from martepy.marte2.objects.message import MARTe2Message
from martepy.marte2.objects.real_time_thread import MARTe2RealTimeThread
from martepy.marte2.objects.statemachine.event import MARTe2StateMachineEvent
from martepy.marte2.gams.constant_gam import ConstantGAM
from martepy.marte2.gams.iogam import IOGAM
from martepy.marte2.objects.referencecontainer import MARTe2ReferenceContainer
from martepy.marte2.config_object import MARTe2ConfigObject

from PyQt5.QtWidgets import QApplication, QGridLayout, QVBoxLayout, QWidget, QMainWindow

top_lvl = os.path.dirname(os.path.dirname(__file__))

def writeSignals_section(input_signals, output_signals):
    test_writer = marteconfig.StringConfigWriter()
    test_writer.tab += 1
    if input_signals:
        test_writer.startSection('InputSignals')
        MARTe2ConfigObject.writeSignals(input_signals, test_writer)
        test_writer.endSection('InputSignals')
    if output_signals:
        test_writer.startSection('OutputSignals')
        MARTe2ConfigObject.writeSignals(output_signals, test_writer)
        test_writer.endSection('OutputSignals')
    return test_writer

def write_datasource_signals_section(signals):
    test_writer = marteconfig.StringConfigWriter()
    test_writer.tab += 1
    if signals:
        test_writer.startSection('Signals')
        out_signal = copy.deepcopy(signals)
        for a in out_signal:
            if 'DataSource' in list(a[1]['MARTeConfig'].keys()):
                del a[1]['MARTeConfig']['DataSource']
            if 'Alias' in list(a[1]['MARTeConfig'].keys()):
                del a[1]['MARTeConfig']['Alias']
        MARTe2ConfigObject.writeSignals(out_signal, test_writer)
        test_writer.endSection('Signals')
    return test_writer

class TFactory():
    def create(self, name):
        if name == 'Message':
            return MARTe2Message
        elif name == 'RealTimeThread':
            return MARTe2RealTimeThread
        elif name == 'ReferenceContainer':
            return MARTe2ReferenceContainer
        elif name == 'ConstantGAM':
            return ConstantGAM
        elif name == 'IOGAM':
            return IOGAM
        elif name == 'StateMachineEvent':
            return MARTe2StateMachineEvent
        
@pytest.fixture
def qapp():
    """Create a QApplication instance."""
    global app
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

@pytest.fixture
def main_window(qapp):
    """Create a QMainWindow instance."""
    window = QMainWindow()
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    window.setGeometry(100, 100, 200, 200)
    return window

@pytest.fixture
def load_parameters(qapp, main_window):
    """Test the load_parameters function."""
    # Create a layout
    layout = QVBoxLayout()
    main_window.centralWidget().setLayout(layout)
    layout_wgt = QWidget()
    layout_wgt.setLayout(layout)
    layout_wgt.configbarBox = QGridLayout()
    layout_wgt.parameterbar = QWidget()
    layout_wgt.parent = emptyObject()
    layout_wgt.parent.API = emptyObject()
    def override_param(param):
        return fakeDef()
    layout_wgt.parent.API.getServiceByName = override_param
    return layout_wgt

class emptyObject():
    pass

class fakeDef():
    def __init__(self):
        self.configuration = {'misc':{'gamsources': ['DDB0']}}

class grSocket():
    def __init__(self, socket=None):
        self.socket = socket
        
    def setParentItem(self, socket=None):
        self.socket = socket
        
class socketClass():
    Socket_GR_Class = grSocket
    def __init__(self, is_input=True, parent=None):
        self.edges = []
        self.is_input = is_input
        self.is_output = not(is_input)
        self.position = 2
        self.node = parent
        self.grSocket = self.__class__.Socket_GR_Class(self)
        
    def setSocketPosition(self):
        pass

class GAMNode(Node):
    graphics_node_class = None
    def __init__(self, gam):

        self.configuration_name = gam.configuration_name
        self.parameters = gam.serialize()['parameters']
        self.inputsb = gam.serialize()['inputsb']
        self.outputsb = gam.serialize()['outputsb']
        self.scene = emptyObject()
        self.scene.grScene = emptyObject()
        def override_none(a):
            return None
        self.scene.grScene.removeItem = override_none
        self.scene.large_import = False
        self.inputs = [socketClass(True, self) for inp in self.inputsb]
        self.outputs = [socketClass(False, self) for outp in self.outputsb]
        
    def updateSocketPositions(self):
        pass

@pytest.fixture(autouse=True)
def ensure_gc():
    gc.collect()

class mock_obj():
    pass

@pytest.fixture
def create_node_mock(qapp):
    node = mock_obj()
    node.application = mock_obj()
    node.application.app = qapp
    node.outputsb = [('Counter',{'MARTeConfig':{'DataSource':'Timer','Type':'uint32','Alias':'Timer'}})]
    node.outputs = [mock_obj()]
    node.outputs[0].label = 'Counter'
    node.outputs[0].edges = []
    def override_none():
        return ''
    def override_param(param):
        return ''
    def override_iogam(param):
        return IOGAM()
    node.updateSocketPositions = override_none
    node.resetParameterbar = override_none
    node.onDoubleClicked = override_param
    node.application.API = mock_obj()
    node.application.API.toGAM = override_iogam
    node.application.API.buildApplication = override_none
    node.application.API.errorCheck = override_param
    return node