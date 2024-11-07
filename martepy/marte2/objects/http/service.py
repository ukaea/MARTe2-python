''' Pythonic representation of the HTTP Service object '''

from martepy.marte2.config_object import MARTe2ConfigObject
from martepy.functions.extra_functions import getname

class MARTe2HttpService(MARTe2ConfigObject):
    ''' Pythonic representation of the HTTP Service object '''
    def __init__(self,
                    configuration_name: str = 'WebRoot',
                    port = 8084,
                    webroot = "WebRoot",
                    timeout = 0,
                    listenmaxconnections = 255,
                    accepttimeout = 1000,
                    maxnumberofthreads = 8,
                    minnumberofthreads = 1,
                ):
        self.class_name = 'HttpService'
        super().__init__()
        self.configuration_name = configuration_name
        self.port = port
        self.webroot = webroot
        self.timeout = timeout
        self.listenmaxconnections = listenmaxconnections
        self.accepttimeout = accepttimeout
        self.maxnumberofthreads = maxnumberofthreads
        self.minnumberofthreads = minnumberofthreads

    def write(self, config_writer):
        ''' Write the configuration of our object '''
        config_writer.startClass('+' + getname(self), self.class_name)
        config_writer.writeNode('Port', f'"{self.port}"')
        config_writer.writeNode('WebRoot', f'"{self.webroot}"')
        config_writer.writeNode('Timeout', f'"{self.timeout}"')
        config_writer.writeNode('ListenMaxConnections', f'"{self.listenmaxconnections}"')
        config_writer.writeNode('AcceptTimeout', f'"{self.accepttimeout}"')
        config_writer.writeNode('MaxNumberOfThreads', f'"{self.maxnumberofthreads}"')
        config_writer.writeNode('MinNumberOfThreads', f'"{self.minnumberofthreads}"')
        config_writer.endSection('+' + getname(self))

    def serialize(self):
        ''' Serialize the object '''
        res = super().serialize()
        res['class_name'] = self.class_name
        res['port'] = self.port
        res['webroot'] = self.webroot
        res['timeout'] = self.timeout
        res['listenmaxconnections'] = self.listenmaxconnections
        res['accepttimeout'] = self.accepttimeout
        res['maxnumberofthreads'] = self.maxnumberofthreads
        res['minnumberofthreads'] = self.minnumberofthreads
        return res

    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True, # pylint: disable=W0221
                    factory=None) -> bool:
        ''' Deserialize the given data to our class instance '''
        super().deserialize(data, hashmap, restore_id, factory)
        self.class_name = data["class_name"]
        self.port = data["port"]
        self.webroot = data["webroot"]
        self.timeout = data["timeout"]
        self.listenmaxconnections = data["listenmaxconnections"]
        self.accepttimeout = data["accepttimeout"]
        self.maxnumberofthreads = data["maxnumberofthreads"]
        self.minnumberofthreads = data["minnumberofthreads"]
        return self

def initialize(factory, plugin_datastore) -> None:
    ''' Register the object with the factory '''
    factory.registerBlock("HttpService", MARTe2HttpService, plugin_datastore)
