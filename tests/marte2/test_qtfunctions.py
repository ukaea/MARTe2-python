import pytest

from PyQt5.QtWidgets import QWidget, QSizePolicy, QApplication, QHBoxLayout, QLineEdit, QGridLayout, QComboBox, QListWidget, QListWidgetItem, QVBoxLayout, QLabel, QPushButton, QSpacerItem

from unittest.mock import MagicMock, patch

from martepy.marte2.qt_functions import *

from ..utilities import qapp, ensure_gc

def test_spacer(qapp):
    spc_wgt = spacer()
    spc_wgt.__class__ == QWidget
    spc_wgt.sizePolicy() == QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

def test_unique_name():
    assert 'myname3' == generateUniqueName(['myname1', 'myname2', 'myname', 'myname4'], 'myname')
    assert 'myname' == generateUniqueName(['myname1', 'myname2', 'myname3', 'myname4'], 'myname')

def test_unique_gam_name():
    assert 'DDB2' == generateUniqueGamName(['DDB0', 'DBB', 'DDB1', 'DDB3'])

def test_lineedit(qapp):
    test_layout = QHBoxLayout()
    mock_slot = MagicMock()
    edit = createLineEdit(test_layout, 'test_line_edt', mock_slot)

    assert edit.__class__ == QLineEdit
    edit.setText("New text")
    mock_slot.assert_called_once_with("New text")

def test_comboedit(qapp):
    test_layout = QHBoxLayout()
    mock_slot = MagicMock()
    combo_box = createComboEdit(test_layout, 'test_combo_edt', mock_slot, ['1', '2'])

    assert combo_box.__class__ == QComboBox

    # Simulate an index change
    combo_box.setCurrentIndex(1)  # Select the second item

    # Assert the slot was called with the correct index
    mock_slot.assert_called_once_with(1)

def test_gridlineedit(qapp):
    test_layout = QGridLayout()
    mock_slot = MagicMock()
    edit = createGridLineEdit(test_layout, 0, 'test_combo_edt', mock_slot)

    assert edit.__class__ == QLineEdit

    edit.setText("New text")
    mock_slot.assert_called_once_with("New text")

def test_gridcomboedit(qapp):
    test_layout = QGridLayout()
    mock_slot = MagicMock()
    combo_box = createGridComboEdit(test_layout, 0, 'test_combo_edt', mock_slot, ['1', '2'])

    assert combo_box.__class__ == QComboBox

    # Simulate an index change
    combo_box.setCurrentIndex(1)  # Select the second item

    # Assert the slot was called with the correct index
    mock_slot.assert_called_once_with(1)

def test_item_exists_in_list(qapp):
    # Create a QListWidget and add some items
    list_widget = QListWidget()
    list_widget.addItem(QListWidgetItem("Item 1"))
    list_widget.addItem(QListWidgetItem("Item 2"))
    list_widget.addItem(QListWidgetItem("Item 3"))

    # Test for an item that exists
    assert textExistsInListWidget(list_widget, "Item 1") == True
    assert textExistsInListWidget(list_widget, "Item 2") == True
    assert textExistsInListWidget(list_widget, "Item 3") == True

    # Test for an item that does not exist
    assert textExistsInListWidget(list_widget, "Item 4") == False

def test_delete_children(qapp):
    # Create a QWidget and QVBoxLayout
    parent_widget = QWidget()
    layout = QVBoxLayout(parent_widget)
    
    # Add some child widgets
    button = QPushButton("Button")
    label = QLabel("Label")
    layout.addWidget(button)
    layout.addWidget(label)

    # Ensure the layout has children
    assert layout.count() == 2

    # Patch deleteLater method to check if it's called
    with patch.object(button, 'deleteLater', wraps=button.deleteLater) as mock_delete_button, \
         patch.object(label, 'deleteLater', wraps=label.deleteLater) as mock_delete_label:
        
        # Call the function to delete children
        deleteChildren(layout)
        
        # Check that deleteLater was called on each widget
        mock_delete_button.assert_called_once()
        mock_delete_label.assert_called_once()

def test_set_layout_enabled(qapp):
    # Create a QWidget and main QVBoxLayout
    main_widget = QWidget()
    main_layout = QVBoxLayout(main_widget)
    
    # Add child widgets and layouts
    button1 = QPushButton("Button 1")
    label1 = QLabel("Label 1")
    main_layout.addWidget(button1)
    main_layout.addWidget(label1)
    
    sub_layout = QHBoxLayout()
    button2 = QPushButton("Button 2")
    label2 = QLabel("Label 2")
    sub_layout.addWidget(button2)
    sub_layout.addWidget(label2)
    
    main_layout.addLayout(sub_layout)
    
    # Ensure all widgets are initially enabled
    assert button1.isEnabled() == True
    assert label1.isEnabled() == True
    assert button2.isEnabled() == True
    assert label2.isEnabled() == True
    
    # Disable the entire layout
    recursivelySetEnabled(main_layout, False)
    
    # Check that all widgets are disabled
    assert button1.isEnabled() == False
    assert label1.isEnabled() == False
    assert button2.isEnabled() == False
    assert label2.isEnabled() == False
    
    # Enable the entire layout
    recursivelySetEnabled(main_layout, True)
    
    # Check that all widgets are enabled again
    assert button1.isEnabled() == True
    assert label1.isEnabled() == True
    assert button2.isEnabled() == True
    assert label2.isEnabled() == True

def test_add_button_layout(qapp):
    # Create mock functions for save and cancel
    mock_save_function = MagicMock()
    mock_cancel_function = MagicMock()

    # Create the main layout
    main_layout = QVBoxLayout()
    
    # Add the button layout to the main layout
    defineSaveCancelButtons(main_layout, mock_save_function, mock_cancel_function)
    
    # Create a QWidget to set the main layout (necessary to properly test)
    main_widget = QWidget()
    main_widget.setLayout(main_layout)

    # Check that the main layout contains the parent widget
    assert main_layout.count() == 1

    # Retrieve the parent widget and its layout
    parent_widget = main_layout.itemAt(0).widget()
    assert parent_widget is not None
    
    parent_layout = parent_widget.layout()
    assert isinstance(parent_layout, QHBoxLayout)
    
    # Check the layout contains the expected number of items
    assert parent_layout.count() == 3  # 1 spacer + 2 buttons

    # Retrieve the widgets from the parent layout
    spacer_item = parent_layout.itemAt(0).widget()
    save_button = parent_layout.itemAt(1).widget()
    cancel_button = parent_layout.itemAt(2).widget()
    
    # Check the types of the items
    assert isinstance(spacer_item, QWidget)
    assert isinstance(save_button, QPushButton)
    assert isinstance(cancel_button, QPushButton)
    
    # Check the text of the buttons
    assert save_button.text() == "Save"
    assert cancel_button.text() == "Cancel"
    
    # Simulate button clicks
    save_button.click()
    cancel_button.click()
    
    # Check that the mock functions were called
    mock_save_function.assert_called_once()
    mock_cancel_function.assert_called_once()
    