import pytest, pdb

from pytestqt import qtbot

from martepy.marte2.qt_classes import *
from martepy.marte2.objects.message import MARTe2Message

from ..utilities import qapp, ensure_gc, create_node_mock

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizePolicy, QHBoxLayout, QWidget, QPushButton, QMainWindow, QLineEdit, QComboBox

def test_addrem_btns(qapp):
    add_rem_btn = AddRemoveHBtn()
    assert isinstance(add_rem_btn, QWidget)
    assert add_rem_btn.hlayout.__class__ == QHBoxLayout
    assert add_rem_btn.remove_btn.__class__ == QPushButton
    assert add_rem_btn.add_btn.__class__ == QPushButton

    assert add_rem_btn.add_btn.text() == 'Add'
    assert add_rem_btn.remove_btn.text() == 'Remove'
    assert add_rem_btn.hlayout.itemAt(0).widget().__class__ == QWidget
    assert add_rem_btn.hlayout.itemAt(1).widget() == add_rem_btn.add_btn
    assert add_rem_btn.hlayout.itemAt(2).widget() == add_rem_btn.remove_btn
    assert add_rem_btn.hlayout.itemAt(0).widget().sizePolicy() == QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

def test_custom_event(qapp):
    evt = CustomEvent("My Event")
    assert evt.event_type == "My Event"

def test_autocomplete(qapp, qtbot):
    wdw = QMainWindow()
    lineedt = AutoCompleteLineEdit(wdw, ['huieh', '1', 'test', 'auto','complete'], qapp)
    assert isinstance(lineedt, QLineEdit)
    # Can't really test this as requires consistent interaction
    
def test_PanelledListConfig(qapp):
    panel = PanelledListConfig()

def test_MsgInfoWidget(qapp):
    def funcChg(value):
        pass
    msginfo = MsgInfoWidget(None,funcChg,funcChg,funcChg,funcChg,funcChg)
    assert msginfo.msg_name.__class__ == QLineEdit
    assert msginfo.msg_dest.__class__ == QLineEdit
    assert msginfo.func.__class__ == QLineEdit
    assert msginfo.mode.__class__ == QComboBox
    assert msginfo.maxwait.__class__ == QLineEdit

def test_MsgWindow(qapp, create_node_mock, monkeypatch):
    msgs = [MARTe2Message()]
    wndw = MessageConfigWindow(create_node_mock.application, qapp, msgs, msgs, 'Message Window', None, None)
    
    assert wndw.main_wgt.left_list.count() == 1
    assert wndw.main_wgt.left_list.item(0).text() == 'Message'

    assert wndw.grid_wgt.msg_name.text() == 'Message'
    assert wndw.grid_wgt.msg_dest.text() == 'App'
    assert wndw.grid_wgt.func.text() == 'StopCurrentStateExecution'
    assert wndw.grid_wgt.maxwait.text() == '0'
    assert wndw.grid_wgt.mode.currentText() == 'ExpectsReply'

    assert wndw.paramname.text() == ''
    assert wndw.paramval.text() == ''

    wndw.add_remmsg.add_btn.clicked.emit()
    assert wndw.main_wgt.left_list.count() == 2
    assert wndw.main_wgt.left_list.item(1).text() == 'Message1'
    assert wndw.main_wgt.left_list.currentItem().text() == 'Message1'

    wndw.param_btns.add_btn.clicked.emit()
    assert wndw.param_config.left_list.count() == 1
    assert wndw.param_config.left_list.item(0).text() == 'func'
    
    # Test Parameter Name Change
    wndw.paramname.setText('funcy')
    wndw.paramNameChg()
    assert wndw.messages[1].parameters.objects == {'funcy': '1'}
    
    wndw.paramval.setText('42')
    wndw.paramValChg()
    assert wndw.messages[1].parameters.objects == {'funcy': '42'}

    wndw.grid_wgt.msg_name.setText('Messy')
    wndw.msgNameChg()
    assert wndw.main_wgt.left_list.item(1).text() == 'Messy'
    
    wndw.grid_wgt.maxwait.setText('30')
    wndw.waitChg()
    assert wndw.messages[1].maxwait == '30'
    
    wndw.grid_wgt.mode.setCurrentText('ExpectsIndirectReply')
    wndw.modeChg()
    assert wndw.messages[1].mode == 'ExpectsIndirectReply'

    wndw.remParam()
    assert wndw.messages[1].parameters.objects == {}
    
    wndw.remMsg()
    assert len(wndw.messages) == 1
    assert wndw.grid_wgt.msg_name.text() == 'Message'
    assert wndw.grid_wgt.msg_dest.text() == 'App'
    assert wndw.grid_wgt.func.text() == 'StopCurrentStateExecution'
    assert wndw.grid_wgt.maxwait.text() == '0'
    assert wndw.grid_wgt.mode.currentText() == 'ExpectsReply'

    wndw.msgChanged(None)
    assert wndw.grid_wgt.msg_name.text() == ''
    assert wndw.grid_wgt.msg_dest.text() == ''
    assert wndw.grid_wgt.func.text() == ''
    assert wndw.grid_wgt.maxwait.text() == ''
    assert wndw.grid_wgt.mode.currentText() == 'ExpectsReply'
    assert wndw.param_config.left_list.count() == 0
    
    wndw.main_wgt.left_list.setCurrentItem(wndw.main_wgt.left_list.item(0))
    wndw.grid_wgt.msg_name.setText('Messy')
    wndw.msgNameChg()
    monkeypatch.setattr(
        QMessageBox, 'question', lambda *args: QMessageBox.Save
    )
    
    wndw.close()
    assert msgs[0].configuration_name.lstrip('+') == 'Messy'

