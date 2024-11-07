''' Pythonic representation of ReferenceContainer '''
from martepy.marte2.config_object import MARTe2ConfigObject
from martepy.functions.extra_functions import getname

class MARTe2ReferenceContainer(MARTe2ConfigObject):
    ''' Pythonic representation of ReferenceContainer '''
    def __init__(self,
                    configuration_name: str = 'Message',
                    objects = [],
                ):
        super().__init__(
            )
        self.class_name = "ReferenceContainer"
        self.objects = objects
        self.configuration_name = configuration_name

    def write(self, config_writer):
        ''' Write our configuration of this class '''
        config_writer.startClass('+' + getname(self),"ReferenceContainer")
        for obj in self.objects:
            obj.write(config_writer)
        config_writer.endSection('+' + getname(self))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.configuration_name == other.configuration_name:
                if self.objects == other.objects:
                    return True
        return False

    def serialize(self):
        ''' Serialize our object '''
        res = super().serialize()
        res['class_name'] = self.class_name
        res["objects"] = [a.serialize() for a in self.objects]
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True, #pylint: disable=W0221
                    factory=None) -> bool:
        ''' Deserialize our data into an instance of our class '''

        def createObj(a):
            return factory.create(a['class_name'])().deserialize(a, factory=factory)
        super().deserialize(data, hashmap, restore_id, factory=factory)
        self.class_name = data["class_name"]
        # This part is tricky as a ref container can
        # contain any object so the factory needs to recircle here
        self.objects = [createObj(a) for a in data["objects"]]
        return self

def initialize(factory, plugin_datastore) -> None:
    ''' Register us with the factory '''
    factory.registerBlock("ReferenceContainer", MARTe2ReferenceContainer, plugin_datastore)
