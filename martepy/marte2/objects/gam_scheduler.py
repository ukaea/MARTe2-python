''' Pythonic representation of GAMScheduler '''

import logging
logger = logging.getLogger(__name__)

from martepy.marte2.config_object import MARTe2ConfigObject
from martepy.functions.extra_functions import getname

class MARTe2GAMScheduler(MARTe2ConfigObject):
    """Object for configuring the default MARTe2 GAM scheduler"""

    def __init__(self,
                    configuration_name: str = '+Scheduler',
                    class_name: str = 'GAMScheduler',
                    timing_datasource_name: str = None,
                    maxcycles = 0
                ):
        super().__init__(configuration_name = configuration_name)
        self.class_name = class_name
        self.timing_datasource_name = timing_datasource_name
        self.maxcycles = maxcycles

    def write(self, config_writer):
        ''' Write our configuration of this class '''
        config_writer.startClass('+' + getname(self), self.class_name)
        config_writer.writeNode('TimingDataSource', self.timing_datasource_name)
        config_writer.writeNode('MaxCycles', self.maxcycles)
        config_writer.endSection('+' + getname(self))

    def serialize(self):
        ''' Serialize our object '''
        res = super().serialize()
        res['class_name'] = self.class_name
        res['timing_datasource_name'] = self.timing_datasource_name
        res['maxcycles'] = self.maxcycles
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True, # pylint: disable=W0221
                    factory=None) -> bool:
        ''' Deserialize our data into an instance of our class '''
        super().deserialize(data, hashmap, restore_id, factory=factory)
        self.class_name = data["class_name"]
        self.timing_datasource_name = data["timing_datasource_name"]
        self.maxcycles = data["maxcycles"]
        return self

def initialize(factory, plugin_datastore) -> None:
    ''' Register us with the factory '''
    factory.registerBlock("GAMScheduler", MARTe2GAMScheduler, plugin_datastore)
