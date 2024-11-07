"""This is version 2 of the framework, a simplified but more extensive version
It's purpose is to leave alot of the work up to the user in the GUI but also create
a basic simulated version of your application. It will:
- Gather a list of GAM datasources
- Iterate through all states and remove signals produced by external datasources
  replacing these with constantGAMs
- Iterate through all states and find all produced signals
- Create an IOGAM and FileWriter Datasource for these and add this to every state, thread 0.
- For each state, it will iterate through this and create a constantGAM for any producer
  signals not produced in said state.
- Among these constantGAMs it will add a State integer which will increment for each state.
- When the function returns it will provide a dictionary of state name to state integer value.

Req:
- It will support multi-layered types
- It should support between threads using the RealTimeThreadAsyncBridge:
    - In order to do this we need to for each state, identify what signals are not present 
      in thread 0 but are present in other threads.
    - It will then create a AsyncBridge between the two threads to bring that 
      threads' signals into thread 0.
"""
import copy

from martepy.functions.extra_functions import getname # pylint: disable=W0614
from martepy.functions.gam_functions import (getAlias,
                                             isMatchingSignal,
                                             findSignalInFunctionList,
                                             getKeyAttribute,
                                             setDatasource,
                                             addDimensions)
from martepy.marte2.datasources.timing_datasource import TimingDataSource
from martepy.marte2.objects.genericobject import MARTe2Object
from martepy.marte2.gams import IOGAM, ConstantGAM
from martepy.marte2.datasources.linux_timer import LinuxTimer
from martepy.marte2.datasources.gam_datasource import GAMDataSource
from martepy.marte2.datasources.files.reader import FileReader
from martepy.frameworks.end_gam import EndGAM
from martepy.marte2.datasources.async_bridge import AsyncBridge

class SimulationGenerator():
    ''' This class is the simulation generator, it takes a pre-defined MARTe2Application instance,
    replaces the input signals from the outside world and logs all signals which occur during
    execution.
    
    *** It is a highly complex set of functions as it achieves a complex task - as a result, we've
    pylint disabled a few check regarding complex code but we're not exceeding those parameters
    too much and most of these have thorough commenting in. ***'''
    def __init__(self, app, configure=True):
        """Initialise our simulation generator object
        """
        self.original_app = app
        self.reset()
        self.constants_gam_source = GAMDataSource('+' + self.constants_ddb.lstrip('+'))
        self.state_constant_vals = {}
        self.gam_sources = []
        self.replaced_datasources = []
        if configure:
            # Configure immediately
            self.configure()

    def reset(self):
        """Reset our application
        """
        # Reset CPU Configurator
        self.simulation_app = copy.deepcopy(self.original_app)
        self.simulation_app.types_used = []
        self.log_ddb = 'LogGAMSource'
        self.constants_ddb = 'ConstantGAMDatasource'
        self.misc_ddb = 'OutsideWorldGAMDDB'
        self.gam_sources = []
        self.overridden_signal_names = []
        self.simulation_app.config['maxcycles'] = 500

    def configure(self, app=None):
        """This configures the simulation by iterating the application
        and looking for all datasources, for each one it then qualifies
        if they are replacable. If they are then they are catalogued.
        """
        # Allow reseting the app here
        if app is not None:
            self.original_app = app
            self.reset()

        # Collect our GAM Datasources
        self.gam_sources = [a.configuration_name.lstrip('+') for a in
                            self.original_app.additional_datasources if isinstance(
                                a, GAMDataSource)]

        # We want to keep in LinuxTimer's for the user
        linux_timers = [a for a in self.original_app.additional_datasources if isinstance(
            a, LinuxTimer)]

        # # Strip out non-GAM Datasources except: AsyncBridge, FileReader.
        # datasources = self.simulation_app.additional_datasources
        # datasources = [a for a in self.original_app.additional_datasources if isinstance(a, (
        #     AsyncBridge, FileReader, GAMDataSource, TimingDataSource))] + linux_timers

        self._internal_datasources = [a.configuration_name.lstrip('+') for a in
                                 self.original_app.additional_datasources if isinstance(a, (
                                     AsyncBridge, FileReader, GAMDataSource, TimingDataSource))]

        self._internal_datasources += [self.misc_ddb, self.log_ddb, self.constants_ddb]
        self._internal_datasources += [a.configuration_name.replace('+','') for a in linux_timers]
        # Ensure we know what we removed
        self.replaced_datasources = [a for a in self.original_app.additional_datasources if not (
            isinstance(a, (AsyncBridge, FileReader, GAMDataSource, LinuxTimer, TimingDataSource)))]

    def _createGamSources(self):
        ''' Define the GAMSources that are used to partition signals '''
        # Create the GAM DataSource for holding our constants and signals
        self.constants_gam_source = GAMDataSource('+' + self.constants_ddb.lstrip('+'))
        LogGAMSource = GAMDataSource('+' + self.log_ddb.lstrip('+'))
        miscDDB = GAMDataSource('+' + self.misc_ddb.lstrip('+'))
        # Ensure we're not reading this
        for item in [self.constants_gam_source, miscDDB, LogGAMSource]:
            if item not in self.simulation_app.additional_datasources:
                self.simulation_app.additional_datasources += [item]

    def _handleTimer(self):
        ''' Function to either inject a timer and return it or find the timer
        block if already defined by the user and return a pointer to it '''
         # We want to give the user the ability to add and use their own timers whilst simulating
        timer = next((a for a in self.simulation_app.additional_datasources if isinstance(
            a, LinuxTimer)), None)
        freq = self.simulation_app.config['timefrequency']
        if not timer:
            timer = LinuxTimer(
                        configuration_name = '+Timer',
                        cpu_mask = 12,
                        sleep_nature = 'Busy',
                        execution_mode = 'RealTimeThread',
                        frequency = freq
                    )
            self.simulation_app.add(additional_datasources = [timer])

        return timer, freq

    def _handlerTimerIO(self, timer, freq):
        # Find the function reading from our linux timer
        timing_block = None

        for state in self.simulation_app.states:
            if state.threads.objects:
                thread = state.threads.objects[0]
                timer_name = timer.configuration_name.replace('+','')
                timing_block = next((a for a in thread.functions if any(
                    b for b in a.input_signals if b[1]['MARTeConfig']['DataSource'] == timer_name)
                    ),None)
                # Only one IOGAM can read from the linuxtimer,
                if not timing_block:
                    timing_block = IOGAM(
                            configuration_name = '+TimerHandler',
                            input_signals = [
                                ('Time', {'MARTeConfig': {'DataSource': 'Timer',
                                                           'Type': 'uint32', 
                                                           'Frequency': freq}}),
                            ],
                            output_signals = [
                                ('DTime', {'MARTeConfig': {'DataSource': self.gam_sources[0],
                                                            'Alias': 'DTime', 'Type': 'uint32'}}),
                            ],)
                    if timing_block not in self.simulation_app.functions:
                        self.simulation_app.functions.insert(0, timing_block)
                    if timing_block not in thread.functions:
                        thread.functions.insert(0, timing_block)
                else:
                    # Find which signal specifies the Frequency
                    freq_input = next((a for a in timing_block.input_signals if 'Frequency' in
                                       list(a[1]['MARTeConfig'].keys())), None)
                    if freq_input:
                        freq_input[1]['MARTeConfig']['Frequency'] = freq
                    else:
                        timing_block.input_signals[0][1]['MARTeConfig']['Frequency'] = freq

        return timing_block

    def _createEndStateSignals(self):
        ''' This function section creates the state signal and end-signal:
        Only works if a thread was created for this state '''

        for state in self.simulation_app.states:
            maxcycles = self.simulation_app.config['maxcycles']
            if len(state.threads.objects) > 0:
                state_name = state.configuration_name.lstrip('+')
                thread = state.threads.objects[0]
                thread_name = thread.configuration_name.lstrip('+')
                state_signal = [('state', {'MARTeConfig': {'DataSource': self.gam_sources[0],
                                                           'Type': 'uint32'}})]
                endgam = EndGAM(f'+{state_name}-{thread_name}-end',int(maxcycles),state_signal)
                thread.functions += [endgam]
                self.simulation_app.functions += [endgam]

        # Create a constant into thread0 of each state that allows us to maintain some
        # tracking of which state we are in when we look at logs later on
        self.state_constant_vals = {}
        for index, state in enumerate(self.simulation_app.states):
            state_name = getname(state)
            Statecon = ConstantGAM(f'+{state_name}ConstantLog',
                                   [('state', {'MARTeConfig': {'Type': 'uint32',
                                                               'Default': index,
                                                               'DataSource':
                                                               self.gam_sources[0]}})])
            if len(state.threads.objects) > 0:
                self.simulation_app.functions += [Statecon]
                state.threads.objects[0].functions.insert(0,Statecon)
            self.state_constant_vals[state_name] = index

    def _replaceExternalSignals(self, timing_block): # pylint: disable=R0914, R0912
        ''' This function works out what signals come from the outside world and replaces them '''
        # Only IOGAM's can go between Datasources
        ninternal_datasources = [getname(a) for a in self.replaced_datasources]
        self.simulation_app.additional_datasources = [a for a in
                                                      self.simulation_app.additional_datasources if
                                                      getname(a) not in ninternal_datasources]
        for s_i, state in enumerate(self.simulation_app.states): # pylint: disable=R1702
            state_name = getname(state)
            for t_i, thread in enumerate(state.threads.objects):
                # Iterate through each state and each subsequent thread
                thread_name = getname(thread)
                # Catalogue the functions we add, maintain a boolean if we added any
                # and create the first constant GAM
                new_functions = []
                top_constant_gam = ConstantGAM(f'+{state_name}{thread_name}TopLvlConstants',[])
                added=False
                for f_i, function in enumerate(thread.functions):
                    # For each function, if it is an IOGAM
                    curr_func = self.simulation_app.states[s_i].threads.objects[t_i].functions[f_i]
                    if isinstance(function, IOGAM):
                        # Ignore our timing block as we don't want to replace this.
                        if function == timing_block:
                            continue # Don't mess with the timer_handler
                        # Is a transferring function possibly
                        to_pop = []
                        for input_signal in function.input_signals:
                            # Check each input signal, if they come from non-managed datasources
                            # they come from the outside world and need replacing
                            datasource = input_signal[1]['MARTeConfig']['DataSource']
                            if datasource in ninternal_datasources:
                                # We need to replace this signal
                                # Manage if it's an EPICS signal
                                if 'PVName' in input_signal[1]['MARTeConfig'].keys():
                                    del input_signal[1]['MARTeConfig']['PVName']

                                # We can't do inplace for new functions to the
                                # thread so we append afterwards. Now delete the input and
                                # it's corresponding output signal.
                                to_pop += [input_signal] # can't remove them
                                # within an iterator of them.
                        # Now that we have found what input signals we need to replace
                        # Remove the IO Input signal we replaced and the output signal
                        for itemtoremove in to_pop:
                            # Figure out the function
                            function = curr_func
                            signals_list = function.input_signals
                            # Where our signal is
                            index = signals_list.index(itemtoremove)
                            added=True
                            # Get the output signal - this is what we need to really replace with a
                            # default value
                            output_signal = function.output_signals[index]
                            alias = getAlias(output_signal)
                            # Track what signals we override
                            self.overridden_signal_names.insert(0,alias)
                            out_type = output_signal[1]['MARTeConfig']['Type']
                            default = 0 if out_type in ('uint32','uint64', 'uint8') else 0.0
                            # Now replace the signal and insert it into our constantsGAM
                            io_gam = self._replaceSignal(output_signal, top_constant_gam,
                                                getname(self.constants_gam_source),
                                                self.simulation_app, default)
                            # Append our IOGAM if one was needed to be created
                            if io_gam:
                                new_functions += [io_gam]
                            # Now remove the signal now that it is done
                            signals_list.remove(itemtoremove)
                            function.output_signals.pop(index)
                        for o_i, output_signal in enumerate(function.output_signals):
                            datasource = output_signal[1]['MARTeConfig']['DataSource']
                            if datasource in ninternal_datasources:
                                # This feeds to the outside world - we don't want to do this,
                                # we should place it into our misc DDB
                                qsignal = function.output_signals[o_i]
                                qsignal[1]['MARTeConfig']['DataSource'] = self.misc_ddb

                if added:
                    # If we needed to replace signals, now we can add our constant GAM as it
                    # now contains signals
                    thread.functions.insert(0,top_constant_gam)
                    for new_function in new_functions:
                        # Any other new functions also need adding to the thread definition
                        thread.functions.insert(1,new_function)

    def build(self): # pylint: disable=R0914, R0912
        """This function is where the actual work gets done to create the new application
        for simulation, configure simply collects information based on the given application
        instance.
        """
        self._createGamSources()

        timer, freq = self._handleTimer()

        timing_block = self._handlerTimerIO(timer, freq)

        self.simulation_app.default_data_source = self.gam_sources[0]

        self._createEndStateSignals()

        self._replaceExternalSignals(timing_block)

        # Resanitize an application between its state, threads functions
        # and it's functions definitions.
        self.simulation_app.sanitize()

        self.simulation_app.buildLog()

        # Now we iterate through again and use a multitude of any's to check:
        # Is there in this state, any thread, with an IOGAM, that is producing that
        # required signal into our LogDDB
        for state in self.simulation_app.states: # pylint: disable=R1702
            missingsignals = ConstantGAM(f'+missingsignals{getname(state)}', [])
            missingio = IOGAM(f'+missingiosignals{getname(state)}',[],[])
            # This gets flagged up by pylint as unnecessary but is in fact very necessary!
            # It delinks the pointer refs
            total_signals = [a for a in self.simulation_app.logging_iogam.input_signals] # pylint: disable=R1721
            total_signals += [a for a in self.simulation_app.async_to_io.input_signals] # pylint: disable=R1721
            for signal in total_signals:
                # This is a complicated if any setup, we're asking, is any signal of any function
                # in any thread of our current state, matching our signal we are looking for
                if len(state.threads.objects) > 0:
                    # Is a used thread
                    if not any(
                        any(any(isMatchingSignal(output_signal, signal) for
                                output_signal in function.output_signals) for
                                function in thread.functions) for thread in state.threads.objects):
                        # There is no producer for this signal within this state
                        # use replace signal to create this signal in thread 0 for this state
                        # We need to account for the fact that defaults must match if this was
                        # produced by a constantGAM for the same datasource.
                        # So we must therefore find the original producer of this signal
                        producer = findSignalInFunctionList(signal, self.simulation_app.functions)

                        default = 0
                        if producer: # a Producer was found
                            if 'Default' in producer[1]['MARTeConfig'].keys(): # It has a default
                                default = getKeyAttribute(producer, 'Default')

                        modsignal = copy.deepcopy(signal)
                        # This next step might seem redundant but it was found
                        # necessary during testing - we ensure we don't repeat the name in
                        # our missing signals gam
                        alias = getAlias(modsignal)
                        unique_name = self.simulation_app.newUniqueName(alias)
                        if not any(out_signal[0] == unique_name for
                                   out_signal in missingsignals.output_signals):
                            # Don't duplicate our work
                            modsignal = (unique_name,modsignal[1])
                            modsignal[1]['MARTeConfig']['Alias'] = unique_name
                            setDatasource(modsignal, self.constants_ddb)
                            self._replaceSignal(modsignal, missingsignals,
                                                self.constants_ddb, self.simulation_app, default)
                            missingio.input_signals += [modsignal]
                            missingio.output_signals += [signal]

            if len(missingsignals.output_signals) > 0:
                state.threads.objects[0].functions += [missingsignals, missingio]

        self.simulation_app.sanitize()

        self.simulation_app.removeUnused()

        # Now we want to insert the internals of types we don't have in the application
        # Need to insert these into the objects part of the application so they appear
        # at the very start
        if self.simulation_app.types_used:
            for type_name in self.simulation_app.types_used:
                empty_obj = MARTe2Object(f'+{type_name}', f'{type_name}::{type_name}Cls')
                self.simulation_app.add(externals=[empty_obj])
        return self.simulation_app

    def unflattenReplace(self, signal_to_replace, type_name, # pylint: disable=R0914
                          constant_gam=None, constantgamsource=None):
        ''' This is a recursive algorithm to unflatten a signal and create a Constant
        GAM which replicates the signal with it's defaults and then combines it back to it's
        complex type structure. '''
        # Get the type definition
        ualias = getAlias(signal_to_replace)
        type_def = self.simulation_app.type_db.getTypeByName(type_name)
        if type_def.name not in self.simulation_app.types_used:
            self.simulation_app.types_used += [type_def.name]
        # For each struct member
        field_members = []
        for field in type_def.fields:
            # Get a name for it
            alias = field.name
            # If it's not fundamental, unpack it as well
            if not self.simulation_app.type_db.isFundamental(field.type):
                # Recursively unpack it
                unflattened_signal = self.unflattenReplace(self, field.type, constantgamsource)
                field_members += unflattened_signal.output_signals[0]
            else:
                # Create the constant value for this field member
                # It's output name should match the same convention of how unflatten
                # creates the overall output name
                constant_signal = (type_name+alias,{'MARTeConfig':{}})
                constant_signal[1]['MARTeConfig']['Type'] = field.type

                # Set the default value for our replacement signal
                default = 0 if field.type in ('uint32', 'uint64', 'uint8') else 0.0
                # We need to account for if our type is multiple elements
                if 'NumberOfElements' in constant_signal[1]['MARTeConfig']:
                    num_elements = int(getKeyAttribute(constant_signal,'NumberOfElements'))
                    # Okay then create the default array format
                    default = "{" + ' '.join([str(default)]*num_elements) + "}"
                    addDimensions(constant_signal) # Double check we have dimensions too
                else:
                    addDimensions(constant_signal)
                constant_signal[1]['MARTeConfig']['Default'] = str(default)
                constant_signal[1]['MARTeConfig']['DataSource'] = constantgamsource
                constant_signal[1]['MARTeConfig']['Alias'] = type_name+alias+ualias
                constant_signal = (type_name+alias,constant_signal[1])
                constant_gam.output_signals += [constant_signal]

                # Now our field member exists, we need to construct our type
                field_member_for_io = copy.deepcopy(constant_signal)
                if 'Default' in field_member_for_io[1]['MARTeConfig']:
                    del field_member_for_io[1]['MARTeConfig']['Default']
                field_members += [field_member_for_io]

        output_signal_for_io = copy.deepcopy(signal_to_replace)
        type_io_gam = IOGAM(f'+IO{ualias}_{type_name}', field_members,[output_signal_for_io])
        self.simulation_app.functions += [type_io_gam]
        return type_io_gam

    def _replaceSignal(self, signal_to_replace=(), constant_gam=None, constantgamsource=None, # pylint: disable=R0917
                       application=None, default=0):
        """This function will create the constant that replaces this signal.
        If this is a basic type, it will simply add this to the constant_gam
        and then add that to the iogam to get filtered into our constantGAMSource,
        however if it is a more complex signal type, it will create the necessary
        constants and IOGAM's to construct this signal type and then place this in
        the IOGAM, the new functions will be added to thread.functions and
        application.functions in place by reference.
        """
        constant_signal = copy.deepcopy(signal_to_replace)
        if 'Frequency' in list(constant_signal[1]['MARTeConfig'].keys()):
            del constant_signal[1]['MARTeConfig']['Frequency']
        type_name = constant_signal[1]['MARTeConfig']['Type']
        # Get the type and check if fundamental
        if not application.type_db.isFundamental(type_name):
            # Really we need to follow the type
            # Challenge: How to handle Types which we may not know in advance?
            # Maybe we make this recursively support nested types? or just keep it flat and simple
            # Start by creating a ConstantGAM from extracting the type
            top_lvl = self.unflattenReplace(signal_to_replace,
                                             type_name, constant_gam, constantgamsource)

            return top_lvl
        # Is a fundamental type
        # Very simple, just add the type and default 0 to our constantGAM
        alias = getAlias(signal_to_replace)
        num_elements = 1
        if 'NumberOfElements' in list(constant_signal[1]['MARTeConfig'].keys()):
            num_elements = int(getKeyAttribute(constant_signal,'NumberOfElements'))
            default = "{" + ' '.join([str(default)]*num_elements) + "}"
        addDimensions(constant_signal)
        new_signal = (signal_to_replace[0], {'MARTeConfig':{
            'Type': type_name, 'Default': str(default),
            'DataSource': constant_signal[1]['MARTeConfig']['DataSource'],
            'Alias': alias}})
        new_signal[1]['MARTeConfig']['NumberOfElements'] = str(num_elements)
        if 'NumberOfDimensions' in list(constant_signal[1]['MARTeConfig'].keys()):
            num_dim = int(getKeyAttribute(constant_signal,'NumberOfDimensions'))
            new_signal[1]['MARTeConfig']['NumberOfDimensions'] = str(num_dim)
        else:
            new_signal[1]['MARTeConfig']['NumberOfDimensions'] = '1'

        constant_gam.output_signals += [new_signal]
        return None
