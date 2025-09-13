import pytest

from martepy.marte2.gams import SimulinkGAM
from martepy.marte2.gams.simulink_gam import initialize
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget, QComboBox

from ...utilities import *

@pytest.mark.parametrize(
    "configuration_name, library, symbolprefix, Verbosity, skipinvalidtunableparams, EnforceModelSignalCoverage, TunableParamExternalSource, NonVirtualBusMode, input_signals, output_signals",
    [
        ("dummyvalue", "Controller.so", "Controller", "1", "1", 0, "",'Structured',[('Constant',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32','NumberOfElements':'1','NumberOfDimensions':'1'}})],[('Constanti',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}})]),
        ("dummyvalue1", "Model.so", "Model", 1, 0, "0", "",'Structured',[('Hello',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint32'}}),('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float64','Alias':'HW'}})],[('Helloout',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint64'}}),('Worldout',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','Alias':'HW'}})]),
        ("dummyvalue2", "Controller.so", "Controller", 0, 1, 1, "",'Structured',[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3}})],[('dout',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint64','NumberOfElements':3}})]),
        ("dummyvalue2", "Model.so", "Model", "0", "1", "1", "",'Structured',[('World',{'MARTeConfig':{'DataSource':'DDB0','Type':'float32','NumberOfElements':3,'NumberOfDimensions':'1'}})],[('small_int',{'MARTeConfig':{'DataSource':'DDB0','Type':'uint8','NumberOfElements':3,'NumberOfDimensions':'1'}})])
    ]
)
def test_SSMGAM(configuration_name, library, symbolprefix, Verbosity,
                skipinvalidtunableparams, EnforceModelSignalCoverage,
                TunableParamExternalSource, NonVirtualBusMode, input_signals,
                output_signals, load_parameters):
    setup_writer = marteconfig.StringConfigWriter()
    example_simgam = SimulinkGAM(configuration_name, input_signals,
                    output_signals,
                    library,
                    symbolprefix,
                    Verbosity,
                    skipinvalidtunableparams,
                    EnforceModelSignalCoverage,
                    TunableParamExternalSource,
                    NonVirtualBusMode)
    
    # Assert attributes
    assert example_simgam.configuration_name == configuration_name
    assert example_simgam.library == library
    assert example_simgam.symbolprefix == symbolprefix
    assert example_simgam.verbosity == Verbosity
    assert example_simgam.skipinvalidtunableparams == int(skipinvalidtunableparams)
    assert example_simgam.enforcemodelsignalcoverage == int(EnforceModelSignalCoverage)
    assert example_simgam.tunableparamexternalsource == TunableParamExternalSource
    assert example_simgam.nonvirtualbusmode == NonVirtualBusMode
    assert example_simgam.output_signals == output_signals
    assert example_simgam.input_signals == input_signals

    # Assert Serializations
    assert example_simgam.serialize()['configuration_name'] == configuration_name
    assert example_simgam.serialize()['parameters']['library'] == library
    assert example_simgam.serialize()['parameters']['symbolprefix'] == symbolprefix
    assert example_simgam.serialize()['parameters']['verbosity'] == Verbosity
    assert example_simgam.serialize()['parameters']['skipinvalidtunableparams'] == int(skipinvalidtunableparams)
    assert example_simgam.serialize()['parameters']['enforcemodelsignalcoverage'] == int(EnforceModelSignalCoverage)
    assert example_simgam.serialize()['parameters']['tunableparamexternalsource'] == TunableParamExternalSource
    assert example_simgam.serialize()['parameters']['nonvirtualbusmode'] == NonVirtualBusMode
    assert example_simgam.serialize()['inputsb'] == input_signals
    assert example_simgam.serialize()['outputsb'] == output_signals

    # Assert Deserialization
    new_simgam = SimulinkGAM().deserialize(example_simgam.serialize())
    assert new_simgam.configuration_name.lstrip('+') == configuration_name
    assert new_simgam.library == library
    assert new_simgam.symbolprefix == symbolprefix
    assert new_simgam.verbosity == Verbosity
    assert new_simgam.skipinvalidtunableparams == int(skipinvalidtunableparams)
    assert new_simgam.enforcemodelsignalcoverage == int(EnforceModelSignalCoverage)
    assert new_simgam.tunableparamexternalsource == TunableParamExternalSource
    assert new_simgam.nonvirtualbusmode == NonVirtualBusMode
    assert new_simgam.output_signals == output_signals
    assert new_simgam.input_signals == input_signals

    # Assert config written
    example_simgam.write(setup_writer)
    test_writer = writeSignals_section(input_signals, output_signals)


def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('SimulinkGAM') == SimulinkGAM
