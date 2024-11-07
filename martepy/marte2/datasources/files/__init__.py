''' Import all the available file datasources in one go '''

from martepy.marte2.datasources.files.writer import FileWriter
from martepy.marte2.datasources.files.reader import FileReader
from martepy.marte2.datasources.files.file_datasources import RFileReader, RFileWriter

__all__ = [
        'FileWriter',
        'FileReader',
        'RFileReader',
        'RFileWriter'
]
