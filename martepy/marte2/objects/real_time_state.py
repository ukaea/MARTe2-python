''' Pythonic representation of RealTimeState '''

from martepy.marte2.config_object import MARTe2ConfigObject
from martepy.marte2.objects.referencecontainer import MARTe2ReferenceContainer
from martepy.functions.extra_functions import getname

def genericThread():
    ''' Return an empty Ref Container '''
    return MARTe2ReferenceContainer(configuration_name='Threads',objects=[])

class MARTe2RealTimeState(MARTe2ConfigObject):
    """Object for configuring RealTimeStates for MARTe2 applications"""

    def __init__(self,
                    configuration_name: str = '+State',
                    threads: MARTe2ReferenceContainer = genericThread(),
                ):
        super().__init__()
        self.configuration_name = configuration_name
        self.class_name = 'RealTimeState'
        self.threads = threads

    def write(self, config_writer):
        ''' Write our configuration of this class '''
        config_writer.startClass('+' + getname(self), self.class_name)
        self.threads.write(config_writer)
        config_writer.endSection('+' + getname(self))

    def serialize(self):
        ''' Serialize our object '''
        res = super().serialize()
        res['class_name'] = self.class_name
        res['threads'] = self.threads.serialize()
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True, # pylint: disable=W0221
                    factory=None) -> bool:
        ''' Deserialize our data into an instance of our class '''
        super().deserialize(data, hashmap, restore_id, factory=factory)
        self.class_name = data["class_name"]
        self.threads = factory.create('ReferenceContainer')().deserialize(data["threads"],
                                                                          factory=factory)
        return self

def initialize(factory, plugin_datastore) -> None:
    ''' Register us with the factory '''
    factory.registerBlock("RealTimeState", MARTe2RealTimeState, plugin_datastore)
