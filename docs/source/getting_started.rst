.. MARTe2-python documentation
   Started on Tue Dec 14 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Getting Started
===============

First, clone and install this repository and it's dependencies::

    $ pip install martepy


.. note::
    Currently the repo only exports configurations and only in the .cfg format. There are future plans to support multiple configurations and importing - it is referenced in the developer guide how you may incorporate this.

You should be familiar with MARTe2 and this documentation is not going to walk through how to use it. What we will demonstrate is how to use
this python repository to build a relatively simple application.

Using martepy for building MARTe configurations
***********************************************

Within martepy/marte2 you have assorted files and folders organised for defining MARTe2 objects such as GAMs, DataSources and generic objects.

.. note:: Examples are available under the example folder and can be started in the docker image available by sharing the top level directory, running an example python file and then running the command ./examples/marte.sh -l RealTimeLoader -s Running -f marte2.cfg

You start with a main application instance, defined as the class object MARTe2Application under generic_application.py in the martepy/marte2 directory. This application holds multiple lists related to the configuration:

- externals: anything that sits outside of the application instance in a MARTe2 configuration such as the HTTP WebService object or the StateMachine object.
- objects: Same as externals - sort of a duplication
- additional_datasources: any datasources
- functions: the configuration GAMs
- states: any states within the configuration

*There are other lists but these are mainly unused*

Many GAMs from MARTe2-components have already been developed and so you can achieve an application with whats available. It is fairly easy to add new GAMs as well if you need to. The GAMs available sit under martepy/marte2/gams. Similary datasources and interfaces sit in their own respective directories. Objects is a directory whereby you have an object instance that sits underneath another object in a MARTe2 configuration.

An example of these kinds of objects are:

- HTTPObjectBrowser
- Parameters (used in Messages)
- Messages
- ReferenceContainer (used alot)
- StateMachine
- ConfigurationDatabase

A minimal viable application needs the following:
- At least one state
- At least one functioning GAM in said state
- A blocking function/datasource that enforces the cycletime

A standard getting started MARTe2 application is typically to setup a LoggerDataSource, a Timing DataSource and funnel the counter from the timer to the logger so this increments per cycle and is displayed on screen. So let's get started with this minimal example.

It's useful to first also define the below function, it's useful for setting up the cpu selections on datasources and other objects.

.. code:: python

    CPU_OFFSET_FROM_ONE = 0  # 0 to start at cpu 1
    def cpu_thread_gen(x):
        ''' Generate a cpu core to used based on thread number x and pre-defined offset from core 1. '''
        return str(hex(2 ** (x + CPU_OFFSET_FROM_ONE)))


Now, import what you will need:

.. code:: python

    from martepy.marte2 import (
        MARTe2GAM,
        MARTe2Application,
        MARTe2RealTimeThread,
        MARTe2RealTimeState,
        MARTe2GAMScheduler
    )

    from martepy.marte2.gams import (
        IOGAM
    )

    from martepy.marte2.datasources import (
        LinuxTimer,
        LoggerDataSource,
        TimingDataSource,
        GAMDataSource
    )

Once we have this, let's define our application and add the datasources we need:

.. code:: python

    app = MARTe2Application()

    app.add(additional_datasources = [
        TimingDataSource(configuration_name = '+Timings'),
    ])

    app.add(inputs = [
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

We only need the one IOGAM to relay the data from timer to logger so let's add this:

.. code:: python

    _signals = [
            ('DTime', {'MARTeConfig': {'DataSource': 'LoggerDataSource', 'Alias': 'DTime', 'Type': 'uint32'}}),
        ],
    )]

    app.add(functions = functions)

.. note:: it's best to retain your GAM functions as a array so you can reuse their instances in defining the states next.

Now that we have all this, you can define the state for running in:

.. code:: python
    
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

Finally, setup your scheduler, you can use GAMScheduler, GAMBareScheduler and FastScheduler. GAMScheduler is suitable for most applications.

.. code:: python

    app.add(internals
    functions = []

    functions += [IOGAM(
        configuration_name = '+GAMDisplay',
        input_signals = [
            ('Time', {'MARTeConfig': {'DataSource': 'Timer', 'Type': 'uint32', 'Frequency': str(500)}}),
        ],
        output = [
        MARTe2GAMScheduler(
            configuration_name = '+Scheduler',
            timing_datasource_name = 'Timings',
            class_name = 'GAMScheduler',
        ),
    ])

Now our application is defined your can build the configuration to return a string which is the actual configuration file contents and then write this to file:

.. code:: python

    full_config_string = app.build_configuration() + '\n'
    with open("timer_logger_example.cfg", "w") as text_file:
        print(full_config_string, file=text_file)

This example can be found in the examples folder as `timer_logger.py` with cfg output file `timer_logger_example.cfg`.

Next steps:

- Review the `water tank example <./water_tank.html>`_.
- It is encouraged to read up on the `simulation framework <./simulation.html>`_.
- Alot of operational functions and configurations were ignored in this example, the default set up is usually adequate for an application but you may want to review the other `examples available <https://github.com/ukaea/MARTe2-python/tree/main/examples>`_.