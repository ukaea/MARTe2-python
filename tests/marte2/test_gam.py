import pytest

from martepy.marte2.gam import MARTe2GAM
from martepy.functions.gam_functions import getAlias

@pytest.mark.parametrize(
    "configuration_name, class_name, names, input_signals, output_signals",
    [
        ("dummyvalue",'IOGAM','Constantf',[('Constantf',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32'}})], [('Constanti',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})]),
        ("dummyvalue1",'MSHKDH','Hello',[('Hello',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}}),('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float64','Alias':'HW'}})],[('Helloout',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint64'}}),('Worldout',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','Alias':'HW'}})]),
        ("dummyvalue2",'SSMGAM','dhkhfe',[('World',{'MARTeConfig':{'Alias': 'dhkhfe', 'DataSource':'DDB0','Type':'float32','NumberOfElements':3}})],[('dout',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint64','NumberOfElements':3}})]),
        ("dummyvalue2",'MuxGAM','World',[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3,'NumberOfDimensions':'1'}})],[('small_int',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint8','NumberOfElements':3,'NumberOfDimensions':'1'}})])
    ]
)
def test_gam(configuration_name, class_name, input_signals, output_signals, names):

    test_obj = MARTe2GAM(configuration_name=configuration_name, class_name=class_name, input_signals=input_signals, output_signals=output_signals)

    assert test_obj.inputs == input_signals
    assert test_obj.outputs == output_signals

    with pytest.raises(NotImplementedError) as excinfo:
        test_obj.writeGamConfig(None)

    assert test_obj.isOrderingRank0() == False

    # Just test that these can execute without error
    test_obj.loadParameters(None, None)

    with pytest.raises(NotImplementedError) as excinfo:
        test_obj.runOde()

    assert getAlias(input_signals[0]) == names

    assert test_obj.serialize() == {'configuration_name': configuration_name, 'inputsb': input_signals,
                                    'outputsb': output_signals, 'class_name': class_name,
                                    'block_type': class_name, 'comment': '', 'rank': False, 'plugin': 'marte2', 'label': class_name,
                                    'parameters': {'Class name': class_name}, 'content': {}, 'inputs': [], 'outputs': [],
                                    'id': id(test_obj), 'pos_x': 0, 'title': f'{configuration_name} ({class_name})', 'pos_y': 0}

    second_gam = MARTe2GAM().deserialize(test_obj.serialize())
    second_gam.class_name = class_name
    assert second_gam == test_obj

    second_gam.input_signals = []

    assert not second_gam == test_obj
