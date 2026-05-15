''' Pythonic representation of the state machine object '''

from martepy.marte2.config_object import MARTe2ConfigObject
from martepy.functions.extra_functions import getname

class MARTe2StateMachine(MARTe2ConfigObject):
    ''' Pythonic representation of the state machine object '''
    def __init__(self,
                    configuration_name: str = 'GOTOSTATE1',
                    states: list = [],
                ):
        super().__init__(
            )
        self.class_name = "StateMachine"
        self.configuration_name = configuration_name.lstrip('+')
        self.states = states

    # pylint: disable=line-too-long
    def toPython(self, app_name):
        header = "from martepy.marte2.objects.statemachine.machine import MARTe2StateMachine\n"

        content = f"""_{self.configuration_name} = MARTe2StateMachine('{self.configuration_name}')\n\n"""

        for state in self.states:
            tmp_content, tmp_header = state.toPython(app_name, "_" + self.configuration_name, 'states')
            content += tmp_content
            header += tmp_header

        content += f"""{app_name}.externals += [_{self.configuration_name}]\n\n"""

        return content, header

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
