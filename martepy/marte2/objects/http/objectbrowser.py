''' Pythonic representation of the HTTP Object Browser '''

from martepy.marte2.config_object import MARTe2ConfigObject
from martepy.functions.extra_functions import getname
from martepy.marte2.objects.http.directoryresource import MARTe2HttpDirectoryResource
from martepy.marte2.objects.http.messageinterface import MARTe2HttpMessageInterface
from martepy.marte2.objects.message import MARTe2Message

class MARTe2HTTPObjectBrowser(MARTe2ConfigObject):
    ''' Pythonic representation of the HTTP Object Browser '''
    def __init__(self,
                    configuration_name: str = 'WebRoot',
                    root: str = '',
                    objects = [],
                ):
        self.class_name = 'HttpObjectBrowser'
        super().__init__()
        self.configuration_name = configuration_name
        self.root = root
        self.objects = objects
        self.possible_objects = {'HttpObjectBrowser': self.__class__,
                    'HttpDirectoryResource': MARTe2HttpDirectoryResource,
                    'HttpMessageInterface': MARTe2HttpMessageInterface,
                    'Message': MARTe2Message}

    def write(self, config_writer):
        ''' Write the configuration of our object '''
        config_writer.startClass('+' + getname(self), self.class_name)
        config_writer.writeNode('Root', f'"{self.root}"')
        for obj in self.objects:
            obj.write(config_writer)
        config_writer.endSection('+' + getname(self))

    def serialize(self):
        ''' Serialize the object '''
        res = super().serialize()
        res['class_name'] = self.class_name
        res['root'] = self.root
        res['objects'] = [a.serialize() for a in self.objects]
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True, # pylint: disable=W0221
                    factory=None) -> bool:
        ''' Deserialize the given data to our class instance '''
        super().deserialize(data, hashmap, restore_id, factory)
        self.class_name = data["class_name"]
        self.root = data['root']
        self.objects = []
        for obj in data['objects']:
            class_obj = self.possible_objects[obj['class_name']]()
            self.objects.append(class_obj.deserialize(obj))
        return self

def initialize(factory, plugin_datastore) -> None:
    ''' Register the object with the factory '''
    factory.registerBlock("HttpObjectBrowser", MARTe2HTTPObjectBrowser, plugin_datastore)
