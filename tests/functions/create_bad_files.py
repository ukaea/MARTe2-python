import os

with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),'output.bin'), 'rb') as infile:
    binary = infile.read()
    newbytes = bytearray(binary)
    newbytes[5] = 255
    sbinary = bytes(newbytes)
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),'bad_descriptor.bin'), 'wb') as outfile:
        outfile.write(sbinary)

    newbytes = bytearray(binary)
    sbinary = bytes(newbytes[:-20])
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),'chopped_line.bin'), 'wb') as outfile:
        outfile.write(sbinary)
pass