''' Pythonic representation of configuration database '''

from martepy.marte2.config_object import MARTe2ConfigObject
from martepy.functions.extra_functions import isint, isfloat

class MARTe2ConfigurationDatabase(MARTe2ConfigObject):
    ''' Pythonic representation of configuration database '''
    def __init__(self,
                    configuration_name: str = '+Parameters',
                    class_name = "ConfigurationDatabase",
                    objects = {},
                ):
        super().__init__()
        self.class_name = class_name
        self.objects = objects
        self.configuration_name = configuration_name

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.configuration_name == other.configuration_name:
                if self.objects == other.objects:
                    return True
        return False

    def write(self, config_writer):
        ''' Write the objects we are holding '''
        config_writer.startClass('+' + self.configuration_name.lstrip('+'), self.class_name)
        for key, value in self.objects.items():
            linevalue = ''
            if isint(value) or isfloat(value):
                linevalue = f"{value}"
            else:
                strline = value.replace('"','').replace("'",'')
                linevalue = f'"{strline}"'
            config_writer.writeNode(key,linevalue)
        config_writer.endSection('+' + self.configuration_name.lstrip('+'))

    def serialize(self):
        ''' Serialize our objects '''
        res = super().serialize()
        res['class_name'] = "ConfigurationDatabase"
        res["objects"] = self.objects
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True, # pylint: disable=W0221
                    factory=None) -> bool:
        ''' Deserialize our objects with a factory '''
        super().deserialize(data, hashmap, restore_id, factory=factory)
        self.class_name = "ConfigurationDatabase"
        # This part is tricky as a ref container can
        # contain any object so the factory needs to recircle here
        self.objects = data["objects"]
        for _, value in self.objects.items():
            if not (isint(value) or isfloat(value)):
                value = value.replace('"','').replace("'",'')
        return self

def initialize(factory, plugin_datastore) -> None:
    ''' Register us with the factory '''
    factory.registerBlock("ConfigurationDatabase", MARTe2ConfigurationDatabase, plugin_datastore)
