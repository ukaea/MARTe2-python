from martepy.marte2.objects.message import MARTe2Message
from martepy.marte2.objects.parameters import MARTe2Parameters
from martepy.marte2.objects.referencecontainer import MARTe2ReferenceContainer
from martepy.marte2.objects.statemachine.event import MARTe2StateMachineEvent
from martepy.marte2.objects.statemachine.machine import MARTe2StateMachine

def createStateMachine(app=None, block_running_state_until_pre=False,http=False):
    """Our States are ReferenceContainers which contain the state events, possibly also a ENTER state. First we
    should define our Initialising state (as from herein we're going to run our app via -m StateMachine:START)

    The set of states created is dependent on the value of block_running_state_until_pre passed to the geenrator. If
    it is False, a PrePulse state is created which is the first one entered after Initialising. If it is True, the
    PrePulse state is skipped, and the application goes straight to Running after Initialising.
    """
    # Lets start by creating our default states and their corresponding events
    machinesetup = [{"StateName": "PrePulse", "nextstate": "Running", "errorstate": "ERROR", 'value': 1},
                    {"StateName": "Running", "nextstate": "EndPulse", "errorstate": "ERROR", 'value': 2},
                    {"StateName": "EndPulse", "nextstate": "Error", "errorstate": "ERROR", 'value': 3}]

    if block_running_state_until_pre:
        del machinesetup[0]

    defaultmessages = [MARTe2Message("+StopCurrentStateExecutionMsg", "App", "StopCurrentStateExecution"),
                        MARTe2Message("+StartNextStateExecutionMsg", "App", "StartNextStateExecution")]

    # Add Initialising State which we'll use to execute
    if block_running_state_until_pre:
        next_state_after_init = "Running"
        next_state_value_after_init = '1'
    else:
        next_state_after_init = "PrePulse"
        next_state_value_after_init = '0'

    params = MARTe2Parameters("+Parameters", [{'name': "param1", 'value': next_state_after_init}])
    prepare = MARTe2Message(f"+PrepareChangeTo{next_state_after_init}Msg", "App", "PrepareNextState", [params])
    update_state_value_params = MARTe2Parameters("+Parameters",
                                                    [{'name': 'SignalName', 'value': 'RTCC2State'},
                                                    {'name': 'SignalValue', 'value': next_state_value_after_init}])
    update_state_value_msg = MARTe2Message("+UpdateStateValue", "App.Functions.RTCCState", "SetOutput",
                                            [update_state_value_params])

    startmessages = [prepare] + [MARTe2Message("+StartNextStateExecutionMsg", "App", "StartNextStateExecution")]
    if http:
        startmessages += [MARTe2Message("+StartHttpService", "WebService", "Start", None, "")]
    event = MARTe2StateMachineEvent('+START', next_state_after_init, "ERROR", 0,
                                    ([update_state_value_msg] + startmessages))

    initialising_state = MARTe2ReferenceContainer("+INITIALISING", [event])
    states = [initialising_state]

    for state in machinesetup:
        # Create our PrepareChange message
        params = MARTe2Parameters("+Parameters", [{'name': "param1", 'value': state['nextstate']}])
        prepare = MARTe2Message("+PrepareChangeTo" + state['nextstate'] + "Msg", "App", "PrepareNextState", [params])
        ''' Change state value by constant '''
        update_state_value_params = MARTe2Parameters("+Parameters",
                                                        [{'name': 'SignalName', 'value': 'RTCC2State'},
                                                        {'name': 'SignalValue', 'value': str(state['value'])}])
        update_state_value_msg = MARTe2Message("+UpdateStateValue", "App.Functions.RTCCState", "SetOutput",
                                                [update_state_value_params])

        event = MARTe2StateMachineEvent('+GOTO' + state['nextstate'].upper(),
                                        state['nextstate'], state['errorstate'], 0,
                                        [prepare] + [update_state_value_msg] + defaultmessages)

        # Now create a reference container with our state name
        entry = []
        errevent = []
        if(state['StateName'] == "EndPulse"):
            flush_file = MARTe2Message("+FlushFileIO", "App", "FlushFile")
            entry = [MARTe2ReferenceContainer('+ENTER', [flush_file])]
        else:
            params = MARTe2Parameters("+Parameters", [{'name': 'param1', 'value': 'ErrorState'}])
            prepare = MARTe2Message("+PrepareChangeToErrorMsg", "App", "PrepareNextState", [params])
            errevent += [MARTe2StateMachineEvent('+GOTOERRORSTATE', "ERROR", "ERROR", 0,
                                                    [prepare] + defaultmessages)]

        currentstate = MARTe2ReferenceContainer('+' + state['StateName'].upper(), entry + [event] + errevent)
        states += [currentstate]

    # Now add Error State
    params = MARTe2Parameters("+Parameters", [{'name': "param1", 'value': "ErrorState"}])
    messages = [MARTe2Message("+StopCurrentStateExecutionMsg", "App", "StopCurrentStateExecution"),
                MARTe2Message("+PrepareChangeToErrorMsg", "App", "PrepareNextState", [params]),
                MARTe2Message("+StartNextStateExecutionMsg","App","StartNextStateExecution")]

    # Change state value by constant
    update_state_value_params = MARTe2Parameters("+Parameters",
                                                    [{'name': 'SignalName', 'value': 'RTCC2State'},
                                                    {'name': 'SignalValue', 'value': '3'}])
    update_state_value_msg = MARTe2Message("+UpdateStateValue", "App.Functions.RTCCState", "SetOutput",
                                            [update_state_value_params])

    enter = MARTe2ReferenceContainer("+ENTER", [update_state_value_msg] + messages)

    params = MARTe2Parameters("+Parameters", [{'name': "param1", 'value': next_state_after_init}])
    resetmessages = [MARTe2Message("+StopCurrentStateExecutionMsg", "App", "StopCurrentStateExecution"),
                        MARTe2Message(f"+PrepareChangeTo{next_state_after_init}Msg", "App", "PrepareNextState", [params]),
                        MARTe2Message("+StartNextStateExecutionMsg", "App", "StartNextStateExecution")]

    resetevent = MARTe2StateMachineEvent('+RESET', next_state_after_init, "ERROR", 0, resetmessages)

    errorstate = MARTe2ReferenceContainer("+ERROR", [enter] + [resetevent])
    states += [errorstate]

    statemachine = MARTe2StateMachine('+StateMachine', states)
    app.add(externals=[statemachine])
