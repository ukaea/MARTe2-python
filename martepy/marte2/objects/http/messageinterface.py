''' Pythonic representation of the HTTP message interface '''

from martepy.marte2.config_object import MARTe2ConfigObject
from martepy.functions.extra_functions import getname
from martepy.marte2.objects.message import MARTe2Message

class MARTe2HttpMessageInterface(MARTe2ConfigObject):
    ''' Pythonic representation of the HTTP message interface '''
    def __init__(self,
                    configuration_name: str = 'WebRoot',
                    objects = [],
                ):
        self.class_name = 'HttpMessageInterface'
        super().__init__()
        self.configuration_name = configuration_name
        self.objects = objects

    def write(self, config_writer):
        ''' Write the configuration of our object '''
        config_writer.startClass('+' + getname(self), self.class_name)
        for obj in self.objects:
            obj.write(config_writer)
        config_writer.endSection('+' + getname(self))

    def serialize(self):
        ''' Serialize the object '''
        res = super().serialize()
        res['class_name'] = self.class_name
        res["objects"] = [a.serialize() for a in self.objects]
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True, # pylint: disable=W0221
                    factory=None) -> bool:
        ''' Deserialize the given data to our class instance '''
        super().deserialize(data, hashmap, restore_id, factory=factory)
        self.class_name = data["class_name"]
        self.objects = [MARTe2Message().deserialize(a) for a in data["objects"]]
        return self

def initialize(factory, plugin_datastore) -> None:
    ''' Register the object with the factory '''
    factory.registerBlock("HttpMessageInterface", MARTe2HttpMessageInterface, plugin_datastore)
