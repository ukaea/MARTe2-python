''' Pythonic representation of the Event Condition Trigger Object '''

from martepy.marte2.config_object import MARTe2ConfigObject
from martepy.functions.extra_functions import getname

class MARTe2EventConditionTrigger(MARTe2ConfigObject):
    ''' Pythonic representation of the Event Condition Trigger Object '''
    def __init__(self,
                    configuration_name: str = '+NewEvent',
                    class_name = "EventConditionTrigger",
                    eventtriggers = {},
                    msgs = [],
                ):
        super().__init__()
        self.class_name = class_name
        self.eventtriggers = eventtriggers
        self.configuration_name = configuration_name
        self.objects = msgs

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            attributes = ['configuration_name', 'eventtriggers', 'objects']
            for item in attributes:
                if not getattr(self, item) == getattr(other, item):
                    return False
            return True
        return False

    def write(self, config_writer):
        ''' Write the configuration of our object '''
        config_writer.startClass('+' + getname(self), self.class_name)
        config_writer.startSection('EventTriggers')
        for key, value in self.eventtriggers.items():
            config_writer.writeNode(key, str(value))
        config_writer.endSection('EventTriggers')
        for obj in self.objects:
            obj.write(config_writer)
        config_writer.endSection('+' + getname(self))

    def serialize(self):
        ''' Serialize the object '''
        res = super().serialize()
        res['class_name'] = "EventConditionTrigger"
        res['eventtriggers'] = self.eventtriggers
        res["objects"] = [a.serialize() for a in self.objects]
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True, # pylint: disable=W0221
                    factory=None) -> bool:
        ''' Deserialize the given data to our class instance '''
        def createObj(a):
            return factory.create(a['class_name'])().deserialize(a, factory=factory)
        super().deserialize(data, hashmap, restore_id, factory=factory)
        self.class_name = "EventConditionTrigger"
        self.eventtriggers = dict(data['eventtriggers'])
        # This part is tricky as a ref container can
        # contain any object so the factory needs to recircle here
        self.objects = [createObj(a) for a in data["objects"]]
        return self

def initialize(factory, plugin_datastore) -> None:
    ''' Register the object with the factory '''
    factory.registerBlock("EventConditionTrigger", MARTe2EventConditionTrigger, plugin_datastore)
