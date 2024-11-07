"""gam_functions.py contains functions that create or maniuplate gams"""

# Is necessary to import all for consolidate function, don't know what GAM the user will
# consolidate
from martepy.marte2.gams import * # pylint: disable=W0614
from martepy.marte2.qt_functions import generateUniqueName

def assignUniqueName(signal: tuple, signals_list: list):
    ''' Ensures that a signal is uniquely named compared to a list of signals '''
    if any(signal_item[0] == signal[0] for signal_item in signals_list):
        existing_names = [a[0] for a in signals_list]
        alias_name = getAlias(signal)
        signal[1]['MARTeConfig']['Alias'] = alias_name
        signal = (generateUniqueName(existing_names, signal[0]), signal[1])
    return signal

def removeKeysFromConfig(signal: tuple, keys: list):
    ''' Safely Delete keys from a signal '''
    for key in keys:
        if key in signal[1]['MARTeConfig'].keys():
            del signal[1]['MARTeConfig'][key]

def getKeyAttribute(signal, key):
    ''' Given a specific MARTe2Config key, retrieve the value '''
    return signal[1]['MARTeConfig'][key]

def setKeyAttribute(signal, key, value):
    ''' Set a attribute of the MARTe Config'''
    signal[1]['MARTeConfig'][key] = value

def addDimensions(signal: tuple):
    ''' If a signal does not contain elements or dimensions, add them '''
    if 'NumberOfDimensions' not in signal[1]['MARTeConfig'].keys():
        signal[1]['MARTeConfig']['NumberOfDimensions'] = '1'

    if 'NumberOfElements' not in signal[1]['MARTeConfig'].keys():
        signal[1]['MARTeConfig']['NumberOfElements'] = '1'

def addAlias(signal: tuple):
    ''' If an Alias is not set, set it to the basic name '''
    if 'Alias' not in signal[1]['MARTeConfig'].keys():
        alias_name = getAlias(signal)
        signal[1]['MARTeConfig']['Alias'] = alias_name

def getGamByName(name: str, function_list):
    ''' Returns a GAM based on the name in a given function list '''
    def getname(value):
        return value.configuration_name.lstrip('+')
    return next((a for a in function_list if getname(a) == name), None)

def getAlias(signal_key):
    ''' Return the alias of a signal '''
    if 'Alias' in list(signal_key[1]['MARTeConfig'].keys()):
        return signal_key[1]['MARTeConfig']['Alias']
    return signal_key[0]

def setDatasource(signal, datasource):
    ''' Simplification of setting a signals datasource '''
    signal[1]['MARTeConfig']['DataSource'] = datasource

def getDatasource(signal):
    ''' Simplification of getting a signals datasource '''
    return signal[1]['MARTeConfig']['DataSource']


def isMatchingSignal(signal, other_signal):
    ''' Here we say a signal is the same if it has the same alias and 
    datasource where the signal exists.'''
    if not getAlias(signal) == getAlias(other_signal):
        return False
    if not getDatasource(signal) == getDatasource(other_signal):
        return False
    return True

def findSignalInFunctionList(signal, functions):
    ''' Will return the signal that matches a given signal in a list of functions '''
    try:
        return next(
            producer
            for function in functions
            for producer in function.output_signals
            if isMatchingSignal(producer, signal)
        )
    except StopIteration:
        return None

def getParameterName(parameter_name: str):
    """This takes the serialized name of a parameter and returns it's attribute name"""
    return parameter_name.lower().replace(' ','_')

def consolidate(thread_0_functions, gam_type, config_name, inputs=[], outputs=[],prepend=False): # pylint: disable=R0912
    """:param thread_0_functions: list of references to rtcc1blocks specific class
    :type thread_0_functions: list[]
    :param str gam_type: type of gam
    :param str config_name: SDN config
    :param inputs: input signal
    :type inputs: list[tuple[str, dict[]]]
    :param outputs: output signal
    :type outputs: list[tuple[str, dict[]]]

    :return gam: marte2 gam
    :rtype: marte2 gam

    Add a GAM which creates a constant signal or reads a signal from SDN
    but check first if a similarly named GAM of that type exists, and if it
    does simply add the signals provided to this method into the
    pre-existing GAM.
    """
    if not any(
        a.class_name == gam_type and a.configuration_name == config_name
        for a in thread_0_functions
    ):
        # First actual IOGAM request for any SDN signal so let's add it.
        gam = globals()[gam_type]
        if gam_type == "ConstantGAM":
            if prepend:
                thread_0_functions.insert(0,gam(configuration_name=config_name, output_signals=[]))
            else:
                thread_0_functions.append(gam(configuration_name=config_name, output_signals=[]))
        elif prepend:
            thread_0_functions.insert(0,
                gam(configuration_name=config_name, input_signals=[], output_signals=[])
            )
        else:
            thread_0_functions.append(
                gam(configuration_name=config_name, input_signals=[], output_signals=[])
            )
    index = next(
        i for i, d in enumerate(thread_0_functions) if d.configuration_name == config_name
    )
    gam = thread_0_functions[index]
    if gam_type != "ConstantGAM": # pylint: disable=R1702
        if gam_type != "IOGAM":
            for inputsig, output in zip(inputs, outputs):
                # Here we test that if an output signal is unique, but the input signal is not
                # We still add the signal but give the input a unique signalname as well.
                # This is useful when we're assuming here that the output signal is a converted
                # signal type and the user would like to convert the same signal into multiple
                # formats this simplifies that process for them by maintaining the alias whilst
                # giving it a different signal name.
                if not any(a == output for a in gam.output_signals):
                    # Input signal does not yet exist, we can also presume output doesn't either.
                    # Let's add it - then reinsert our converting GAM to the index, replacing it.
                    # Check that our input signal name is unique and if not, make it unique
                    if any(a[0] == inputsig[0] for a in gam.input_signals):
                        i = 1
                        while(any(inputsig[0] + "_" + str(i) == a[0] for a in gam.input_signals)):
                            i = i + 1
                        inputsig = (inputsig[0] + "_" + str(i),inputsig[1])
                    gam.input_signals.append(inputsig)
                    gam.output_signals.append(output)
        else:
            for a in inputs:
                gam.input_signals.append(a)
            for a in outputs:
                gam.output_signals.append(a)
    else:
        for output in outputs:
            if not any(a == output for a in gam.output_signals):
                # Input signal does not yet exist, we can also presume output doesn't either.
                # Let's add it - then reinsert our convertin GAM to the index, replacing it.
                gam.output_signals.append(output)
    thread_0_functions[index] = gam
    return gam
