import pytest

from martepy.marte2.objects.http.service import MARTe2HttpService, initialize
from martepy.marte2.factory import Factory
import martepy.marte2.configwriting as marteconfig

from ...utilities import *

@pytest.mark.parametrize(
    "accepttimeout, configuration_name, listenmaxconnections, maxnumberofthreads, minnumberofthreads, port, timeout, webroot",
    [
        ("1000", "dummyvalue", 255, "4", "1", "40", "-1", "WebRoot"),
        ("500", "dummyvalue1", "255", "25", "2", "8080", "100", "WebRoot"),
        (500, "dummyvalue2", "1000", 25, 2, 40, 0, "WebRoot"),
        (1000, "dummyvalue2", 1000, 4, 1, 8080, -1, "WebRoot")
    ]
)
def test_MARTe2HttpService(accepttimeout, configuration_name, listenmaxconnections, maxnumberofthreads, minnumberofthreads, port, timeout, webroot):
    setup_writer = marteconfig.StringConfigWriter()
    example_marte2httpservice = MARTe2HttpService(accepttimeout=accepttimeout, configuration_name=configuration_name, listenmaxconnections=listenmaxconnections, maxnumberofthreads=maxnumberofthreads, minnumberofthreads=minnumberofthreads, port=port, timeout=timeout, webroot=webroot)
    
    # Assert attributes
    assert example_marte2httpservice.accepttimeout == accepttimeout
    assert example_marte2httpservice.configuration_name == configuration_name
    assert example_marte2httpservice.listenmaxconnections == listenmaxconnections
    assert example_marte2httpservice.maxnumberofthreads == maxnumberofthreads
    assert example_marte2httpservice.minnumberofthreads == minnumberofthreads
    assert example_marte2httpservice.port == port
    assert example_marte2httpservice.timeout == timeout
    assert example_marte2httpservice.webroot == webroot

    # Assert Serializations
    assert example_marte2httpservice.serialize()['accepttimeout'] == accepttimeout
    assert example_marte2httpservice.serialize()['configuration_name'] == configuration_name
    assert example_marte2httpservice.serialize()['listenmaxconnections'] == listenmaxconnections
    assert example_marte2httpservice.serialize()['maxnumberofthreads'] == maxnumberofthreads
    assert example_marte2httpservice.serialize()['minnumberofthreads'] == minnumberofthreads
    assert example_marte2httpservice.serialize()['port'] == port
    assert example_marte2httpservice.serialize()['timeout'] == timeout
    assert example_marte2httpservice.serialize()['webroot'] == webroot

    # Assert Deserialization
    new_marte2httpservice = MARTe2HttpService().deserialize(example_marte2httpservice.serialize())
    assert new_marte2httpservice.accepttimeout == accepttimeout
    assert new_marte2httpservice.configuration_name.lstrip('+') == configuration_name
    assert new_marte2httpservice.listenmaxconnections == listenmaxconnections
    assert new_marte2httpservice.maxnumberofthreads == maxnumberofthreads
    assert new_marte2httpservice.minnumberofthreads == minnumberofthreads
    assert new_marte2httpservice.port == port
    assert new_marte2httpservice.timeout == timeout
    assert new_marte2httpservice.webroot == webroot

    # Assert config written
    example_marte2httpservice.write(setup_writer)

    assert str(setup_writer) == f'''+{configuration_name} = {{
    Class = HttpService
    Port = "{port}"
    WebRoot = "{webroot}"
    Timeout = "{timeout}"
    ListenMaxConnections = "{listenmaxconnections}"
    AcceptTimeout = "{accepttimeout}"
    MaxNumberOfThreads = "{maxnumberofthreads}"
    MinNumberOfThreads = "{minnumberofthreads}"
}}'''

def test_factory_implementation():
    factory = Factory()
    initialize(factory, factory.classes)
    assert factory.create('HttpService') == MARTe2HttpService