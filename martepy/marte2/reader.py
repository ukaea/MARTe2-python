"""This is the reader capable of reading a MARTe2 cfg file and translating this into
the MARTe2 Pythonic class representations
"""
import copy
import os

from martepy.marte2.generic_application import GAMDataSource, MARTe2Application
from martepy.marte2.objects import (MARTe2Message,
                                    MARTe2ReferenceContainer,
                                    MARTe2StateMachine,
                                    MARTe2StateMachineEvent)
from martepy.marte2.objects.http.directoryresource import MARTe2HttpDirectoryResource
from martepy.marte2.objects.http.messageinterface import MARTe2HttpMessageInterface
from martepy.marte2.objects.http.service import MARTe2HttpService
from martepy.marte2.objects.real_time_state import MARTe2RealTimeState
from martepy.marte2.objects.real_time_thread import MARTe2RealTimeThread
from martepy.marte2.objects.gam_scheduler import MARTe2GAMScheduler
from martepy.marte2.factory import Factory as mpyFactory
from martepy.marte2.objects.http.objectbrowser import MARTe2HTTPObjectBrowser
from martepy.marte2.objects.configuration_database import MARTe2ConfigurationDatabase
from martepy.marte2.qt_functions import genNextStateMsgs
from martepy.functions.extra_functions import getname

class TreeNode:
    ''' Node which represents an item in the configuration for navigating the tree '''
    def __init__(self, name, parent = None):
        self.name = name
        self.parameters = {}
        self.children = []
        self.parent = parent

    def addParameter(self, key, value):
        ''' Add a parameter to the config item '''
        self.parameters[key] = value

    def addChild(self, child):
        ''' Add a child to the config tree item '''
        self.children.append(child)

    def __str__(self, level=0):
        ''' Display the item details as a string as it would in the cfg '''
        result = "\t" * level + f"{self.name}\n"
        for key, value in self.parameters.items():
            result += "\t" * (level + 1) + f"{key} = {value}\n"
        for child in self.children:
            result += child.__str__(level + 1)
        return result


def parseFile(file_path):
    ''' Parse a cfg file given a path - wrapper around the parse text function '''
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content


def buildTree(content):
    ''' Read a text content and parse it into TreeNode classes for later interpretation '''
    root = TreeNode('root')
    current_node = root
    lines = content.split('\n')
    building = False
    multiline_expr = False
    current_line = ''
    key = ''
    for line in lines:
        stripped_line = line.lstrip(' ')
        if building:
            current_line += stripped_line
            if not stripped_line.strip().endswith('\\n'):
                building = False
                current_node.addParameter(key, current_line.replace('\\n','\n'))
            continue
        if multiline_expr:
            current_line += stripped_line + '\n'
            if stripped_line == '\"' or (stripped_line.endswith('\"')):
                multiline_expr = False
                current_node.addParameter(key, current_line.rstrip('\n'))
            continue
        if stripped_line.strip().endswith('{'):
            # Start of a new TreeNode
            name = stripped_line.split('=')[0].strip()
            new_node = TreeNode(name, current_node)
            current_node.addChild(new_node)
            current_node = new_node
        elif stripped_line.strip().endswith("}"):
            if '=' in stripped_line and '+' not in stripped_line:
                key, value = stripped_line.split("=")
                key = key.strip()
                value = value.strip()
                current_node.addParameter(key, value)
                continue
            current_node = current_node.parent
        elif "=" in stripped_line:
            key, value = stripped_line.split("=")
            key = key.strip()
            value = value.strip()
            if stripped_line.strip(' ').endswith('\\n'):
                building = True
                current_line = value
            elif value == '\"' or (value.startswith('\"') and not value.endswith('\"')):
                multiline_expr = True
                current_line = value
            else:
                current_node.addParameter(key, value)

    return root


def formatToSignal(tree_definition):
    '''Need to change to the signal format:
    signals = [('AnalogueIn',{'MARTeConfig':{
            'Alias': 'n/c',
            'DataSource': self.datasource,
            'Type': 'float64',
            'NumberOfElements': 1
        }})]
    '''
    if tree_definition:
        signals = []
        for child in tree_definition.children:
            # Now for the special case of SimulinkWrapper - or possible more
            # Where we have embedded signals in another layer, we want to account for these
            if child.children:
                bus_name = child.name
                for sub_child in child.children:
                    current_signal = grabParameters(sub_child)
                    current_signal[1]['MARTeConfig']['Bus'] = bus_name
                    signals.append(current_signal)
            else:
                signals.append(grabParameters(child))
        return signals
    return []

def grabParameters(child):
    ''' Split up so we can recurse on multiple levels - 
    this assumes it has the signal child and there are no further levels,
    it gathers the parameters and builds the signal definitin '''
    name = child.name
    parameters = {}
    for param in list(child.parameters):
        key = param
        value = child.parameters[key]
        parameters[key] = value.replace('"','')
    return (name, {'MARTeConfig':parameters})


def getSignals(function_def, formatter):
    ''' Given a cfg definition of a signal - return this into the signal format
    we universally use '''
    return formatToSignal(next((a for a in function_def.children if a.name == formatter), None))

def readApplication(file_path):
    ''' Read an application given a file path - wrapper around the parse file function '''
    file_content = parseFile(file_path)
    return readApplicationText(file_content)

class UnrecognisedParameterException(Exception):
    ''' Exception that should be thrown when an unknown parameter in a tree occurs '''
    def __init__(self, class_name, key):
        self.msg = f'Unrecognised parameter caught for class {class_name} and parameter {key}'

def getParameters(child):
    ''' Return the parameters of an object '''
    return {key:value for key, value in child.parameters.items() if key != 'Class'}

def setParameters(child, child_obj, class_name):
    ''' Set an objects parameters '''
    for key, value in getParameters(child).items():
        if hasattr(child_obj, key.lower()):
            setattr(child_obj, key.lower(), value.replace('"','').replace("'",''))
        else:
            raise UnrecognisedParameterException(class_name,key)

def handleChildObjects(parent_obj, function, factory):
    ''' Handle when a function contains objects of it's own - so far only needed 
    for the MessageGAM that we know of but could be applicable to other GAMs. '''
    if function.children:
        # So far we've only seen this with MessageGAM but it gives the concept that
        # there may be objects within a function
        for child in function.children:
            if child.name in ('InputSignals', 'OutputSignals'):
                continue
            # Something unknown, we should check that our gam has a read_gam_config function
            # It should have a class attribute, so we can use that to decipher what that class is
            # It's name should also correspond to its attribute name in the GAM in lower case so
            # we know where to put it. This should be true recursively down.
            # But, if the class does not have attr, we will dump this into the objects attribute -
            # assuming it goes there.
            if child.name[0] == '+':
                # Is a new object class to build
                class_name = child.parameters['Class']
                child_cls = factory.create(class_name)
                child_obj = child_cls(configuration_name=child.name)
                if hasattr(child_obj, 'objects'):
                    child_obj.objects = []
                if class_name == 'ConfigurationDatabase':
                    # We make an exception for the configuration database - may regret later.
                    child_obj.objects = getParameters(child)
                else:
                    setParameters(child, child_obj, class_name)
                handleChildObjects(child_obj, child, factory)
                if hasattr(parent_obj, child.name.strip('+').lower()):
                    setattr(parent_obj, child.name.strip('+').lower(), child_obj)
                else:
                    parent_obj.objects += [child_obj]
            elif hasattr(parent_obj, child.name.strip('+').lower()):
                setattr(parent_obj, child.name.strip('+').lower(), child.parameters)
            else:
                parent_obj.objects += [child_obj]

def getRootClass(tree_root, class_name):
    ''' Iterator that returns the first node in a given tree with a matching class '''
    for result in tree_root.children:
        if hasattr(result, 'parameters'):
            # Written this way to make more readable - initially was a one line list comprehension
            if any(param == 'Class' for param in list(result.parameters)):
                if result.parameters['Class'] == class_name:
                    return result
    # Nothing was found, return None like you would with next(({condition}), None)
    return None

mfactory = mpyFactory()
main_dir = os.path.abspath(os.path.dirname(__file__))
mfactory.loadRemote(os.path.join(main_dir,"objects","objects.json"))
mfactory.loadRemote(os.path.join(main_dir,"gams","gams.json"))
mfactory.loadRemote(os.path.join(main_dir,"datasources","datasources.json"))
mfactory.loadRemote(os.path.join(os.path.dirname(main_dir),"frameworks","end.json"))

def getSimulinkParameters(function):
    ''' Specifically for the SimulinkWrapperGAM, gets the parameters section '''
    output_list = []

    for key, value in function.parameters.items():
        # Extract the type inside parentheses
        type_start = value.find('(') + 1
        type_end = value.find(')')
        param_type = value[type_start:type_end].strip()

        # Extract everything after the closing parenthesis
        presets = value[type_end + 1:].strip()

        output_list.append({
            'parameter_name': key,
            'type': param_type,
            'presets': presets
        })

    return output_list

def toFunctionObj(function):
    ''' Convert object to it's function class '''
    class_name = function.parameters['Class']
    block_cls = mfactory.create(class_name)
    input_signals = getSignals(function, "InputSignals")
    output_signals = getSignals(function, "OutputSignals")
    # Handle Parameters object for Simulink Wrapper GAM
    matching_obj = next((obj for obj in function.children if obj.name == 'Parameters'), None)
    parameters = []
    if matching_obj:
        parameters = getSimulinkParameters(matching_obj)
    configuration_name = function.name.strip('+')
    blk = block_cls(configuration_name=configuration_name, input_signals=input_signals,
                    output_signals=output_signals)
    for parameter_name, parameter_value in function.parameters.items():
        if parameter_name == 'Class':
            continue
        setattr(blk, parameter_name.lower(), parameter_value.replace('"',''))
    if not parameters:
        handleChildObjects(blk, function, mfactory)
    if parameters:
        blk.parameters = parameters
    return configuration_name, blk

def toDataSourceObj(datasource):
    ''' Convert object to it's datasource class '''
    configuration_name = datasource.name.lstrip('+')
    class_name = datasource.parameters['Class']
    signals = getSignals(datasource, "Signals")
    try:
        blk_cls = mfactory.create(class_name)
    except ValueError:
        blk_cls = mfactory.create(configuration_name)
    try:
        blk = blk_cls(configuration_name=configuration_name, output_signals=signals)
    except TypeError:
        blk = blk_cls(configuration_name=configuration_name, input_signals=signals)
    # Catch any leftover parameters
    param_cpy = copy.deepcopy(datasource.parameters)
    del param_cpy['Class']
    for param in list(param_cpy):
        value = param_cpy[param].strip('"').strip("'")
        setattr(blk, param.lower(), value)
    return blk

def returnFromChildren(children, name):
    ''' Given a tree nodes children, return the named node or None '''
    for child in children:
        if child.name == name:
            return child
    return None

def readApplicationText(file_content):
    ''' Given text content, read this in and interpret it into the MARTe2
    Pythonic class representations '''
    app = MARTe2Application()
    tree_root = buildTree(file_content)
    # The first set of objects should be anything root level and our application.
    # First let's find our application, we can worry about
    # root level objects later when we incorporate those
    application_definition = getRootClass(tree_root, 'RealTimeApplication')
    app.app_name = application_definition.name.lstrip('$')

    # Okay now we have this, there will be four child sections:
    # - Functions
    # - Data (DataSources)
    # - States
    # - Scheduler
    function_map = {}
    # Now iterate our functions and interpret them based on our factory knowledge of them
    for function in returnFromChildren(application_definition.children, '+Functions').children:
        # There will always be a class parameter here
        configuration_name, blk = toFunctionObj(function)
        app.add(functions=[blk])
        function_map[configuration_name.strip('+')] = blk

    # Handle the datasource section
    datasources = returnFromChildren(application_definition.children, '+Data')

    for datasource in datasources.children:
        blk = toDataSourceObj(datasource)
        app.add(additional_datasources=[blk])

    # Handle if we have a defined default DataSource
    if 'DefaultDataSource' in list(datasources.parameters.keys()):
        app.default_data_source = datasources.parameters['DefaultDataSource']
    else:
        if len([a for a in app.additional_datasources if isinstance(a, GAMDataSource)]) == 0:
            app.default_data_source = 'DDB0'
        else:
            app.default_data_source = [a for a in app.additional_datasources if
                                       isinstance(a, GAMDataSource)][0]

    # Get the states defined in our application
    getStates(application_definition, function_map, app)
    # And now the scheduler finally

    scheduler = next(a for a in application_definition.children if a.name == '+Scheduler')
    app.add(internals=[
        MARTe2GAMScheduler(configuration_name = scheduler.name,
                           timing_datasource_name=scheduler.parameters['TimingDataSource'],
                           class_name=scheduler.parameters['Class'])])

    new_state_machine = defineStateMachine(tree_root, application_definition,
                                           app, getname(app.states[0]))

    app.add(externals=[new_state_machine])

    found_http_browser, found_http_service, http_messages = toHttp(tree_root)
    if found_http_browser:
        app.add(externals=[found_http_browser])
    if found_http_service:
        app.add(externals=[found_http_service])
    return app, new_state_machine, found_http_browser, http_messages

def getStates(application_definition, function_map, app):
    ''' Get an applications states definition '''
    # Now decipher the states
    states = next(a for a in application_definition.children if a.name == '+States')
    for state in states.children:
        config_name = state.name
        threads = MARTe2ReferenceContainer('Threads', objects=[])
        for thread in state.children[0].children:
            thread_name = thread.name
            cpus = thread.parameters['CPUs'] if 'CPUs' in list(thread.parameters.keys()) else 0x1
            if 'x' in cpus:
                cpus = int(float.fromhex(cpus))
            else:
                cpus = int(cpus)
                functions = '{ }'
            if 'Functions' in list(thread.parameters.keys()):
                functions = thread.parameters['Functions']
            functions = functions.strip('{').strip('}').split(' ')
            functions = [function_map[function] for function in functions if function != '']
            # Find the actual function we evaluated with this name
            new_thread = MARTe2RealTimeThread(configuration_name = thread_name,
                                              cpu_mask = cpus, functions = functions)
            threads.objects.append(new_thread)
        new_state = MARTe2RealTimeState(configuration_name = config_name, threads = threads)
        app.add(states = [new_state])

    # Ensure we have an error state with a thread definition
    error_state = next((a for a in app.states if a.configuration_name == '+Error'), None)
    if error_state:
        if not error_state.threads.objects:
            new_thread = MARTe2RealTimeThread(configuration_name = '+Thread1',
                                              cpu_mask = 4294967295, functions = [])
            error_state.threads.objects = [new_thread]
    else:
        threads = MARTe2ReferenceContainer('Threads', objects=[])
        threads.objects = [MARTe2RealTimeThread(configuration_name = '+Thread1',
                                          cpu_mask = 4294967295, functions = [])]
        new_state = MARTe2RealTimeState(configuration_name = '+Error', threads = threads)
        app.add(states = [new_state])

def defineStateMachine(tree_root, application_definition, app, first_state): # pylint:disable=R0914
    ''' Find our state machine, if not found, create one'''
    state_machine = getRootClass(tree_root, 'StateMachine')
    if state_machine is None:
        return createBasicStateMachine(application_definition, app, first_state)
    new_state_machine = MARTe2StateMachine(state_machine.name, [])
    for states in state_machine.children:
        new_state = MARTe2ReferenceContainer(states.name, [])
        for event in states.children:
            if event.parameters['Class'] == 'StateMachineEvent':
                timeout = -1
                try:
                    # Won't necessarily be defined for Error Events
                    timeout = event.parameters['Timeout'].strip('"')
                except KeyError:
                    pass
                new_event = MARTe2StateMachineEvent(event.name, event.parameters['NextState'],
                                                    event.parameters['NextStateError'],
                                                    timeout, [])
            else:
                new_event = MARTe2ReferenceContainer('+ENTER', [])
            for message in event.children:
                maxwait = -1
                try:
                    maxwait = message.parameters['MaxWait'].strip('"')
                except KeyError:
                    pass
                new_message = MARTe2Message(message.name,
                                            message.parameters['Destination'].strip('"'),
                                            message.parameters['Function'].strip('"'),
                                            MARTe2ConfigurationDatabase(objects={}),
                                            message.parameters['Mode'],
                                            maxwait)
                if message.children:
                    parameter = message.children[0]
                    objects = {key:value for key, value in
                                parameter.parameters.items() if key != 'Class'}
                    new_message.parameters = MARTe2ConfigurationDatabase(parameter.name,
                                                                            objects=objects)
                if event.parameters['Class'] == 'StateMachineEvent':
                    new_event.messages += [new_message]
                else:
                    new_event.objects += [new_message]
            new_state.objects += [new_event]
        new_state_machine.states += [new_state]
    return new_state_machine

def createBasicStateMachine(application_definition, app, first_state):
    ''' creates a very basic state machine object '''
    # Create a state machine basic version based on the number of states
    states = []
    # First you want an entry point which just starts the application
    app_name = application_definition.name
    msgs = genNextStateMsgs(first_state.replace('+',''), app_name)
    msgs.pop(0)
    initial_event = MARTe2StateMachineEvent('+START',
                                            first_state.upper().replace('+',''),
                                            'ERROR', 0, msgs)
    states += [MARTe2ReferenceContainer("+INITIAL", [initial_event])]
    msgs = genNextStateMsgs('Error', app_name)
    state1 = MARTe2StateMachineEvent('+ERROR', 'ERROR', 'ERROR', 0, [])
    states += [MARTe2ReferenceContainer("+STATE1", [state1])]

    # The error state is special, it needs the enter and reset state,
    # the enter state must exist!
    msgs = genNextStateMsgs('Error', app_name)
    error_enter = MARTe2ReferenceContainer('+ENTER', msgs)
    msgs = genNextStateMsgs(first_state, app_name)
    error_reset = MARTe2StateMachineEvent('+RESET', first_state.upper().replace('+',''),
                                            first_state.upper().replace('+',''), 0, msgs)
    states += [MARTe2ReferenceContainer("+ERROR", [error_enter, error_reset])]

    # Check that an error state exists, if not, create one for the application
    if not any(getname(state).upper() == "ERROR" for state in app.states):
        threads = MARTe2ReferenceContainer('Threads', objects=[])
        threads.objects = [MARTe2RealTimeThread(configuration_name = '+Thread1',
                                          cpu_mask = 4294967295, functions = [])]
        new_state = MARTe2RealTimeState(configuration_name = '+Error', threads = threads)
        app.add(states=[new_state])

    new_state_machine = MARTe2StateMachine('+StateMachine', states)
    return new_state_machine

def createHttpBrowser(http_browser, http_messages):
    ''' From our given found browser, create it's object '''
    if http_browser is None:
        return None
    parent_browser = MARTe2HTTPObjectBrowser(http_browser.name,
                                                http_browser.parameters['Root'],
                                                objects=[])
    object_browser = getRootClass(http_browser, 'HttpObjectBrowser')
    if object_browser:
        attributes = [object_browser.name, object_browser.parameters['Root']]
        parent_browser.objects += [MARTe2HTTPObjectBrowser(*attributes,
                                                            objects=[])]
        # This is the initial child version,
        # we're going to build the children objects first
    resources_html = getRootClass(http_browser, 'HttpDirectoryResource')
    if resources_html:
        attributes = [resources_html.name, resources_html.parameters['BaseDir']]
        parent_browser.objects += [MARTe2HttpDirectoryResource(*attributes)]
    message_interface = getRootClass(http_browser, 'HttpMessageInterface')
    if message_interface:
        if message_interface.children:
            # Has messages defined
            for message in message_interface.children:
                maxwait = int(message.parameters['MaxWait'].strip('"'))
                new_message = MARTe2Message(message.name,
                                            message.parameters['Destination'].strip('"'),
                                            message.parameters['Function'].strip('"'),
                                            MARTe2ConfigurationDatabase(objects={}),
                                            message.parameters['Mode'].strip('"'),
                                            maxwait)
                if message.children:
                    # Has a parameter set defined
                    parameter = message.children[0]
                    objects = {key:value for key, value in
                                parameter.parameters.items() if key != 'Class'}
                    new_message.parameters = MARTe2ConfigurationDatabase(parameter.name,
                                                                            objects=objects)
                http_messages.append(new_message)
        parent_browser.objects += [MARTe2HttpMessageInterface(resources_html.name,
                                                                http_messages)]
    return parent_browser

def toHttp(tree_root):
    ''' Find in our application the HTTP objects'''
    found_http_browser = None
    found_http_service = None
    http_messages = []
    try:
        http_browser = getRootClass(tree_root, 'HttpObjectBrowser')
        http_service = getRootClass(tree_root, 'HttpService')
        # First interpret the WebRoot
        if http_browser:
            found_http_browser = createHttpBrowser(http_browser, http_messages)
        # Now interpret the WebService
        if http_service:
            attributes = [http_service.name,
                          http_service.parameters['Port'],
                          http_service.parameters['WebRoot'],
                          http_service.parameters['Timeout'],
                          http_service.parameters['ListenMaxConnections'],
                          http_service.parameters['AcceptTimeout'],
                          http_service.parameters['MaxNumberOfThreads'],
                          http_service.parameters['MinNumberOfThreads']]
            found_http_service = MARTe2HttpService(*attributes)
    except AttributeError:
        http_browser = None # Will handle later on in the call stack upwards
        http_service = None
    return found_http_browser, found_http_service, http_messages

if __name__ == "__main__":
    CFG_PATH = "Simulation.cfg"
    main_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    test_file = os.path.join(main_dir, 'tests','frameworks',
                             'simulation_framework','multistatethread_complextype.cfg')
    appcfg = readApplication(test_file)[0]
    with open('Out.cfg','w', encoding='utf-8') as outfile:
        outfile.write(appcfg.writeToConfig())
