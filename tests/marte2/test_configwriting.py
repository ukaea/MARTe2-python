import pytest

from martepy.marte2.configwriting import ConfigWriter, StringConfigWriter

def test_string_writer():
    test_obj = StringConfigWriter()
    test_obj.lines = ['test','my','lines']
    assert test_obj.toString() == '''test\nmy\nlines'''

def test_configwriter():
    test_obj = ConfigWriter()

    with pytest.raises(NotImplementedError) as excinfo:
        test_obj._output('line')

    test_obj = StringConfigWriter()
    
    test_obj.startSection('HelloWorld')

    with pytest.raises(IndexError) as excinfo:
        test_obj.setTab(2)
    assert str(excinfo.value) == 'Asked to setTab(2) when stack isn\'t empty.\nTab = 1, Stack = HelloWorld'

    with pytest.warns(UserWarning, match="Setting tab, section stack isn't empty! Tab was 1, now 2"):
        test_obj.setTab(2, override=True)

    with pytest.raises(IndexError) as excinfo:
        test_obj.endSection('World')
    assert str(excinfo.value) == 'Failed trying to close section "World"'

    test_obj.tab = -2
    with pytest.raises(IndexError) as excinfo:
        test_obj.getPrefix()
    assert str(excinfo.value) == 'Tab Error, tab is set to: -2'
    test_obj = StringConfigWriter()
    test_obj.writeMARTe2Vector('Defaults', [0.9793,898.8797,8.8766], formatAsFloat=True)
    assert str(repr(test_obj)) == 'Defaults = { 0.9793 898.88 8.8766 }'

