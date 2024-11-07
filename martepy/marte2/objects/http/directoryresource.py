''' Pythonic representation of the directory resource '''

from martepy.marte2.config_object import MARTe2ConfigObject
from martepy.functions.extra_functions import getname

class MARTe2HttpDirectoryResource(MARTe2ConfigObject):
    ''' Pythonic representation of the directory resource '''
    def __init__(self,
                    configuration_name: str = 'WebRoot',
                    basedir = "",
                ):
        self.class_name = 'HttpDirectoryResource'
        self.basedir = basedir
        super().__init__()
        self.configuration_name = configuration_name

    def write(self, config_writer):
        ''' Write the configuration of our object '''
        config_writer.startClass('+' + getname(self), self.class_name)
        config_writer.writeNode('BaseDir', f'"{self.basedir}"')
        config_writer.endSection('+' + getname(self))

    def serialize(self):
        ''' Serialize the object '''
        res = super().serialize()
        res['class_name'] = self.class_name
        res['basedir'] = self.basedir
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True, # pylint: disable=W0221
                    factory=None) -> bool:
        ''' Deserialize the given data to our class instance '''
        super().deserialize(data, hashmap, restore_id, factory=factory)
        self.class_name = data["class_name"]
        self.basedir = data['basedir']
        return self

def initialize(factory, plugin_datastore) -> None:
    ''' Register the object with the factory '''
    factory.registerBlock("HttpDirectoryResource", MARTe2HttpDirectoryResource, plugin_datastore)
