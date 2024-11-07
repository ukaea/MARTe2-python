import pytest

from martepy.marte2.objects.gam_scheduler import MARTe2GAMScheduler, initialize
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from ...utilities import *

@pytest.mark.parametrize(
    "configuration_name, maxcycles, timing_datasource_name",
    [
        ("dummyvalue", "500", "GAMScheduler"),
        ("dummyvalue1", 500, "FastScheduler"),
        ("dummyvalue2", 2, "GAMBareScheduler"),
        ("dummyvalue2", "2", "FastScheduler")
    ]
)
def test_MARTe2GAMScheduler(configuration_name, maxcycles, timing_datasource_name):
    setup_writer = marteconfig.StringConfigWriter()
    example_marte2gamscheduler = MARTe2GAMScheduler(configuration_name=configuration_name, maxcycles=maxcycles, timing_datasource_name=timing_datasource_name)
    
    # Assert attributes
    assert example_marte2gamscheduler.configuration_name == configuration_name
    assert example_marte2gamscheduler.maxcycles == maxcycles
    assert example_marte2gamscheduler.timing_datasource_name == timing_datasource_name

    # Assert Serializations
    assert example_marte2gamscheduler.serialize()['configuration_name'] == configuration_name
    assert example_marte2gamscheduler.serialize()['maxcycles'] == maxcycles
    assert example_marte2gamscheduler.serialize()['timing_datasource_name'] == timing_datasource_name

    # Assert Deserialization
    new_marte2gamscheduler = MARTe2GAMScheduler().deserialize(example_marte2gamscheduler.serialize())
    assert new_marte2gamscheduler.configuration_name.lstrip('+') == configuration_name
    assert new_marte2gamscheduler.maxcycles == maxcycles
    assert new_marte2gamscheduler.timing_datasource_name == timing_datasource_name

    # Assert config written
    example_marte2gamscheduler.write(setup_writer)

    assert str(setup_writer) == f'''+{configuration_name} = {{
    Class = GAMScheduler
    TimingDataSource = {timing_datasource_name}
    MaxCycles = {maxcycles}
}}'''

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('GAMScheduler') == MARTe2GAMScheduler