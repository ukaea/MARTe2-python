
import os

from martepy.marte2 import (
    MARTe2Application,
    MARTe2RealTimeThread,
    MARTe2RealTimeState,
    MARTe2GAMScheduler,
    MARTe2Message,
    MARTe2HTTPObjectBrowser,
    MARTe2HttpDirectoryResource,
    MARTe2HttpMessageInterface,
    MARTe2HttpService,
    MARTe2ConfigurationDatabase,
    MARTe2StateMachineEvent,
    MARTe2ReferenceContainer,
    MARTe2StateMachine
)

from martepy.marte2.gams import (
    IOGAM
)

from martepy.marte2.datasources import (
    LinuxTimer,
    LoggerDataSource,
    TimingDataSource
)

CPU_OFFSET_FROM_ONE = 0  # 0 to start at cpu 1
def cpu_thread_gen(x):
    ''' Generate a cpu core to used based on thread number x and pre-defined offset from core 1. '''
    return str(hex(2 ** (x + CPU_OFFSET_FROM_ONE)))

app = MARTe2Application()

app.add(additional_datasources = [
    TimingDataSource(configuration_name = '+Timings'),
])

app.add(additional_datasources = [
    LinuxTimer(
        configuration_name = '+Timer',
        cpu_mask = int(cpu_thread_gen(1), 16),
        sleep_nature = 'Busy',
        execution_mode = 'RealTimeThread',
        output_signals = [
            ('Counter', {'MARTeConfig':{'Type':'uint32' }}),
            ('Time',    {'MARTeConfig':{'Type':'uint32' }}),
        ],
    )
])

app.add(additional_datasources = [
    LoggerDataSource(configuration_name = '+LoggerDataSource'),
])

functions = []

functions += [IOGAM(
    configuration_name = '+GAMDisplay',
    input_signals = [
        ('Time', {'MARTeConfig': {'DataSource': 'Timer', 'Type': 'uint32', 'Frequency': str(500)}}),
    ],
    output_signals = [
        ('DTime', {'MARTeConfig': {'DataSource': 'LoggerDataSource', 'Alias': 'DTime', 'Type': 'uint32'}}),
    ],
)]

app.add(functions = functions)

app.add(states = [
    MARTe2RealTimeState(
        configuration_name = '+Running',
        threads = [
            MARTe2RealTimeThread(
                configuration_name = '+Thread0',
                cpu_mask = int(cpu_thread_gen(1), 16),
                functions = functions,
            ),
        ],
    ),
])

app.add(internals = [
    MARTe2GAMScheduler(
        configuration_name = '+Scheduler',
        timing_datasource_name = 'Timings',
        class_name = 'GAMScheduler',
    ),
])


''' Fixed definition of HTTP Service however because the martepy repo has a dynamic definition this is possible to make dynamic also '''

marte2_dir = os.path.join(os.path.dirname(__file__), "state_machine_http_example.cfg")

''' First thing to do is define the messages we might send to the StateMachine '''
Messages = [MARTe2Message("+GOTOERROR","StateMachine","GOTOERROR"),MARTe2Message("+RESET","StateMachine","RESET")]

''' Object Browser Definition '''
ObjectBrowser = MARTe2HTTPObjectBrowser('+ObjectBrowse','/')

''' ResourcesHtml Definition '''
ResourcesHtml = MARTe2HttpDirectoryResource('+ResourcesHtml',marte2_dir + '/Resources/HTTP/')

MessageInterface = MARTe2HttpMessageInterface('+HttpMessageInterface',Messages)

Objectlist = [ObjectBrowser,ResourcesHtml,MessageInterface]

HTTPBrowser = MARTe2HTTPObjectBrowser('+WebRoot','.',Objectlist)

''' Add WebServer '''
service = MARTe2HttpService('+WebService')
''' Add this to application '''
app.add(externals=[HTTPBrowser] + [service])

''' Our States are ReferenceContainers which contain the state events, possibly also a ENTER state. First we should define
Our Initialising state (as from herein you should run your application via -m StateMachine:START in order to have a functioning state machine) '''

''' Lets start by creating our default states and their corresponding events '''
defaultmessages = [MARTe2Message("+StopCurrentStateExecutionMsg","App",     "StopCurrentStateExecution"),MARTe2Message("+StartNextStateExecutionMsg","App","StartNextStateExecution")]

states = []

# Add Initialising State which we'll use to execute
params = MARTe2ConfigurationDatabase(objects={"param1":"Running"})
prepare = MARTe2Message("+PrepareChangeToRunningMsg", "App", "PrepareNextState", params)

startmessages = [prepare] + [MARTe2Message("+StartNextStateExecutionMsg","App","StartNextStateExecution")]

''' Note the below is necessary for the HTTPService to be running if you are using one. '''

startmessages += [MARTe2Message("+StartHttpService", "WebService", "Start",None,"")]
event = MARTe2StateMachineEvent('+START',"RUNNING","ERROR",0,startmessages)

currentstate = MARTe2ReferenceContainer("+INITIALISING",[event])
states += [currentstate]

# Add our running state
params = MARTe2ConfigurationDatabase(objects={"param1":"ErrorState"})
prepare = MARTe2Message("+PrepareChangeToEndMsg", "App", "PrepareNextState", params)

event = MARTe2StateMachineEvent('+GOTOERROR','ERROR','ERROR',0,([prepare]+defaultmessages))

currentstate = MARTe2ReferenceContainer('+RUNNING',[event])

states += [currentstate]

# Now add Error State
params = MARTe2ConfigurationDatabase(objects={"param1":"ErrorState"})
messages = [MARTe2Message("+StopCurrentStateExecutionMsg","App","StopCurrentStateExecution"),
            MARTe2Message("+PrepareChangeToErrorMsg", "App", "PrepareNextState", params),
            MARTe2Message("+StartNextStateExecutionMsg","App","StartNextStateExecution")]

enter = MARTe2ReferenceContainer("+ENTER",messages)

params = MARTe2ConfigurationDatabase(objects={"param1":"Running"})
resetmessages = [MARTe2Message("+StopCurrentStateExecutionMsg","App","StopCurrentStateExecution"),
            MARTe2Message("+PrepareChangeToPrePulseMsg", "App", "PrepareNextState", params),
            MARTe2Message("+StartNextStateExecutionMsg","App","StartNextStateExecution")]

resetevent = MARTe2StateMachineEvent('+RESET',"Running","ERROR",0,resetmessages)

errorstate = MARTe2ReferenceContainer("+ERROR",([enter] + [resetevent]))

states += [errorstate]

statemachine = MARTe2StateMachine('+StateMachine',states)

app.add(externals=[statemachine])

app.add(states = [
    MARTe2RealTimeState(
        configuration_name = '+ErrorState',
        threads = [],
    ),
])

full_config_string = app.writeToConfig() + '\n'
with open("state_machine_http_example.cfg", "w") as text_file:
    print(full_config_string, file=text_file)
