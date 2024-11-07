'''
This module provides capability for a user to convert a MARTe2 written binary file into a human
readable CSV file.
'''

import struct
from typing import Type, Tuple, Iterable
from functools import lru_cache
import itertools
from dataclasses import dataclass


class Bin2CSVError(Exception):
    """Generic exception for all errors"""

@dataclass
class TypeDescriptor:
    ''' Basic descriptor of a type in it's binary format '''
    code: int
    name: str
    struct_format: str
    size: int

@dataclass
class SignalDescriptor:
    ''' Basic Descriptor of a signal in it's binary format '''
    name: str
    type_descr: TypeDescriptor
    elements: int

    def format(self):
        ''' Format the descriptor into string representation '''
        if self.elements == 1:
            return self.type_descr.struct_format
        return f'{self.elements:d}{self.type_descr.struct_format}'

standard_type_descriptors = {
    t.code: t for t in (
        TypeDescriptor(2048, 'int32', 'i', 4),
        TypeDescriptor(2052, 'uint32', 'I', 4),
        TypeDescriptor(2056, 'float32','f', 4),
        TypeDescriptor(4100, 'uint64', 'Q', 8),
        TypeDescriptor(4104, 'float64','d',8),
        TypeDescriptor(1028, 'uint16', 'H', 2),
        TypeDescriptor(516, 'uint8', 'B', 1),
        TypeDescriptor(512, 'int8', 'b', 1)
    )
}


class RowInterpreter:
    """Class using the descriptors built from the start of a MARTe2 binary
    FileWriter output to interpret the bytes from the rest of the file, with
    the ability to output what it interprets for storage in a CSV. If the CSV
    format is expected to be compatible outside of the MARTe2 world, see also
    the `StandardCSVRowInterpreter` class.
    """

    def __init__(self, *signal_descriptors: Tuple[SignalDescriptor],
                 delimiter: str = ',', struct_endianity_char: str = '<'):
        """RowInterpreter constructor.

        Constructor parameters are stored in private fields because the rowSize
        and rowFormat results are cached and will be invalid if these fields
        are edited after they have been called the first time.
        """
        self._signal_descriptors = signal_descriptors
        self._delimeter = delimiter
        self._struct_endianity_char = struct_endianity_char

    @lru_cache(maxsize=None) # pylint: disable=W1518
    def rowSize(self) -> int:
        """Return the number of bytes that one row of data would require in the
        MARTe2 binary file.
        """
        return sum(signal.type_descr.size * signal.elements for
                   signal in self._signal_descriptors)

    @lru_cache(maxsize=None) # pylint: disable=W1518
    def rowFormat(self) -> str:
        """Return the `struct` library format string used to unpack one row."""
        return self._struct_endianity_char + ''.join(signal.format() for
                                                     signal in self._signal_descriptors)

    def headerRow(self) -> str:
        """Return the first row of an equivalent CSV file format, containing
        column names.
        """
        column_names = [f'{signal.name} ({signal.type_descr.name})[{signal.elements}]' for
                        signal in self._signal_descriptors]
        signal_names_string = self._delimeter.join(column_names)
        return f'#{signal_names_string}\n'

    def binToCsvRow(self, binary_data: bytes) -> str:
        """Return the CSV file formatted data for a row's worth of binary data.
        This will raise an exception if the provided data does not match in
        size with the descriptors this RowInterpreter was constructed with.
        """
        return self.valuesToCsvRow(self.binToValues(binary_data))

    def binToValues(self, binary_data: bytes) -> Iterable:
        """Return the values in Python types for a row's worth of binary data.
        This will raise an exception if the provided data does not match in
        size with the descriptors this RowInterpreter was constructed with.
        """
        return struct.unpack(self.rowFormat(), binary_data)

    def valuesToCsvRow(self, row_values: Iterable) -> str:
        """Return the CSV file formatted data for a row's data as Python types.
        This will raise an exception if the provided data does not match in
        number of items with the descriptors this RowInterpreter was constructed
        with.
        """
        row_value_generator = (i for i in row_values)
        csv_value_strings = []
        signals = [(signal, itertools.islice(row_value_generator, signal.elements)) for
                   signal in self._signal_descriptors]
        for signal, signal_iterable in signals:
            if signal.elements == 1:
                csv_value_strings.append(str(next(signal_iterable)))
            else:
                inner_values = ' '.join(str(value) for value in signal_iterable)
                csv_value_strings.append(f'{{{inner_values}}}')
        return self._delimeter.join(csv_value_strings) + '\n'


class StandardCSVRowInterpreter(RowInterpreter):
    """A variant of the `RowInterpreter` class which writes a more standardised
    CSV format. The difference is that signals which are arrays in MARTe2 will
    be separated into individual signals, whereas the `RowInterpreter` class
    follows the MARTe2 convention of encasing the array values in curly braces
    and allocating them only a single header item.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def valuesToCsvRow(self, row_values: Iterable) -> str:
        return self._delimeter.join(str(value) for value in row_values) + '\n'

    def headerRow(self) -> str:
        signal_names_string = self._delimeter.join(self._headerItem(signal) for
                                                   signal in self._signal_descriptors)
        return f'#{signal_names_string}\n'

    def _headerItem(self, signal: SignalDescriptor) -> str:
        if signal.elements == 1:
            return f'{signal.name} ({signal.type_descr.name})'
        indices = range(signal.elements)
        signal_desc = f'({signal.type_descr.name}[{signal.elements}])'
        index_strings = [f'{signal.name}[{i}] {signal_desc}' for i in indices]
        return self._delimeter.join(index_strings)


class Bin2CSV():
    '''
    The main entrypoint to convert a MARTe2 binary log produced by the FileWriter datasource
    to a csv file.
    See RowInterpretator and StandardRowInterpretator for explanation of marte2_csv
    '''
    def __init__(self,
        bin_path: str = 'log.bin',
        csv_path: str = 'log_0.csv',
        marte2_csv: bool = True
    ):
        self.bin_path = bin_path
        self.csv_path = csv_path
        self.marte2_csv = marte2_csv

    def interpreterClass(self) -> Type[RowInterpreter]:
        ''' Get our declared interpretator'''
        if self.marte2_csv:
            return RowInterpreter
        return StandardCSVRowInterpreter

    @lru_cache(maxsize=None) # pylint: disable=W1518
    def unpackStruct(self, name_size, fin):
        ''' Unpack the signal '''
        return struct.unpack('<H' + str(name_size) + 'sI', fin.read((name_size+6)))

    def main(self):
        """Convert the binary file into CSV"""
        with open(self.bin_path, 'rb') as fin:
            nsignals, = struct.unpack('<I', fin.read(4))

            name_size = 32

            signals = []
            for _ in range(nsignals):
                signal_code, signal_name, signal_elements = self.unpackStruct(name_size, fin)

                signal_name = signal_name.rstrip(b'\x00').decode('utf-8')
                try:
                    signal_type = standard_type_descriptors[signal_code]
                except KeyError:
                    msg = f'Unknown TypeDescription code: {signal_code} for signal {signal_name}'
                    raise Bin2CSVError(msg) # pylint: disable=W0707

                signals.append(SignalDescriptor(signal_name, signal_type, signal_elements))

            interpreter = self.interpreterClass()(*signals)

            with open(self.csv_path, 'w', encoding='utf-8') as fout:
                fout.write(interpreter.headerRow())

                while True:
                    raw_row = fin.read(interpreter.rowSize())
                    if len(raw_row) < interpreter.rowSize():
                        if raw_row:
                            msg = f'Reached EOF with partial row: {len(raw_row)} leftover bytes'
                            raise Bin2CSVError(msg)
                        break

                    fout.write(interpreter.binToCsvRow(raw_row))
