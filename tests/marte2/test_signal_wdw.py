import pytest
import pdb

from martepy.marte2.signal_names_wdw import *
from martepy.marte2.gams.iogam import IOGAM
from martepy.functions.gam_functions import getAlias

from PyQt5.QtWidgets import QApplication, QPushButton

from ..utilities import qapp, ensure_gc, create_node_mock

def test_getalias():
    assert 'Counter' == getAlias(('Counter',{'MARTeConfig':{'DataSource':'Timer','Type':'uint32'}}))
    assert 'Timer' == getAlias(('Counter',{'MARTeConfig':{'DataSource':'Timer','Type':'uint32','Alias':'Timer'}}))

def test_signal_wdw_null(qapp):
    with pytest.raises(Exception) as excinfo:
        sgl_wdw = SignalWdw(None, None, False, False, False)
    assert str(excinfo.value) == 'Node cannot be null'

def test_signal_wdw(create_node_mock):
    sgl_wdw = SignalWdw(None, create_node_mock, False, False, False)
    assert sgl_wdw.signal_tbl.item(0, 0).text() == 'Counter'
    assert sgl_wdw.signal_tbl.item(0, 1).text() == 'Timer'
    assert sgl_wdw.signal_tbl.item(0, 2).text() == 'uint32'
    assert sgl_wdw.signal_tbl.item(0, 3).text() == '1'
    assert sgl_wdw.signal_tbl.item(0, 4).text() == '1'
    assert sgl_wdw.signal_tbl.item(0, 5).text() == 'Timer'

    assert sgl_wdw.save_button.__class__ == QPushButton
    assert sgl_wdw.save_button.text() == 'Save'
    assert sgl_wdw.cancel_button.__class__ == QPushButton
    assert sgl_wdw.cancel_button.text() == 'Cancel'
    sgl_wdw.close()

def test_signal_wdw_save(create_node_mock):
    sgl_wdw = SignalWdw(None, create_node_mock, False, False, False)
    sgl_wdw.signal_tbl.item(0, 0).setText('NewName')
    sgl_wdw.signal_tbl.item(0, 3).setText('4')
    sgl_wdw.signal_tbl.item(0, 2).setText('float32')
    sgl_wdw.save_button.clicked.emit()

    assert create_node_mock.outputsb[0][0] == 'NewName'
    assert create_node_mock.outputsb[0][1]['MARTeConfig']['DataSource'] == 'Timer'
    assert create_node_mock.outputsb[0][1]['MARTeConfig']['NumberOfElements'] == '1'
    assert create_node_mock.outputsb[0][1]['MARTeConfig']['NumberOfDimensions'] == '4'
    assert create_node_mock.outputsb[0][1]['MARTeConfig']['Type'] == 'float32'
    assert create_node_mock.outputsb[0][1]['MARTeConfig']['Alias'] == 'NewName'

    #
    # sgl_wdw.close()

def test_signal_wdw_cancel(create_node_mock):
    sgl_wdw = SignalWdw(None, create_node_mock, False, False, False)
    sgl_wdw.signal_tbl.item(0, 0).setText('NewName')
    sgl_wdw.signal_tbl.item(0, 3).setText('4')
    sgl_wdw.signal_tbl.item(0, 2).setText('float32')
    sgl_wdw.cancel_button.clicked.emit()

    assert create_node_mock.outputsb[0][0] == 'Counter'
    assert create_node_mock.outputsb[0][1]['MARTeConfig']['DataSource'] == 'Timer'
    assert create_node_mock.outputsb[0][1]['MARTeConfig']['NumberOfElements'] == '1'
    assert create_node_mock.outputsb[0][1]['MARTeConfig']['NumberOfDimensions'] == '1'
    assert create_node_mock.outputsb[0][1]['MARTeConfig']['Type'] == 'uint32'
    assert create_node_mock.outputsb[0][1]['MARTeConfig']['Alias'] == 'Timer'

