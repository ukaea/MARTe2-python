.. MARTe2-python documentation
   Started on Tue Dec 14 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Building complex objects in MARTe2
==================================

This document outlines how to create some of the more complex objects/threads in MARTe2 using the pythonic classes provided.

.. toctree::
   :maxdepth: -1

One of the more complex tasks in the martepy module is to create a HTTP Web Service in your MARTe2 configuration or to use the StateMachine. This is because they have child objects which need definition and instantiation, cascading up through the parents when developing.

HTTPService:
************

If you use the HTTPService you must also implement a StateMachine in order to initialise it at application startup. Thankfully defining the HTTPService is actually fairly simple (compared to the StateMachine). 
The Messages in the service don't need parameters so are simple to construct along with the hierarchy of objects needed to build the root objects. Keep in mind you can't just copy and paste the remaining section of this document. You must build and configure an application with multiple states.'

*Note in this case we have the variable self.marte2_dir which should point to the location of your MARTe2_DIR environment variable. - you could modify this to read the environment variable instead but this assumes you are building your configuration on the execution machine*.

.. code:: python

    # Fixed definition of HTTP Service however because the martepy repo has a dynamic definition this is possible to make dynamic also

    marte2_dir = os.path.join(os.path.dirname(__file__), "state_machine_http_example.cfg")

    # First thing to do is define the messages we might send to the StateMachine
    Messages = [MARTe2Message("+GOTOERROR","StateMachine","GOTOERROR"),MARTe2Message("+RESET","StateMachine","RESET")]

    # Object Browser Definition
    ObjectBrowser = MARTe2HTTPObjectBrowser('+ObjectBrowse','/')

    # ResourcesHtml Definition
    ResourcesHtml = MARTe2HttpDirectoryResource('+ResourcesHtml',marte2_dir + '/Resources/HTTP/')

    MessageInterface = MARTe2HttpMessageInterface('+HttpMessageInterface',Messages)

    Objectlist = [ObjectBrowser,ResourcesHtml,MessageInterface]

    HTTPBrowser = MARTe2HTTPObjectBrowser('+WebRoot','.',Objectlist)

    # Add WebServer
    service = MARTe2HttpService('+WebService')
    # Add this to application
    app.add(externals=[HTTPBrowser] + [service])

StateMachine:
*************

Now imagine the application we built before now has two states and the HTTPService, the second state we'll call State2. So we have two states + the required error state when using a StateMachine:
- Running
- End
- Error

.. code:: python

    # Our States are ReferenceContainers which contain the state events, possibly also a ENTER state. First we should define
    # Our Initialising state (as from herein you should run your application via -m StateMachine:START in order to have a functioning state machine)

    # Lets start by creating our default states and their corresponding events
    defaultmessages = [MARTe2Message("+StopCurrentStateExecutionMsg","App",     "StopCurrentStateExecution"),MARTe2Message("+StartNextStateExecutionMsg","App","StartNextStateExecution")]

    states = []

    # Add Initialising State which we'll use to execute
    params = MARTe2ConfigurationDatabase(objects={"param1":"Running"})
    prepare = MARTe2Message("+PrepareChangeToRunningMsg", "App", "PrepareNextState", params)

    startmessages = [prepare] + [MARTe2Message("+StartNextStateExecutionMsg","App","StartNextStateExecution")]

    # Note the below is necessary for the HTTPService to be running if you are using one.

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


This example can be found in the examples folder as `state_machine_http.py` with cfg output file `state_machine_http_example.cfg`.