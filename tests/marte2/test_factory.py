import pytest
import os

from martepy.marte2.factory import Factory

from martepy.marte2.gams import * 

from ..utilities import top_lvl

def test_factory():
    test_obj = Factory()
    json_file = os.path.join(top_lvl, 'martepy', 'marte2', 'gams', 'gams.json')

    test_obj.loadRemote(json_file)
    classes = {'ConstantGAM': ConstantGAM, 'ConversionGAM': ConversionGAM, 'ExpressionGAM': ExpressionGAM,
                                'MathExpressionGAM': ExpressionGAM, 'IOGAM': IOGAM, 'MessageGAM': MessageGAM, 'MuxGAM': MuxGAM,
                                'SSMGAM': SSMGAM, 'WaveformGAM::WaveformSin': WaveformSinGAM, 'WaveformSin': WaveformSinGAM,
                                'WaveformSinGAM': WaveformSinGAM, 'WaveformGAM::WaveformChirp': WaveformChirpGAM,
                                'WaveformChirp': WaveformChirpGAM, 'WaveformChirpGAM': WaveformChirpGAM,
                                'WaveformGAM::WaveformPointsDef': WaveformPointsGAM, 'WaveformPointsDef': WaveformPointsGAM,
                                'WaveformPointsGAM': WaveformPointsGAM, 'PIDGAM': PIDGAM, 'FilterGAM': FilterGAM}
    
    assert test_obj.classes == classes

    test_obj.unregisterBlock('SSMGAM')

    classes.pop('SSMGAM')

    assert test_obj.classes == classes

    with pytest.raises(ValueError) as excinfo:
        test_obj.unregisterBlock('SSMsGAM')
    assert str(excinfo.value) == "Unknown block type SSMsGAM"

    for key, value in classes.items():
        assert value == test_obj.create(key)

    with pytest.raises(ValueError) as excinfo:
        test_obj.create('SSMsGAM')
    assert str(excinfo.value) == "Unknown block type SSMsGAM"

    assert test_obj.getAll() == [ConstantGAM, ConversionGAM, ExpressionGAM, ExpressionGAM, IOGAM, MessageGAM, MuxGAM,
                                 WaveformSinGAM, WaveformSinGAM, WaveformSinGAM, WaveformChirpGAM, WaveformChirpGAM, WaveformChirpGAM,
                                 WaveformPointsGAM, WaveformPointsGAM, WaveformPointsGAM, PIDGAM, FilterGAM]
    
    test_obj.unloadAll()

    assert test_obj.classes == {}

    assert test_obj.getAll() == []