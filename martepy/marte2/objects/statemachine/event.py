''' Pythonic representation of the State Machine Event Object '''

from martepy.marte2.config_object import MARTe2ConfigObject
from martepy.marte2.objects.message import MARTe2Message
from martepy.functions.extra_functions import getname

class MARTe2StateMachineEvent(MARTe2ConfigObject):
    ''' Pythonic representation of the State Machine Event Object '''
    def __init__(self,
                    configuration_name: str = 'GOTOSTATE1',
                    nextstate = "",
                    nextstateerror = "",
                    timeout = 0,
                    messages = [],
                ):
        super().__init__(
            )
        self.class_name = "StateMachineEvent"
        self.configuration_name = configuration_name.upper()
        self.nextstate = nextstate.upper()
        self.nextstateerror = nextstateerror.upper()
        self.timeout = timeout
        self.messages = messages

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            attributes = ['configuration_name', 'nextstate',
                          'nextstateerror', 'timeout', 'messages']
            for item in attributes:
                if not getattr(self, item) == getattr(other, item):
                    return False
            return True
        return False

    def write(self, config_writer):
        ''' Write the configuration of our object '''
        def sanitize(value):
            return value.replace('"','')

        config_writer.startClass('+' + getname(self),"StateMachineEvent")
        config_writer.writeNode('NextState', f'"{sanitize(self.nextstate)}"')
        if self.nextstateerror != "":
            config_writer.writeNode('NextStateError', f'"{sanitize(self.nextstateerror)}"')
        config_writer.writeNode('Timeout', f'{self.timeout}')
        for message in self.messages:
            message.write(config_writer)
        config_writer.endSection('+' + getname(self))

    def serialize(self):
        ''' Serialize the object '''
        res = super().serialize()
        res['class_name'] = self.class_name
        res['nextstate'] = self.nextstate
        res['nextstateerror'] = self.nextstateerror
        res['timeout'] = self.timeout
        res["messages"] = [a.serialize() for a in self.messages]
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True, # pylint: disable=W0221
                    factory=None) -> bool:
        ''' Deserialize the given data to our class instance '''
        super().deserialize(data, hashmap, restore_id, factory=factory)
        self.class_name = data['class_name']
        self.nextstate = data['nextstate']
        self.nextstateerror = data['nextstateerror']
        self.timeout = data['timeout']
        self.messages = [MARTe2Message().deserialize(a,factory=factory) for a in data['messages']]
        return self

def initialize(factory, plugin_datastore) -> None:
    ''' Register the object with the factory '''
    factory.registerBlock("StateMachineEvent", MARTe2StateMachineEvent, plugin_datastore)
