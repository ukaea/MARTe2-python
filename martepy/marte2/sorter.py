''' Topologically sorts the dependencies of headers in a given directory based on header 
imports '''

import os
import re

def _extractIncludes(file_path):
    ''' Get the includes from a C++ header '''
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        # Use a regular expression to extract included header files
        includes = re.findall(r'#include\s+[<"]([^>"]+)[>"]', content)
        return includes

def _findDependencies(directory):
    ''' From a directory, create a dictionary of headers and their dependencies '''
    # Get all header files in the directory
    header_files = [file for file in os.listdir(directory) if file.endswith(".h")]

    # Create a dictionary to store dependencies
    dependencies = {file: set(_extractIncludes(os.path.join(directory, file))) for
                    file in header_files}

    return dependencies

def _topologicalSort(dependencies, directory):
    ''' Sort our dictionary based on it's dependencies defined from includes '''
    sorted_files = []
    visited = set()

    def visit(file):
        if file not in visited:
            visited.add(file)
            if os.path.exists(os.path.join(directory, file)):
                sorted_files.append(os.path.join(directory, file))

    for file in dependencies.keys():
        visit(file)

    return sorted_files[::-1]

def sortHeaders(directory):
    ''' Publically accessible function to sort headers and return an ordered list of 
    files given a directory '''
    dependencies = _findDependencies(directory)
    ordered_files = _topologicalSort(dependencies, directory)
    ordered_files.reverse()
    return ordered_files
