''' Pythonic representation of ReferenceContainer '''

from martepy.marte2.config_object import MARTe2ConfigObject
from martepy.functions.extra_functions import getname

class MARTe2Object(MARTe2ConfigObject):
    ''' Pythonic representation of ReferenceContainer '''
    def __init__(self,
                    configuration_name: str = 'Message',
                    class_name = "ReferenceContainer",
                    objects = [],
                ):
        super().__init__()
        self.class_name = class_name
        self.objects = objects
        self.configuration_name = configuration_name

    def write(self, config_writer):
        ''' Write our configuration of this class '''
        config_writer.startClass('+' + getname(self), self.class_name)
        for obj in self.objects:
            obj.write(config_writer)
        config_writer.endSection('+' + getname(self))

    def serialize(self):
        ''' Serialize our object '''
        res = super().serialize()
        res['class_name'] = self.class_name
        res["objects"] = [a.serialize() for a in self.objects]
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True, # pylint: disable=W0221
                    factory=None) -> bool:
        ''' Deserialize our data into an instance of our class '''
        super().deserialize(data, hashmap, restore_id, factory=factory)
        self.class_name = data['class_name']
        def toObj(a):
            return factory.create(a['class_name'])().deserialize(a, factory=factory)
        # This part is tricky as a ref container can
        # contain any object so the factory needs to recircle here
        self.objects = [toObj(a) for a in data["objects"]]
        return self

def initialize(factory, plugin_datastore) -> None:
    ''' Register us with the factory '''
    factory.registerBlock("ReferenceContainer", MARTe2Object, plugin_datastore)
    factory.registerBlock("MARTe2Object", MARTe2Object, plugin_datastore)
