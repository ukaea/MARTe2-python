import pytest
from unittest.mock import patch
import pdb

from martepy.marte2.config_object import MARTe2ConfigObject
from martepy.marte2.configwriting import ConfigWriter
from martepy.functions.extra_functions import getname
from martepy.functions.gam_functions import getParameterName, getAlias

def test_config_obj():
    test_obj = MARTe2ConfigObject()
    assert str(repr(test_obj)) == '''_config_writer = None
configuration_name = 
'''
    test_obj.configuration_name = '+Hello_World'
    assert getname(test_obj) == 'Hello_World'

    with pytest.raises(TypeError) as excinfo:
        test_obj.setTab(2)
    assert str(excinfo.value) == 'This MARTe1ConfigObject has no _config_writer'

    writer = ConfigWriter()
    test_obj.setWriter(writer)
    assert test_obj._config_writer == writer
    test_obj.setTab(2)
    assert test_obj._config_writer.tab == 2

    with pytest.raises(NotImplementedError) as excinfo:
        test_obj.write(writer)

    with pytest.raises(NotImplementedError) as excinfo:
        str(test_obj)

    with pytest.raises(NotImplementedError) as excinfo:
        test_obj()

    writer = ConfigWriter()
    def fake_write(param):
        param.writeBareLine('I am a Pi')

    with patch.object(test_obj, 'write', fake_write):
        assert str(test_obj) == 'I am a Pi'
    
    assert getParameterName('IamA Parameter') == 'iama_parameter'

    assert getAlias(('Constant',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32','Default':'2'}})) == 'Constant'
    assert getAlias(('Constant',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32','Default':'2', 'Alias':'RenameCon'}})) == 'RenameCon'
