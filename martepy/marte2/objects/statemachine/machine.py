''' Pythonic representation of the state machine object '''

from martepy.marte2.config_object import MARTe2ConfigObject
from martepy.functions.extra_functions import getname

class MARTe2StateMachine(MARTe2ConfigObject):
    ''' Pythonic representation of the state machine object '''
    def __init__(self,
                    configuration_name: str = 'GOTOSTATE1',
                    states = [],
                ):
        super().__init__(
            )
        self.class_name = "StateMachine"
        self.configuration_name = configuration_name
        self.states = states

    def addstate(self,state: list):
        ''' Safe method to add states to the machine '''
        self.states += state

    def write(self, config_writer):
        ''' Write the configuration of our object '''
        config_writer.startClass('+' + getname(self),"StateMachine")
        for state in self.states:
            state.write(config_writer)
        config_writer.endSection('+' + getname(self))

    def serialize(self):
        ''' Serialize the object '''
        res = super().serialize()
        res['class_name'] = self.class_name
        res["states"] = [a.serialize() for a in self.states]
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True, # pylint: disable=W0221
                    factory=None) -> bool:
        ''' Deserialize the given data to our class instance '''
        def createObj(a):
            return factory.create(a['class_name'])().deserialize(a, factory=factory)
        super().deserialize(data, hashmap, restore_id, factory=factory)
        self.class_name = data['class_name']
        self.states = [createObj(a) for a in data['states']]
        return self

def initialize(factory, plugin_datastore) -> None:
    ''' Register the object with the factory '''
    factory.registerBlock("StateMachine", MARTe2StateMachine, plugin_datastore)
