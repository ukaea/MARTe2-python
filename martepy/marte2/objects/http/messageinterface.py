''' Pythonic representation of the HTTP message interface '''

from martepy.marte2.config_object import MARTe2ConfigObject
from martepy.functions.extra_functions import getname
from martepy.marte2.objects.message import MARTe2Message

class MARTe2HttpMessageInterface(MARTe2ConfigObject):
    ''' Pythonic representation of the HTTP message interface '''
    def __init__(self,
                    configuration_name: str = 'WebRoot',
                    objects: list = [],
                ):
        self.class_name = 'HttpMessageInterface'
        super().__init__()
        self.configuration_name = configuration_name.lstrip('+')
        self.objects = objects

    # pylint: disable=line-too-long
    def toPython(self, app_name, parent_name=None):
        header = "from martepy.marte2.objects.http.messageinterface import MARTe2HttpMessageInterface\n"

        content = f"""\n\n_{self.configuration_name} = MARTe2HttpMessageInterface('{self.configuration_name}')"""

        content += f"# Generate HTTP Message Interface objects for {self.configuration_name}\n"

        for obj in self.objects:
            tmp_content, tmp_header = obj.toPython(app_name, "_" + self.configuration_name)
            content += tmp_content
            header += tmp_header

        if parent_name:
            content += f"""{parent_name}.objects += [_{self.configuration_name}]\n\n"""
        else:
            content += f"""{app_name}.externals += [_{self.configuration_name}]\n\n"""

        return content, header

    def write(self, config_writer):
        ''' Write the configuration of our object '''
        config_writer.startClass('+' + getname(self), self.class_name)
        for obj in self.objects:
            obj.write(config_writer)
        config_writer.endSection('+' + getname(self))

    def serialize(self):
        ''' Serialize the object '''
        res = super().serialize()
        res['class_name'] = self.class_name
        res["objects"] = [a.serialize() for a in self.objects]
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True, # pylint: disable=W0221
                    factory=None) -> bool:
        ''' Deserialize the given data to our class instance '''
        super().deserialize(data, hashmap, restore_id, factory=factory)
        self.class_name = data["class_name"]
        self.objects = [MARTe2Message().deserialize(a) for a in data["objects"]]
        return self

def initialize(factory, plugin_datastore) -> None:
    ''' Register the object with the factory '''
    factory.registerBlock("HttpMessageInterface", MARTe2HttpMessageInterface, plugin_datastore)
