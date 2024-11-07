"""extra_functions.py contains additional useful functions"""


class ConfigGeneratorError(Exception):
    """Generic exception for errors encountered during configuration generation"""

def getname(object_cls):
    ''' Return the name of an object, omitting the + '''
    return object_cls.configuration_name.lstrip('+')

def normalizeSignal(signal):
    ''' Checks that a signal has elements and dimensions and removes these if not
    otherwise it ensures they are both set. It also handles defaults in this context,
    if a default is with zero dimensions/elements, it will remove the {} encapsulation
    of default.'''
    if 'NumberOfDimensions' in signal['MARTeConfig']:
        if 'NumberOfElements' in signal['MARTeConfig']:
            dimensions = signal['MARTeConfig']['NumberOfDimensions']
            elements = signal['MARTeConfig']['NumberOfElements']
            if int(dimensions) == 1 and int(elements) == 1:
                del signal['MARTeConfig']['NumberOfDimensions']
                del signal['MARTeConfig']['NumberOfElements']

    if 'NumberOfElements' not in signal['MARTeConfig'].keys():
        if 'Default' in signal['MARTeConfig'].keys():
            current_default = str(signal['MARTeConfig']['Default'])
            signal['MARTeConfig']['Default'] = current_default.lstrip('{').rstrip('}')

    return signal

def findIndexByDictKey(list_i, key, value):
    ''' This will search through a list of dictionaries and find a key value matching pair
    # this is intended for where dictionaries are identified by a unique key/value.'''
    for index, dictionary in enumerate(list_i):
        if dictionary.get(key).lstrip('+') == value:
            return index
    return -1

def isint(value):
    ''' Is our value a valid integer? '''
    try:
        int(value)
        return True
    except ValueError:
        return False

def isfloat(value):
    ''' Is our value a valid float value? '''
    try:
        float(value)
        return True
    except ValueError:
        return False

def calculateStackSize(signals):
    """:param signals: inputs and outputs
    :type signals: list[tuple[str, dict[]]]

    :return stacksize: total size of variable types
    :rtype: int

    Given a function, how big is the input and output signal stack size of the variables
    """
    types = {"int8": 1, "int16": 2, "int32": 4, "int64": 8,
             "uint8": 1, "uint16": 2, "uint32": 4, "uint64": 8,
             "float32": 4, "float64": 8}
    stacksize = 0
    for signal in signals:
        signal_type = signal[1]["MARTeConfig"]["Type"]
        num = 1
        if 'NumberOfElements' in signal[1]["MARTeConfig"].keys():
            num = int(signal[1]["MARTeConfig"]['NumberOfElements'])
        stacksize = stacksize + types[signal_type] * num
    return stacksize

def form(sig_name, type_, num=None, datasource='DDB0', alias=None, default=None):
    """:param str sig_name: signal name
    :param str type_: signal type
    :param int num: number of elements
    :param str datasource: MARTe datasource
    :param str alias: signal alias

    :return: output signals formatted
    :rtype: list[tuple[str, dict[]]]

    Formats the input/output signals
    """
    if alias is None:
        alias = sig_name
    formatted = [(sig_name, {'MARTeConfig': {'DataSource': datasource,
                                             'Type': type_,
                                             'Alias': alias}})]
    if default:
        formatted[0][1]['MARTeConfig']['Default'] = default
    if num:
        formatted[0][1]['MARTeConfig']['NumberOfElements'] = num
    return formatted
