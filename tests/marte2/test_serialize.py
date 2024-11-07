import pytest

from martepy.marte2.serialize import Serializable

def test_serialize():
    serial = Serializable()
    assert serial.id == id(serial)
    with pytest.raises(NotImplementedError) as excinfo:
        serial.serialize()
    with pytest.raises(NotImplementedError) as excinfo:
        serial.deserialize({})