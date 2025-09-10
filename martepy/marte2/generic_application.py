"""A more unified and simpler approach to developing MARTe2 application
"""
import copy
import os
import martepy.marte2.configwriting as marteconfig
from martepy.functions.gam_functions import (addAlias, addDimensions, assignUniqueName, consolidate,
                                             getAlias, getDatasource, getGamByName,
                                             getKeyAttribute, setDatasource,
                                             setKeyAttribute,
                                             removeKeysFromConfig)
from martepy.functions.extra_functions import getname
from martepy.marte2.gams.iogam import IOGAM
from martepy.marte2.datasources.gam_datasource import GAMDataSource
from martepy.marte2.factory import Factory
from martepy.marte2.type_database import TypeDBv2 as TypeDB
from martepy.marte2.datasources.files.file_datasources import RFileWriter
from martepy.marte2.datasources.files.writer import FileWriter
from martepy.marte2.qt_functions import generateUniqueName
from martepy.marte2.datasources.async_bridge import AsyncBridge

class MARTe2Exception(Exception):
    ''' A general MARTe2 Exception - should match similar to what you would receive
    if you tried to actually run the configuration in MARTe2.'''

class MARTe2Application():
    ''' The pythonic object representation of a MARTe2 application, how to build it and
    ultimately write this into it's string configuration format. '''
    def __init__(self, app_name = '$App'):
        self.resetApp()
        self.externals = self.NonDuplicatingList()
        self.inputs = []
        self.outputs = []
        self.additional_datasources = self.NonDuplicatingList()
        self.additional_logging = {'inputs':[],'outputs':[],'logger_in':[]}
        self.triggering_services = []
        self.functions = self.NonDuplicatingList()
        self.states = self.NonDuplicatingList()
        self.internals = self.NonDuplicatingList()
        self.objects = self.NonDuplicatingList()
        self.default_data_source = 'DDB0'
        self.config = {'log': True,
                       'log_level': 31,
                       'error_state': True,
                       'state_machine': True,
                       'numcores': 16,
                       'timefrequency': 1000}
        self.type_db = TypeDB()
        self.maxcycles = 40000
        self.app_name = 'App'
        # Load the factory
        self.factory = Factory()
        self.marte2_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
        datasources = os.path.join(self.marte2_dir,"datasources", "datasources.json")
        gams = os.path.join(self.marte2_dir,"gams", "gams.json")
        objects = os.path.join(self.marte2_dir,"objects","objects.json")
        self.factory.loadRemote(datasources)
        self.factory.loadRemote(gams)
        self.app_name = app_name
        self.factory.loadRemote(objects)
        self.logging_iogam = IOGAM('+LoggingGAM',[],[])
        self.filewriter = RFileWriter('+LoggingFileWriter',filename='output.csv')
        self.asyncbridge = AsyncBridge('+LoggingAsyncBridge')
        self.async_to_io = IOGAM('+async_sim_io',[],[])
        self.io_asyncs = []
        self.loggingintoio = IOGAM('+ToLogGAM',[],[])
        self.iogams = [self.logging_iogam, self.loggingintoio, self.async_to_io]
        self._internal_datasources = []

    def loadTypeLibrary(self, filepath: str):
        ''' Load type definition directory into our type database '''
        self.type_db.loadDb(filepath)

    class NonDuplicatingList(list):
        ''' A non duplicating list class - effectively a set '''
        def append(self, item):
            if not any(item == list_item for list_item in self):
                super().append(item)

        def __iadd__(self, other):
            for item in other:
                self.append(item)
            return self

    def resetApp(self):
        ''' Reset our application instance. '''
        self.externals = self.NonDuplicatingList()
        self.inputs = []
        self.outputs = []
        self.additional_datasources = self.NonDuplicatingList()
        self.additional_logging = {'inputs':[],'outputs':[],'logger_in':[]}
        self.triggering_services = []
        self.functions = self.NonDuplicatingList()
        self.states = self.NonDuplicatingList()
        self.internals = self.NonDuplicatingList()
        self.objects = self.NonDuplicatingList()


    def add(self, externals=[], additional_datasources=[], functions=[],
            states=[], internals=[], objects=[]):
        ''' Safely add objects to our application '''
        self.externals += externals
        self.additional_datasources += additional_datasources
        self.functions += functions
        self.states += states
        self.internals += internals
        self.objects += objects

    def getSignals(self):
        """We want to produce a list of all signals made
        """
        signals = {}
        for anyproducer in self.additional_datasources + self.functions:
            for output_signal in anyproducer.output_signals:
                if 'DataSource' in output_signal[1]['MARTeConfig']:
                    datasource = output_signal[1]['MARTeConfig']['DataSource']
                else:
                    datasource = anyproducer.configuration_name.lstrip('+')
                if datasource not in signals:
                    signals[datasource] = {}
                signals[datasource][getAlias(output_signal)] = output_signal
        return signals

    def getInputDatasources(self):
        ''' Return a list of datasources which bring data into the application from the outside
        world '''
        # Need to try a different method, we need to collect what is our DDB GAM Datasources first
        # So we can ignore these and then any input signal from any other datasource can be assumed
        # to have come from the outside world, we collect these aliases, avoid duplicates
        gam_datasources = [gam_datasource for gam_datasource in self.additional_datasources if
                           isinstance(gam_datasource, GAMDataSource)]
        gam_names = [gam_datasource.configuration_name.strip('+') for gam_datasource
                     in gam_datasources]
        external_inputs = []
        for function in self.functions:
            for input_signal in function.input_signals:
                if input_signal[1]['MARTeConfig']['DataSource'] not in gam_names:
                    external_inputs.append(input_signal)

        return external_inputs

    def getOutputDatasources(self):
        ''' Return a list of datasources which output to the outside world '''
        # Need to try a different method, we need to collect what is our DDB GAM Datasources first
        # So we can ignore these and then any output signal to any other datasource can be assumed
        # to go to the outside world, we collect these aliases, avoid duplicates
        gam_datasources = [gam_datasource for gam_datasource in self.additional_datasources if
                           isinstance(gam_datasource, GAMDataSource)]
        gam_names = [gam_datasource.configuration_name.strip('+') for
                     gam_datasource in gam_datasources]
        external_outputs = []
        for function in self.functions:
            for output_signal in function.output_signals:
                if output_signal[1]['MARTeConfig']['DataSource'] not in gam_names:
                    external_outputs.append(output_signal)

        return external_outputs

    def getinputSignals(self):
        """We want to produce a list of all signals made
        """
        signals = {}

        for anyproducer in self.additional_datasources + self.functions:
            for output_signal in anyproducer.output_signals:
                signals[getAlias(output_signal)] = output_signal
        return signals

    def newUniqueName(self, basename):
        ''' Generate a unique name from what is already defined in our application. '''
        count = 0
        existing_signals = []
        name = basename
        for function in self.functions:
            for output_signal in function.output_signals:
                existing_signals.append(output_signal[0])
                existing_signals.append(getAlias(output_signal))
        if name in existing_signals:
            for _ in existing_signals: # It would be impossible to exceed this,
                # better than doing an infinite while loop
                count = count + 1
                name = f'{basename}{count}'
                if name not in existing_signals:
                    break
        return name

    def onlyErrors(self): # pylint:disable=R0914, R0915, R0912
        ''' Check our application for any errors given what we know, if we were to run this
        configuration now, what would MARTe2 error/say? '''
        exceptions = []
        consumed = {}
        produced = {}
        function_names = []
        # Signal names of same name within same function - use MARTeApplication.getAlias
        for function in self.functions:
            # Same named functions in application
            if function.configuration_name.lstrip('+') in function_names:
                exceptions.append(MARTe2Exception("""Two functions with the same name exist -
this can happen if you have two functions in the same state or across states which are
non-identical but identical in name."""))
            function_names.append(function.configuration_name.lstrip('+'))
            input_signal_names = []
            for signal in function.input_signals:
                if signal[0] in input_signal_names:
                    exceptions.append(MARTe2Exception(f"""Cannot have same root name of input
signal repeated within function: {function.configuration_name.lstrip('+')}"""))
                input_signal_names.append(signal[0])
                datasource = signal[1]['MARTeConfig']['DataSource']
                if datasource not in consumed:
                    consumed[datasource] = []
                consumed[datasource].append(getAlias(signal))
            output_signal_aliases = []
            output_signal_names = []
            for signal in function.output_signals:
                if getAlias(signal) in output_signal_aliases:
                    exceptions.append(MARTe2Exception(f"""Multiple producers of alias within
function: {function.configuration_name.lstrip('+')}"""))
                elif signal[0] in output_signal_names:
                    exceptions.append(MARTe2Exception(f"""Cannot have same root name of output
signal repeated within function: {function.configuration_name.lstrip('+')}"""))
                output_signal_aliases.append(getAlias(signal))
                output_signal_names.append(signal[0])

            # Perform a check on IOGAM and the same bytes in as bytes out
            if function.class_name == 'IOGAM':
                def calculateTotalBytes(signals):
                    type_sizes = {
                        'uint8': 1, 'int8': 1,
                        'uint16': 2, 'int16': 2,
                        'uint32': 4, 'int32': 4, 'float32': 4,
                        'uint64': 8, 'int64': 8, 'float64': 8
                    }
                    total = 0
                    for signal in signals:
                        _, config = signal
                        marte = config.get('MARTeConfig', {})
                        type_str = marte.get('Type')
                        num_elements = int(marte.get('NumberOfElements', '1'))
                        if type_str not in type_sizes:
                            exceptions.append(MARTe2Exception(f"Unsupported type: {type_str}"))
                        total += type_sizes[type_str] * num_elements
                    return total

                input_total = calculateTotalBytes(function.input_signals)
                output_total = calculateTotalBytes(function.output_signals)

                if input_total != output_total:
                    exceptions.append(MARTe2Exception(
                        f"""Input/output size mismatch: {input_total} bytes in, {output_total}
 bytes out in IOGAM function: {function.configuration_name}"""
                    ))
        # More than one producer of a signal in a datasource - use MARTeApplication.getAlias

        for datasource_name, datasource_signals in produced.items():
            seen = set()
            for string in datasource_signals:
                if string in seen:
                    exceptions.append(MARTe2Exception(f"""Multiple producers found of
signal/alias: {string} in datasource {datasource_name}"""))
                else:
                    seen.add(string)
        # Same named datasources in application
        datasource_names = []
        for datasource in self.additional_datasources:
            if datasource.configuration_name.lstrip('+') in datasource_names:
                exceptions.append(MARTe2Exception("""Two datasources with the same name exist
 - this can happen if you have two datasources in the same state or across states which are
 non-identical but identical in name."""))
            datasource_name = datasource.configuration_name.replace('+','')
            datasource_names.append(datasource_name)
            input_signal_names = []
            for signal in datasource.input_signals:
                if signal[0] in input_signal_names:
                    exceptions.append(MARTe2Exception(f"""Cannot have same root name of input
 signal repeated within datasource: {datasource.configuration_name.lstrip('+')}"""))
                input_signal_names.append(signal[0])

            output_signal_names = []
            for signal in datasource.output_signals:
                if signal[0] in output_signal_names:
                    exceptions.append(MARTe2Exception(f"""Cannot have same root name of
 output signal repeated within datasource: {datasource.configuration_name.lstrip('+')}"""))
                output_signal_names.append(signal[0])
            # A datasource must be read/written in each state
            for input_signal in datasource.input_signals:
                for state in self.states:
                    # Ignore if not functions in this state
                    if all(len(thread.functions) == 0 for thread in state.threads.objects):
                        continue
                    if not any(((sinput[1]['MARTeConfig']['DataSource'] ==
                                 datasource.configuration_name.lstrip('+') and
                                 getAlias(sinput) == getAlias(input_signal) for
                                 sinput in function.input_signals) for
                                 function in thread.functions) for
                                 thread in state.threads.objects):
                        exceptions.append(MARTe2Exception(f"""No function in state
{state.configuration_name.lstrip('+')} found reading from datasource
{datasource.configuration_name.lstrip('+')} for signal {getAlias(input_signal)}"""))
                    if datasource_name not in consumed:
                        consumed[datasource_name] = []
                    consumed[datasource_name].append(getAlias(input_signal))

            for output_signal in datasource.output_signals:
                for state in self.states:
                    if all(len(thread.functions) == 0 for thread in state.threads.objects):
                        continue
                    if not any(((output[1]['MARTeConfig']['DataSource'] ==
                                 datasource.configuration_name.lstrip('+') and
                                 getAlias(output) == getAlias(output_signal) for
                                 output in function.output_signals) for
                                 function in thread.functions) for
                                 thread in state.threads.objects):
                        exceptions.append(MARTe2Exception(f"""No function in state
{state.configuration_name.lstrip('+')} found writing to datasource
{datasource.configuration_name.lstrip('+')} for signal {getAlias(output_signal)}"""))
                if datasource_name not in produced:
                    produced[datasource_name] = []
                if getAlias(output_signal) not in produced[datasource_name]:
                    produced[datasource_name].append(getAlias(output_signal))
        # All consumers must have their producing signal - use MARTeApplication.getAlias
        for datasource_name, consumed_signals in consumed.items():
            for consumer_signal in consumed_signals:
                if datasource_name not in produced:
                    if datasource_name not in [getname(a) for a in self.additional_datasources]:
                        exceptions.append(MARTe2Exception(f"""No datasource {datasource_name}
 found yet consumed by signal {consumer_signal}"""))
                if datasource_name not in produced:
                    if datasource_name not in [getname(a) for a in self.additional_datasources]:
                        exceptions.append(MARTe2Exception(f"""datasource {datasource_name} not
  found for consumed signal {consumer_signal}"""))
                    continue
                if consumer_signal not in produced[datasource_name]:
                    exceptions.append(MARTe2Exception(f"""No producer found for signal
 {consumer_signal} in datasource {datasource_name}"""))

        # Now qualify that you can't have states with the same name and
        # subsequently threads with the same name
        state_names = []
        for state in self.states: # pylint: disable=R1702
            thread_names = []
            produced_state = copy.deepcopy(produced)
            if state.configuration_name.lstrip('+') in state_names:
                exceptions.append(MARTe2Exception(f"""Multiple states with the same
 name: {state.configuration_name.lstrip('+')}"""))
            state_names.append(state.configuration_name.lstrip('+'))
            for thread in state.threads.objects:
                if thread.configuration_name.lstrip('+') in thread_names:
                    exceptions.append(MARTe2Exception(f"""Multiple threads with the same
 name in state: {state.configuration_name.lstrip('+')},
 with name: {thread.configuration_name.lstrip('+')}"""))
                for function in thread.functions:
                    for output_signal in function.output_signals:
                        if 'DataSource' in signal[1]['MARTeConfig'].keys():
                            datasource = signal[1]['MARTeConfig']['DataSource']
                            if datasource not in produced_state:
                                produced_state[datasource] = []
                            produced_state[datasource].append(getAlias(signal))
                thread_names.append(thread.configuration_name.lstrip('+'))

        # Only one function can write to a FileWriter across states/threads
        for filewriter in [a for a in self.additional_datasources if
                           isinstance(a, (FileWriter, RFileWriter))]:
            writers = [a for a in self.functions if any(
                getKeyAttribute(output_signal, 'DataSource') ==
                getname(filewriter) for output_signal in a.output_signals)]
            if len(writers) > 1:
                exceptions.append(MARTe2Exception(f"""Multiple writers to FileWriter
 {getname(filewriter)}"""))

        return exceptions

    @staticmethod
    def _unflattenLog(orig_signal, type_db, loggingiogam, loggingintoio, filewriter, loggamsource): # pylint:disable=R0914
        # Here we want to get the signals associated type and
        # then unflatten it's members so we can get it into
        # the SimFileWriter
        new_gams = []
        types_used = []
        type_name = getKeyAttribute(orig_signal,'Type')
        type_def = type_db.getTypeByName(type_name)

        if type_def.name not in types_used:
            types_used += [type_def.name]

        top_gam = IOGAM(f'+unflatten{getAlias(orig_signal)}',
                        input_signals=[orig_signal], output_signals=[])
        new_gams = [top_gam]

        for field in type_def.fields:
            if not type_db.isFundamental(field.type):
                new_gams += MARTe2Application._unflattenLog(field, type_db, loggingiogam,
                                                            loggingintoio, filewriter,
                                                            loggamsource)
            else:
                # For each field, we now want to create an IOGAM output_signal for it
                alias = getAlias(orig_signal) + field.name
                out_sgl = (alias, copy.deepcopy(orig_signal[1]))
                setKeyAttribute(out_sgl,'Type',field.type)
                default = 0 if field.type in ('uint32','uint64', 'uint8') else 0.0
                setKeyAttribute(out_sgl,'Default',default)
                setKeyAttribute(out_sgl,'Alias',alias)
                top_gam.output_signals.append(out_sgl)
                loggingiogam.input_signals += [out_sgl]
                out_sgl = copy.deepcopy(out_sgl)
                if any(signal[0] == out_sgl[0] for signal in loggingiogam.output_signals):
                    existing_names = [a[0] for a in loggingiogam.input_signals]
                    out_sgl = (generateUniqueName(existing_names, out_sgl[0]), out_sgl[1])

                setKeyAttribute(out_sgl,'DataSource',loggamsource)

                loggingiogam.output_signals += [out_sgl]
                loggingintoio.input_signals += [out_sgl]
                out_sgl = copy.deepcopy(out_sgl)
                setKeyAttribute(out_sgl,'DataSource',getname(filewriter))

                loggingintoio.output_signals += [out_sgl]

                out_sgl = copy.deepcopy(out_sgl)
                removeKeysFromConfig(out_sgl, ['DataSource'])
                filewriter.input_signals += [out_sgl]
        return new_gams

    def _logSignal(self, signal, thread_index: int, state, thread): # pylint: disable=R0914,R0915
        ''' This function will log a signal, if it is outside the primary thread
        it will use an Async Bridge to transfer the signal to the primary and then 
        add this to the log. If it is a complex type, it will unflatten the signal type. '''
        # Is not a signal from the outside world and therefore we want to log it
        # into our primary thread and primary FileWriter for the simulation.
        new_functions = []
        osig_name = getAlias(signal)
        if thread_index == 0:
            # Now we need to add to loggingintoio IOGAM to get this into our
            # LoggingGAMSource

            if not any(getAlias(signal) == osig_name for
                        signal in self.logging_iogam.input_signals):

                new_signal = copy.deepcopy(signal)
                removeKeysFromConfig(new_signal, ['Default'])

                addDimensions(new_signal)

                addAlias(new_signal)

                out_signal = copy.deepcopy(new_signal)

                if self.type_db.isFundamental(
                    new_signal[1]['MARTeConfig']['Type']):

                    setDatasource(out_signal, 'LogGAMSource')

                    assignUniqueName(new_signal, self.logging_iogam.input_signals)

                    self.logging_iogam.input_signals += [new_signal]

                    assignUniqueName(out_signal, self.logging_iogam.output_signals)

                    removeKeysFromConfig(out_signal, ['Alias'])

                    self.logging_iogam.output_signals += [out_signal]

                    self.loggingintoio.input_signals += [out_signal]

                    out_signal = copy.deepcopy(out_signal)

                    setDatasource(out_signal, getname(self.filewriter))

                    self.loggingintoio.output_signals += [out_signal]

                    out_signal = copy.deepcopy(out_signal)

                    removeKeysFromConfig(out_signal, ['DataSource'])

                    self.filewriter.input_signals += [out_signal]
                else:
                    new_functions += MARTe2Application._unflattenLog(out_signal,
                                                                     self.type_db,
                                                                     self.logging_iogam,
                                                                     self.loggingintoio,
                                                                     self.filewriter,
                                                                     'LogGAMSource')
        else:
            # Create an IOGAM to get it to the bridge - if not already made
            # Now add signal to loggingintoio
            # Next check if not already logged
            # We need to signals, the input of our signal to the async bridge from the thread
            # and the output signal to the async bridge
            input_signal = copy.deepcopy(signal)
            # Neither signal should have a Default value set in the IOGAM
            removeKeysFromConfig(input_signal, ['Default'])

            # We assume here that the AsyncBridge can handle complex types
            # so we will unflatten this later in the primary thread, set the Async Bridge
            state_name = getname(state)
            thread_name = getname(thread)
            iobridge_name = f'+{state_name}_{thread_name}_async_sim'
            # Get the Async Bridge in question
            iobridge = getGamByName(iobridge_name.lstrip('+'), self.io_asyncs)
            # Ensure it has a unique name
            if iobridge:
                assignUniqueName(input_signal, iobridge.input_signals)
            # Make sure it will still link by alias back to the original
            input_alias = getAlias(signal)
            input_signal[1]['MARTeConfig']['Alias'] = input_alias
            # Set the output signal to the async bridge
            out_signal = copy.deepcopy(input_signal)
            # Now create our output_signal and set it to the bridge
            setDatasource(out_signal, 'LoggingAsyncBridge')
            removeKeysFromConfig(out_signal, ['Alias'])
            # Now we're ready, add to our IOGAM to Async Bridge
            io_async_gam = consolidate(self.io_asyncs,'IOGAM',iobridge_name,
                                        [input_signal],[out_signal])
            # Make sure we keep track of our async IO's
            if io_async_gam not in self.io_asyncs:
                self.io_asyncs.append(io_async_gam)
            if io_async_gam not in new_functions:
                new_functions.append(io_async_gam)
            # Now we know what the signal will be on the primary thread of the async bridge
            # Now create the logging of this signal in the primary thread
            tolog = copy.deepcopy(out_signal)
            assignUniqueName(tolog, self.loggingintoio.input_signals)
            setDatasource(tolog, 'LogGAMSource')
            consolidate(state.threads.objects[0].functions,
                        'IOGAM','+async_sim_io',
                        [out_signal],[tolog])

            if self.type_db.isFundamental(input_signal[1]['MARTeConfig']['Type']):
                # Add to our log

                self.loggingintoio.input_signals += [tolog]

                tolog = copy.deepcopy(tolog)
                setDatasource(tolog, getname(self.filewriter))

                self.loggingintoio.output_signals += [tolog]
                tolog = copy.deepcopy(tolog)
                del tolog[1]['MARTeConfig']['DataSource']
                self.filewriter.input_signals += [tolog]
            else:
                # Unflatten and add to log
                MARTe2Application._unflattenLog(tolog,
                                                self.type_db,
                                                self.logging_iogam,
                                                self.loggingintoio,
                                                self.filewriter,
                                                'LogGAMSource')

        return new_functions

    def buildLog(self):
        """Build a datalogger IO and log signals from our application given user input
        """
        # Now that everything exists as it should, we now need to create a
        # method of logging every signal ever created.
        # First we need to track every signal that is produced, if it is not
        # a part of our constant or misc DDB's
        # We should start by creating a IOGAM called loggingGAM which feeds
        # from our logDDB into our our FileWriter
        # We should also create our FileWriter as a reference, only one IOGAM
        # can write to this FileWriter, hence our approach
        #
        # When we move signals into our logDDB we should check if it already
        # exists as a signal name duplicate, if so, generate unique name

        self.additional_datasources += [self.asyncbridge, self.filewriter]
        self.functions += [self.logging_iogam, self.loggingintoio]
        for state in self.states:
            if len(state.threads.objects) > 0:
                state.threads.objects[0].functions += self.iogams
            for thread_index, thread in enumerate(state.threads.objects):
                new_functions = []
                # if we are not in thread 0 we must create an AsyncBridge for this
                # thread if not already existing and send this signal through said bridge
                # Once we have all these signals into thread 0, we use an IOGAM for each
                # state to transfer these into our log DDB and then add these to our
                # loggingIOGAM and filewriter

                for function in thread.functions:
                    if function in self.iogams or function in self.io_asyncs:
                        continue
                    if hasattr(function, 'isSimulation') and function.isSimulation:
                        continue
                    for output_signal in function.output_signals:
                        if getDatasource(output_signal) not in self._internal_datasources:
                            new_functions += self._logSignal(output_signal,
                                                              thread_index, state, thread)
                thread.functions += new_functions

    def writeToConfig(self, out=None):
        ''' Write our application out and return as a string '''
        # Fix any breaks in the config automatically
        self.sanitize()
        self.removeUnused()
        if not out:
            out = marteconfig.StringConfigWriter()

        for piece in self.externals:
            if piece:
                piece.write(out)

        #Adding capability to have non application and non state machine
        # entities in our configuration, for instance, the HTTPObjectBrowser
        for obj in self.objects:
            obj.write(out)

        out.startClass(f'${self.app_name.replace("$","")}', 'RealTimeApplication')

        out.startClass('+Functions', 'ReferenceContainer')

        for i in self.functions:
            i.write(out)

        out.endSection('+Functions')

        out.startClass('+Data', 'ReferenceContainer')

        if not len([a for a in self.additional_datasources if isinstance(a, GAMDataSource)]) == 0:
            out.writeNode('DefaultDataSource', self.default_data_source)

        for i in self.additional_datasources:
            i.write(out)

        out.endSection('+Data')

        out.startClass('+States', 'ReferenceContainer')

        for i in self.states:
            i.write(out)

        out.endSection('+States')

        for i in self.internals:
            i.write(out)

        out.endSection(f'${self.app_name.replace("$","")}')

        return str(out) + "\n"

    def sanitize(self):
        ''' Resanitize an application between its state, 
        threads functions and it's functions definitions.'''
        self.functions = []
        for state in self.states:
            for thread in state.threads.objects:
                for function in thread.functions:
                    if function not in self.functions: # Avoid duplications
                        self.functions.append(function)


    def removeUnused(self):
        ''' Removes empty and unused objects such as:
        - An IOGAM with no inputs or outputs
        - An Async bridge with no IOGAMs writing to it or from it
        - A GAM DataSource with no signals defined throughout the application into it. '''
        self.sanitize()
        # If a GAM Datasource has no values assigned to it - we should remove it
        gam_sources = [(a.configuration_name.lstrip('+'), a) for
                       a in self.additional_datasources if isinstance(a, GAMDataSource)]
        for datasource, gam_object in gam_sources:
            if not any(any(output_signal[1]['MARTeConfig']['DataSource'] == datasource for
                           output_signal in function.output_signals) for
                           function in self.functions):
                # We need to remove this
                self.additional_datasources.remove(gam_object)

        # If an IOGAM has no inputs/outputs, it should be removed,
        # if it has no inputs, sanity is all but lost:
        for function in self.functions:
            if isinstance(function, IOGAM):
                if len(function.input_signals) == 0 or len(function.output_signals) == 0:
                    # Delete the function from both our functions and
                    # whereever it's used in threads/states
                    for state in self.states:
                        for thread in state.threads.objects:
                            thread.functions = [a for a in thread.functions if not a == function]

        self.sanitize()

        # As above, if an async bridge exists without any
        # reading/writing signals the heap allocation will fail
        asyncbridges = [a for a in self.additional_datasources if isinstance(a, AsyncBridge)]
        for bridge in asyncbridges:
            if not any(any(input_signal[1]['MARTeConfig']['DataSource'] == getname(bridge) for
                           input_signal in function.input_signals) for
                           function in self.functions) and not any(
                any(output_signal[1]['MARTeConfig']['DataSource'] == getname(bridge) for
                    output_signal in function.output_signals) for function in self.functions):

                # Remove the bridge as it is unused
                self.additional_datasources.remove(bridge)
