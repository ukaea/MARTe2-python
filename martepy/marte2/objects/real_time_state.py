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
        self.configuration_name = configuration_name.lstrip('+')
        self.class_name = 'RealTimeState'
        self.threads = threads

    # pylint: disable=line-too-long
    def toPython(self, app_name, parent_name=None):
        header = "from martepy.marte2.objects.real_time_state import MARTe2RealTimeState\n"

        content = f"""_{self.configuration_name} = MARTe2RealTimeState('{self.configuration_name}')\n\n"""

        tmp_content, tmp_header = self.threads.toPython(app_name, "_" + self.configuration_name, 'threads')
        content += tmp_content
        header += tmp_header

        if parent_name:
            content += f"""{parent_name}.objects += [_{self.configuration_name}]\n\n"""
        else:
            content += f"""{app_name}.states += [_{self.configuration_name}]\n\n"""

        return content, header

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
