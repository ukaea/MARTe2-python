import pytest
import pdb
from martepy.marte2.gams.iogam import IOGAM
from martepy.marte2.gams.constant_gam import ConstantGAM
from martepy.marte2.gams.mux import MuxGAM

from martepy.functions.gam_functions import consolidate

def test_consolidate():
    functions = []
    consolidate(functions,'IOGAM','helloworld',[('Constant',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})], [('Constant',{'MARTeConfig':{'DataSource':'DDB1','Type':'uint32'}})])
    consolidate(functions,'IOGAM','helloworld',[('Constant1',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})], [('Constant1',{'MARTeConfig':{'DataSource':'DDB1','Type':'uint32'}})])

    assert len(functions) == 1
    assert len(functions[0].input_signals) == 2
    assert len(functions[0].output_signals) == 2

    consolidate(functions,'IOGAM','helloworldb',[('Constant',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})], [('Constant',{'MARTeConfig':{'DataSource':'DDB1','Type':'uint32'}})])
    consolidate(functions,'IOGAM','helloworldc',[('Constant1',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})], [('Constant1',{'MARTeConfig':{'DataSource':'DDB1','Type':'uint32'}})], prepend=True)

    assert len(functions) == 3
    assert len(functions[2].input_signals) == 1
    assert len(functions[2].output_signals) == 1
    # Test that our last function was inserted to the start of our functions list
    assert functions[0].configuration_name == 'helloworldc'
    assert len(functions[0].input_signals) == 1
    assert len(functions[0].output_signals) == 1

    functions = []
    consolidate(functions,'ConstantGAM','helloworld',outputs = [('Constant',{'MARTeConfig':{'DataSource':'DDB1','Type':'uint32', 'Default':'0.3'}})])
    consolidate(functions,'ConstantGAM','helloworld',outputs = [('Constant1',{'MARTeConfig':{'DataSource':'DDB1','Type':'uint32', 'Default':'3'}})])
    consolidate(functions,'ConstantGAM','helloworldb',outputs = [('Constant2',{'MARTeConfig':{'DataSource':'DDB1','Type':'uint32', 'Default':'5'}})],prepend=True)

    assert len(functions) == 2

    assert len(functions[1].input_signals) == 0
    assert len(functions[1].output_signals) == 2

    assert functions[0].configuration_name == 'helloworldb'
    assert len(functions[0].output_signals) == 1

    functions = []
    consolidate(functions,'MuxGAM','helloworld',[('Constant',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})], [('Constant',{'MARTeConfig':{'DataSource':'DDB1','Type':'uint32'}})])
    consolidate(functions,'MuxGAM','helloworld',[('Constant1',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})], [('Constant1',{'MARTeConfig':{'DataSource':'DDB1','Type':'uint32'}})])

    assert len(functions) == 1
    assert len(functions[0].input_signals) == 2
    assert len(functions[0].output_signals) == 2

    consolidate(functions,'MuxGAM','helloworldb',[('Constant',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})], [('Constant',{'MARTeConfig':{'DataSource':'DDB1','Type':'uint32'}})])

    assert len(functions) == 2
    assert len(functions[1].input_signals) == 1
    assert len(functions[1].output_signals) == 1

    # Here we test that if an output signal is unique, but the input signal is not
    # We still add the signal but give the input a unique signalname as well.
    # This is useful when we're assuming here that the output signal is a converted
    # signal type and the user would like to convert the same signal into multiple formats
    # this simplifies that process for them by maintaining the alias whilst giving it a
    # different signal name.
    functions = []
    consolidate(functions,'ConversionGAM','helloworld',[('Constant',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})], [('Constant',{'MARTeConfig':{'DataSource':'DDB1','Type':'uint32'}})])
    consolidate(functions,'ConversionGAM','helloworld',[('Constant1',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})], [('Constant1',{'MARTeConfig':{'DataSource':'DDB1','Type':'uint32'}})])

    assert len(functions) == 1
    assert len(functions[0].input_signals) == 2
    assert len(functions[0].output_signals) == 2

    consolidate(functions,'ConversionGAM','helloworld',[('Constant',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})], [('Constant2',{'MARTeConfig':{'DataSource':'DDB1','Type':'uint32'}})])
    consolidate(functions,'ConversionGAM','helloworld',[('Constant',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})], [('Constant3',{'MARTeConfig':{'DataSource':'DDB1','Type':'uint32'}})])
    assert len(functions) == 1
    assert len(functions[0].input_signals) == 4
    assert len(functions[0].output_signals) == 4

    assert functions[0].input_signals[0]
    assert functions[0].input_signals[2][0] == 'Constant_1'
    assert functions[0].input_signals[3][0] == 'Constant_2'
