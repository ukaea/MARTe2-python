import pytest
import copy
import pdb

from martepy.marte2.configwriting import StringConfigWriter
from martepy.marte2.datasource import MARTe2DataSource

def test_datasource():
    test_obj = MARTe2DataSource('+HelloWorld','FileReader',
                                [('Constant',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32','Default':'2'}})],
                                [('Constant',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32','Default':'2'}})])
    
    writer = StringConfigWriter()
    with pytest.raises(NotImplementedError) as excinfo:
        test_obj.writeDatasourceConfig(writer)

    test_obj.writeInputSignals(writer)
    assert str(repr(writer)) == '''InputSignals = {
    Constant = {
        Type = uint32
        Default = 2
    }
}'''

    writer = StringConfigWriter()
    test_obj.writeOutputSignals(writer)
    assert str(repr(writer)) == '''OutputSignals = {
    Constant = {
        Type = uint32
        Default = 2
    }
}'''

    writer = StringConfigWriter()
    with pytest.raises(NotImplementedError) as excinfo:
        test_obj.write(writer)
    assert str(repr(writer)) == '''+HelloWorld = {
    Class = FileReader'''

    writer = StringConfigWriter()
    test_obj.writeSignals([('Constant',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32','Default':'2'}})], writer)
    assert str(repr(writer)) == '''Constant = {
    Type = uint32
    Default = 2
}'''

    def override_none(param):
        return ''
    writer = StringConfigWriter()
    test_obj.writeDatasourceConfig = override_none
    test_obj.write(writer)
    assert str(repr(writer)) == '+HelloWorld = {\n    Class = FileReader\n}'

    basic_copy = copy.deepcopy(test_obj)
    assert basic_copy == test_obj
    basic_copy.configuration_name = 'FailName'
    assert not basic_copy == test_obj

    intermediary = MARTe2DataSource().deserialize(test_obj.serialize())
    intermediary.class_name = 'FileReader'
    assert test_obj == intermediary
