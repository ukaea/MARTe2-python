"""This class acts as a storage database to store types and
packet definitions for later use in the application.
The packet definitions are also simply types however in this
context they could be SDN/UDP inputs/outputs to your system.

Types are stored in RDF format for the best computational storage possible.
"""

import re
import os
import shutil
from string import Template
import getpass
import copy
from datetime import datetime

from martepy.marte2.sorter import sortHeaders

STRUCT_PATTERN = re.compile(r'.*?typedef\s+struct\s*(\w*)\s*{([^}]*)}\s*(\w*)\s*;.*', re.DOTALL)
VERSION_PATTERN = r"_(\d+_\d+)\.h$"

class TypeException(Exception):
    """Exceptions to be raised specific to the type database"""

# Define field class
class Field: # pylint: disable=R0903
    ''' Type member definition '''
    def __init__(self, name, field_type, noelements=1, comment = ''):
        self.name = name
        self.type = field_type
        self.noelements = noelements
        self.comment = comment

    def __eq__(self, other):
        if not isinstance(other, Field):
            return False
        return (self.comment == other.comment and
                self.type == other.type and
                self.name == other.name and
                self.noelements == other.noelements)

# Define type class
class Type:
    ''' Class representation of a type '''
    def __init__(self, name, fundamental=False, file='', version='1_0', comments=''):
        self.name = name
        self.fundamental = fundamental
        self.fields = []
        self.file = file
        self.version = version
        self.comments = comments

    def addField(self, field):
        ''' Add a field '''
        self.fields.append(field)

    def __eq__(self, other):
        if not isinstance(other, Type):
            return False
        return (self.file == other.file and
                self.version == other.version and
                self.fundamental == other.fundamental and
                self.name == other.name and
                self.fields == other.fields)


class Constant(): # pylint: disable=R0903
    ''' Definition for any constant values - usually found in interpretting a type where
    the type has an array element and the array size is defined by a constant. '''
    def __init__(self, name, value, comments=''):
        self.name = name
        self.value = value
        self.comments = comments

class TypeDBv2():
    ''' The Type Database class '''
    def __init__(self):
        # In it's memory state it's best to store the data
        # in dictionary format as it gives us an O(1) efficieny
        # i.e. as the datastore increases in size, retrieving types does not
        # However since we store the types as objects in files then
        # That itself should have a O(N) efficiency.
        # This stores types
        self.types = {}
        # This stores definitions, mainly just useful as it allows multiple files
        # to use a shared set of definitions, as long as we parse those defining files first
        self.definitions = {}
        self.template_path = os.path.join(os.path.dirname(__file__), 'templates')

    def __eq__(self, other):
        if not isinstance(other, TypeDBv2):
            return False
        return self.types == other.types


    def _evaluateExpression(self, expression, constants):
        ''' Evaluate an expression in C++ '''
        def applyOperator(operators, values):
            ''' Apply C++ operations on a number '''
            while operators and len(values) > 1:
                operator = operators.pop()
                right = values.pop()
                left = values.pop()

                if operator == '<<':
                    values.append(left << right)
                elif operator == '>>':
                    values.append(left >> right)

        def isHexadecimal(s):
            ''' Evaluate whether it is a hexadecimal number '''
            try:
                # Attempt to convert the string to an integer with base 16
                int(s, 16)
                return True
            except ValueError:
                return False

        def parseTokens(tokens):
            ''' Token parser for interpretting a expression '''
            operators = []
            values = []

            for token in tokens:
                if token in constants:
                    values.append(constants[token].value)
                elif token == '(':
                    operators.append(token)
                elif token == ')':
                    while operators and operators[-1] != '(':
                        applyOperator(operators, values)
                    operators.pop()  # Remove the '('
                elif token in ['<<', '>>']:
                    while operators and operators[-1] in ['<<', '>>']:
                        applyOperator(operators, values)
                    operators.append(token)
                elif token.isdigit():
                    values.append(int(token))
                elif isHexadecimal(token):
                    values.append(int(token, 16))
                else:
                    raise ValueError(f"Invalid token: {token}")

            applyOperator(operators, values)

            return values[0] if not operators else values

        # Tokenize the expression
        tokens = re.findall(r'\b(?:<<|>>|\w+|\(|\))\b', expression)

        if not tokens:
            raise ValueError()
        # Evaluate the expression recursively
        result = parseTokens(tokens)

        return result

    def _getVersion(self, filepath):
        ''' Based on a files name, derive the version '''
        match = re.search(VERSION_PATTERN, os.path.basename(filepath))
        if match:
            return match.group(1)
        return '1_0'

    def _cleanContent(self, header_content):
        ''' Removes commented lines from the overall content '''
        filtered_list = [item for item in header_content if
                         not (item.startswith('#') or item == '\n')]
        overall_content = ''.join(filtered_list)
        return overall_content

    def _evaluateHeaderDefs(self, header_content):
        ''' This function evaluates any constant or numeric definitions in header contents '''
        for line in header_content:
            pattern = re.compile(r'^#define\s+(\w+)\s+(\S+)(.*)$')
            match = pattern.match(line)

            if match is None:
                continue

            if match:
                value = self._evaluateExpression(match.group(2), self.definitions)
                self.definitions[match.group(1)] = Constant(match.group(1), # name
                                                            value, # value
                                                            match.group(3)) # additional string

    def _parseHeader(self, header_content, file=''):
        ''' Read and parse a header files contents to a type '''
        # Regular expressions to match typedef structs
        self._evaluateHeaderDefs(header_content)

        # So now we have definitions captured, we can compute structs now
        # Let's start by driving efficiency by removing lines that start with #
        # Then let's squash our lines back together with any new line definitions,
        # this will help us get rid of comment fields later
        # Minimizing the content will help
        # Now let's first find all our typedefs

        matches = STRUCT_PATTERN.findall(self._cleanContent(header_content))

        def cleanString(input_string):
            ''' Clean our string line of any new lines and spaces unnecessarily '''
            # Remove new lines
            without_newlines = input_string.replace('\n', ' ')

            # Reduce multiple spaces to a single space
            without_multiple_spaces = re.sub(r'\s+', ' ', without_newlines)

            return without_multiple_spaces

        def removeCcomments(input_string):
            ''' Remove any C/C++ Comments '''
            pattern = r'\/\*[\s\S]*?\*\/'
            cleaned_string = re.sub(pattern, '', input_string)
            return cleaned_string

        def captureCcomments(input_string):
            ''' Capture the C/C++ Comments '''
            pattern = r'\/\*([\s\S]*?)\*\/'
            matches = re.findall(pattern, input_string)
            if matches:
                merged_string = '.'.join(matches)
                return merged_string
            return ''

        version = self._getVersion(file)
        # Finally create all our types in the header and update our dictionaries
        for match in matches:
            # This gets all our typedefs, for this level it just extracts the string for us
            # and the name if declared before or after the struct definition
            name = match[0] if match[2] == '' else match[2]
            new_type = Type(name, file=file, version = version)
            # Remove duplicate spaces and new line content and get us a flat string for our
            # definition only seperated by what we know
            # Now get our types
            # clean typedef content and split by ;
            for type_partial in cleanString(match[1]).split(';'):
                matches = re.findall(r'\s(\w+)\s(\w+)(?:\[(\w+)\])?\s*',
                                     removeCcomments(type_partial))
                if not matches:
                    continue
                noelements = 1 if matches[0][2] == '' else matches[0][2]
                try:
                    noelements = int(noelements)
                except ValueError:
                    # This means we have a string definition
                    try:
                        noelements = self._evaluateExpression(noelements,
                                                               self.definitions)
                    except ValueError as exc:
                        raise ValueError(f'''could not evaluate string of number of\n elements
 for field {matches[0][0]}, string is: {noelements}''') from exc
                type_def = matches[0][0].lower()
                type_def = 'uint32' if type_def == 'bitfield' else type_def
                type_def = 'float32' if type_def == 'float' else type_def
                new_type.fields.append(Field(matches[0][1],type_def,
                                             noelements,captureCcomments(type_partial)))
            self.types[name] = new_type

    def isFundamental(self, type_name):
        ''' Check if a given type is a fundamental type of MARTe2 '''
        return type_name.lower() in ["uint32", "uint64", "float32", "float64",
                                     "uint8", "int32", "int64", "int8", "int16"]

    def loadDb(self, directory_path):
        ''' Load a directory of types into the database '''
        header_paths = sortHeaders(directory_path)

        for header_path in header_paths:
            self.loadFile(header_path)

    def loadFile(self, file_path):
        ''' Load a type file '''
        with open(file_path, 'r', encoding='utf-8') as header_file:
            header_content = header_file.readlines()
            self._parseHeader(header_content, file=file_path)

    def getTypeByName(self, type_name):
        ''' Get a type based on it's name '''
        try:
            return self.types[type_name]
        except Exception as exc:
            raise TypeException(type_name) from exc

    def saveType(self, typedef, file_path):
        ''' Save the type to file '''
        self._updateStructInFile(file_path, typedef)

    # Function to generate the struct definition as a string
    def _generateStructDefinition(self, type_info):
        ''' Generate the struct definition for a type '''
        struct_def = "typedef struct {\n"
        for field in type_info.fields:
            if int(field.noelements) > 1:
                struct_def += f"    {field.type} {field.name}[{field.noelements}];\n"
            else:
                struct_def += f"    {field.type} {field.name};\n"
        struct_def += f"}} {type_info.name};"
        return struct_def

    # Function to update the struct in the file
    def _updateStructInFile(self, file_path, type_info):
        ''' Do an inplace saving of our type definition '''
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Regex to find the struct definition
        re_str = rf"typedef\s+struct\s*{{[^}}]*}}\s*{re.escape(type_info.name)}\s*;"
        struct_pattern = re.compile(re_str, re.DOTALL)

        # Generate the new struct definition
        new_struct_def = self._generateStructDefinition(type_info)

        # Replace the old struct with the new one
        updated_content = struct_pattern.sub(new_struct_def, content)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)

    def toLibrary(self, output_path):
        ''' Output our type database as it's C++ compilable MARTe2 format '''
        paths= ''
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        for packet_name, type_def in self.types.items():
            path = self._createSubfolder(output_path, packet_name)
            self._write(self._create(self.template_path, packet_name,
                                     type_def, 'cpp', self._cppSubstituteDict),
                                     path, f'{packet_name}.cpp')
            self._write(self._create(self.template_path, packet_name,
                                     type_def, 'h', self._hSubstituteDict),
                                     path, f'{packet_name}.h')
            self._write(self._create(self.template_path, packet_name,
                                     type_def, 'makefile', self._makefileSubstituteDict),
                                     path, 'Makefile.inc')
            self._write('include Makefile.inc', path, 'Makefile.gcc')
            if paths:
                paths += '        '  # adding indentation
            paths += f'{packet_name}.x\\\n'
        self._write(self._create(self.template_path, paths, '', 'root_makefile',
                                 self._rootSubstituteDict), output_path, 'Makefile.inc')
        self._write('export TARGET=x86-linux\n\ninclude Makefile.inc',
                    output_path, 'Makefile.x86-linux')
        return paths

    def _createSubfolder(self, output_path, packet_name) -> str:
        """Create the subfolder for the packet's type definition."""
        if not os.path.exists(path := os.path.join(output_path, packet_name)):
            os.mkdir(path)
        return path

    def _create(self, template_path, packet_name, type_def, extension, substitute_dict) -> str:
        """Create the file contents."""
        with open(os.path.join(template_path, f'{extension}_template.txt'), 'r',
                  encoding='utf-8') as fhand:
            src = Template(fhand.read())
            result = src.substitute(substitute_dict(packet_name, type_def))
            result = result.replace('£', '$').replace('Â','')
        fhand.close()
        return result

    def _write(self, definition, path, filename) -> None:
        """Write the file."""
        with open(os.path.join(path, filename), 'w', encoding='utf-8') as fhand:
            fhand.write(definition)
        fhand.close()

    def _cppSubstituteDict(self, packet_name, type_def) -> dict:
        """Create the substitution dictionary for the packet."""
        return {
            'type_name': f'{packet_name}Cls',
            'type_def': self._extractCppDef(packet_name, type_def),
            'header_name': f'{packet_name}.h',
            'file_name': f'{packet_name}.cpp',
        }

    def _hSubstituteDict(self, packet_name, type_def) -> dict:
        """Create the substitution dictionary for the packet."""
        return {
            'type_name_upper': f'{packet_name.upper()}_H_',
            'struct_def': self._extractHDef(packet_name, type_def),
            'file_name': f'{packet_name}.h',
        }

    def _makefileSubstituteDict(self, packet_name, _) -> dict:
        """Return the substitution dictionary for the library makefile."""
        return {
            'type_name_x': f'{packet_name}.x',
            'type_name': packet_name,
        }

    def _rootSubstituteDict(self, packet_name, _) -> dict:
        """Return the substitution dictionary for the root level makefile."""
        return {'type_list': packet_name}

    def _extractCppDef(self, packet_name, type_def) -> str:
        """Extract the cpp type definition."""
        declaration = ''
        entries = ''
        for field in type_def.fields:
            declaration += f'''DECLARE_CLASS_MEMBER({packet_name}, {field.name},
 {field.type}, "[{field.noelements}]", "");\n'''
            entries += f'&{packet_name}_{field.name}_introspectionEntry, '
        declaration += f'''static const MARTe::IntrospectionEntry*
 {packet_name}StructEntries[] = {{  {entries}0 }};\n'''
        declaration += f'DECLARE_STRUCT_INTROSPECTION({packet_name}, {packet_name}StructEntries)\n'
        return declaration

    def _extractHDef(self, packet_name, type_def) -> str:
        """Extract the header type definition."""
        declaration = f'    struct {packet_name} {{\n'
        for field in type_def.fields:
            declaration += f'        {field.type} {field.name};\n'
        declaration += '    };\n'
        return declaration

    def updateDb(self, type_db_filepath):
        ''' For each type, save them '''
        # Go through each type and save it
        for type_name, type_def in self.types.items():
            self.saveTypeDef(type_db_filepath, type_name, type_def)

    def incrementVersion(self, version):
        ''' Increment the version number of our type'''
        # Split the version string into major and minor parts
        major, minor = version.split('_')

        # Convert the minor part to an integer and increment it
        minor = int(minor) + 1

        # Reconstruct the version string
        new_version = f"{major}_{minor}"

        return new_version

    def updateFileVersion(self, file_path, new_version):
        ''' Update the version def in the file contents '''
        # Regular expression pattern to match the version in the filename
        pattern = r"_(\d+_\d+)\.h$"

        # Search for the pattern in the filename
        match = re.search(pattern, file_path)

        if match:
            current_version = match.group(1)

            # Create the new filename by replacing the old version with the new version
            new_file_path = file_path.replace(f"_{current_version}.h", f"_{new_version}.h")

            # Create the archive folder path
            archive_folder = os.path.join(os.path.dirname(file_path), "archive")

            # Ensure the archive folder exists
            os.makedirs(archive_folder, exist_ok=True)

            # Create the archived file path
            archived_file_path = os.path.join(archive_folder, os.path.basename(file_path))

            # Move the old version file to the archive folder
            shutil.move(file_path, archived_file_path)

            # Rename the file with the new version
            with open(archived_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(new_file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return new_file_path, archived_file_path
        return file_path

    def saveTypeDef(self, type_db_filepath, type_name, type_value):
        ''' Save a given type definition to file '''
        if not os.path.exists(self.types[type_name].file):
            # Save to file
            substitution = {'packetname': type_name,
                'version': self.types[type_name].version,
                'username': getpass.getuser(),
                'datetime': str(datetime.now())}
            with open(os.path.join(self.template_path, 'header.txt'), 'r',
                      encoding='utf-8') as fhand:
                src = Template(fhand.read())
                result = src.substitute(substitution)
            fhand.close()
            with open(os.path.join(type_db_filepath,
                                   f'{type_name}_{self.types[type_name].version}.h'),
                                   'w',
                                   encoding='utf-8') as outfile:
                outfile.write(result)
            outfile.close()
        else:
            old_type = copy.deepcopy(type_value)
            self.loadFile(type_value.file)
            new_type = self.types[type_name]
            self.types[type_name] = old_type
            if not old_type == new_type:
                # Has changes - increment
                version = self.types[type_name].version
                self.types[type_name].version = self.incrementVersion(version)
                # update filename
                version = self.types[type_name].version
                self.types[type_name].file = self.updateFileVersion(self.types[type_name].file,
                                                                    version)[0]
        self.saveType(self.types[type_name], self.types[type_name].file)
