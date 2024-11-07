''' Pythonic representation of the Thread object '''

from martepy.marte2.config_object import MARTe2ConfigObject
from martepy.functions.extra_functions import getname

class NonDuplicatingList(list):
    ''' Ensure our list is non duplicating '''
    def append(self, item):
        ''' Ensure the append is not appending again '''
        if not any(item == list_item for list_item in self):
            super().append(item)

    def __iadd__(self, other):
        for item in other:
            self.append(item)
        return self

class MARTe2RealTimeThread(MARTe2ConfigObject):
    """Object for configuring RealTimeThreads for MARTe2 applications"""

    def __init__(self,
                    configuration_name: str = 'Thread',
                    cpu_mask: int = 0xFFFFFFFF,
                    functions: list = [],
                ):
        super().__init__()
        self.configuration_name = configuration_name
        self.class_name = 'RealTimeThread'
        self.cpu_mask = cpu_mask
        self.functions = functions

    def write(self, config_writer):
        ''' Write our configuration of this class '''
        config_writer.startClass('+' + getname(self), self.class_name)
        if isinstance(self.cpu_mask, str):
            if 'x' in self.cpu_mask:
                # Capitalize the letters only
                capitalized_hex = self.cpu_mask[:2] + self.cpu_mask[2:].upper()
                config_writer.writeNode('CPUs', capitalized_hex)
            else:
                hex_value = hex(int(self.cpu_mask))
                # Capitalize the letters only
                capitalized_hex = hex_value[:2] + hex_value[2:].upper()
                config_writer.writeNode('CPUs', capitalized_hex)
        else:
            hex_value = hex(self.cpu_mask)
            # Capitalize the letters only
            capitalized_hex = hex_value[:2] + hex_value[2:].upper()
            config_writer.writeNode('CPUs', capitalized_hex)
        function_names = NonDuplicatingList()
        [function_names.append(getname(i)) for i in self.functions] # pylint: disable=W0106
        config_writer.writeMARTe2Vector('Functions', function_names, formatAsFloat = False)
        config_writer.endSection('+' + getname(self))

    def serialize(self):
        ''' Serialize our object '''
        res = super().serialize()
        res['class_name'] = self.class_name
        res['cpu_mask'] = self.cpu_mask
        if len(self.functions) > 0:
            res['functions'] = [a.serialize() for a in self.functions]
        else:
            res['functions'] = []
        return res

    def __eq__(self, other):
        attributes = ['configuration_name', 'class_name', 'cpu_mask']
        if isinstance(other, self.__class__):
            for attribute in attributes:
                if not getattr(self, attribute) == getattr(other, attribute):
                    return False
            for function, ofunction in zip(self.functions, other.functions):
                if not function == ofunction:
                    return False
            return True
        return False

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True, # pylint: disable=W0221
                    factory=None) -> bool:
        ''' Deserialize our data into an instance of our class '''

        def createObj(a):
            return factory.create(a['class_name'])().deserialize(a)

        super().deserialize(data, hashmap, restore_id, factory=factory)
        self.class_name = data["class_name"]
        self.cpu_mask = data["cpu_mask"]
        self.functions = [createObj(a) for a in data["functions"]]
        return self

def initialize(factory, plugin_datastore) -> None:
    ''' Register us with the factory '''
    factory.registerBlock("RealTimeThread", MARTe2RealTimeThread, plugin_datastore)
