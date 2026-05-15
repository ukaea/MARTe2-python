''' Pythonic representation of Message '''

from martepy.marte2.config_object import MARTe2ConfigObject
from martepy.marte2.objects.configuration_database import MARTe2ConfigurationDatabase

class MARTe2Message(MARTe2ConfigObject):
    ''' Pythonic representation of Message '''
    def __init__(self,
                    configuration_name: str = 'Message',
                    destination: str = "App",
                    function: str = "StopCurrentStateExecution",
                    parameters: MARTe2ConfigurationDatabase = MARTe2ConfigurationDatabase(),
                    mode: str = "ExpectsReply",
                    maxwait: int = 0,
                ):
        super().__init__(
            )
        self.class_name = "Message"
        self.configuration_name = configuration_name.lstrip('+')
        self.destination = destination
        self.function = function
        self.parameters = parameters
        self.mode = mode
        self.maxwait = maxwait

    # pylint: disable=line-too-long
    def toPython(self, app_name, parent_name=None, type_name="objects"):
        header = "from martepy.marte2.objects.message import MARTe2Message\n"

        content = f"""\n\n_{self.configuration_name} = MARTe2Message('{self.configuration_name}', '{self.destination}', '{self.function}', '{self.mode}', {self.maxwait})\n\n"""

        content += f"# Generate Message Parameters objects for {self.configuration_name}\n"

        tmp_content, tmp_header = self.parameters.toPython(app_name, "_" + self.configuration_name, 'parameters', False)
        content += tmp_content
        header += tmp_header

        if parent_name:
            content += f"""{parent_name}.{type_name} += [_{self.configuration_name}]\n\n"""
        else:
            content += f"""{app_name}.internals += [_{self.configuration_name}]\n\n"""

        return content, header

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            comparisons = ['configuration_name', 'destination','function',
                           'parameters','mode','maxwait']
            for item in comparisons:
                try:
                    if not getattr(self, item) == getattr(other, item):
                        return False
                except AttributeError:
                    return False
            return True
        return False

    def write(self, config_writer):
        ''' Write our configuration of this class '''
        def sanitize(value):
            return str(value).replace('"','')
        config_writer.startClass('+' + self.configuration_name.lstrip('+'),"Message")
        dest = sanitize(self.destination).replace('$','')
        config_writer.writeNode('Destination', f'"{dest}"')
        config_writer.writeNode('Function', f'"{sanitize(self.function)}"')
        config_writer.writeNode('MaxWait', f'"{sanitize(self.maxwait)}"')
        if self.mode != "":
            config_writer.writeNode('Mode', f'"{sanitize(self.mode)}"')
        if self.parameters:
            if self.parameters.objects:
                self.parameters.write(config_writer)
        config_writer.endSection('+' + self.configuration_name.lstrip('+'))

    def serialize(self):
        ''' Serialize our object '''
        res = super().serialize()
        res['class_name'] = self.class_name
        res['destination'] = self.destination
        res['maxwait'] = self.maxwait
        res['function'] = self.function
        res['parameters'] = self.parameters.serialize()
        res['mode'] = self.mode
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True, # pylint: disable=W0221
                    factory=None) -> bool:
        ''' Deserialize our data into an instance of our class '''
        super().deserialize(data, hashmap, restore_id, factory=factory)
        self.class_name = data["class_name"]
        self.destination = data["destination"]
        self.function = data["function"]
        self.maxwait = data['maxwait']

        self.parameters = MARTe2ConfigurationDatabase().deserialize(data["parameters"],
                                                                    factory=factory)
        self.mode = data["mode"]
        return self

def initialize(factory, plugin_datastore) -> None:
    ''' Register us with the factory '''
    factory.registerBlock("Message", MARTe2Message, plugin_datastore)
