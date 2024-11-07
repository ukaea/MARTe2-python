import tarfile
import json
import copy
import shutil
import io
import glob
import os
import tempfile

def discover_xmt_files(directory):
     """Discover all .xmt files in the specified directory."""
     return glob.glob(os.path.join(directory, '*.xmt'))

def modify_file_in_tar(input_tar_path):
    """
    Modify the contents of a specific file in a tar archive without changing any other contents.

    :param input_tar_path: Path to the input tar file.
    :param output_tar_path: Path to the output tar file.
    :param target_file: The relative path of the file to be modified within the tar archive.
    :param modify_function: A function that modifies the contents of the target file.
    """
    # Create a temporary directory to work with
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract the contents of the tar file
        with tarfile.open(input_tar_path, 'r') as tar:
            tar.extractall(path=temp_dir)


        if os.path.exists(os.path.join(temp_dir, 'test_def.json')):
            os.remove(os.path.join(temp_dir, 'test_def.json'))
        
        os.remove(input_tar_path)
        # Create a new tar file with the modified contents
        with tarfile.open(input_tar_path, 'w') as tar:
            for root, dirs, files in os.walk(temp_dir):
                for directory in dirs:
                    dir_path = os.path.join(root, directory)
                    arcname = os.path.relpath(dir_path, temp_dir)
                    tar.add(dir_path, arcname=arcname)  # Add directory explicitly
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    tar.add(file_path, arcname=arcname)
                    
curr_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)))

files = discover_xmt_files(curr_dir)
for filepath in files:
    if not filepath == 'multistatethread_complextype_timer_filereading.xmt':
        modify_file_in_tar(filepath)
