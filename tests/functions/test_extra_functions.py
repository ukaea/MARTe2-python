import pytest

from martepy.functions.extra_functions import calculateStackSize, form, findIndexByDictKey, isfloat

def test_calculate_stacksize():
    signals = [('Name1', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'uint32', 'Alias': 'Namealias', 'Default': '3.2', 'NumberOfElements': '1'}}),
               ('djgjkghf', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'uint8', 'Alias': 'AliasOut', 'NumberOfElements': '3'}}),
               ('tester', {'MARTeConfig': {'DataSource': 'FileWriter', 'Type': 'float64', 'Alias': 'tester', 'NumberOfElements': '8'}})]
    
    assert calculateStackSize(signals) == 71

def test_form():
    assert form('Name1','uint32','1','DDB0','Namealias','3.2') == [('Name1', {'MARTeConfig': {'DataSource': 'DDB0', 'Type': 'uint32', 'Alias': 'Namealias', 'Default': '3.2', 'NumberOfElements': '1'}})]
    assert form('djgjkghf','uint8','3','DDB1','AliasOut') == [('djgjkghf', {'MARTeConfig': {'DataSource': 'DDB1', 'Type': 'uint8', 'Alias': 'AliasOut', 'NumberOfElements': '3'}})]
    assert form('tester','float64','8','FileWriter') == [('tester', {'MARTeConfig': {'DataSource': 'FileWriter', 'Type': 'float64', 'Alias': 'tester', 'NumberOfElements': '8'}})]

def test_findIndexByDictKey():
    # Sample data
    list_of_dicts = [
        {'id': '001', 'name': 'Alice', 'value': '+123'},
        {'id': '002', 'name': 'Bob', 'value': '456'},
        {'id': '003', 'name': 'Charlie', 'value': '+789'},
    ]
    
    # Test cases
    assert findIndexByDictKey(list_of_dicts, 'id', '001') == 0
    assert findIndexByDictKey(list_of_dicts, 'name', 'Bob') == 1
    assert findIndexByDictKey(list_of_dicts, 'value', '123') == 0
    assert findIndexByDictKey(list_of_dicts, 'value', '456') == 1
    assert findIndexByDictKey(list_of_dicts, 'value', '789') == 2
    assert findIndexByDictKey(list_of_dicts, 'id', '004') == -1
    assert findIndexByDictKey(list_of_dicts, 'name', 'Dave') == -1
    assert findIndexByDictKey(list_of_dicts, 'value', '000') == -1

def test_float():
    assert isfloat('2.0')
    assert isfloat(2.0)
    assert not isfloat('2b')
    assert isfloat(2)
    assert isfloat('2')