import pytest
import os
import csv

from martepy.functions.bin2csv import Bin2CSV, Bin2CSVError

def test_bin2csv():
    input_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),'output.bin')
    output_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),'log0.csv')
    binmain = Bin2CSV(input_path,output_path)
    binmain.main()
    with open(output_path, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')

    input_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),'output.bin')
    output_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),'log1.csv')
    binmain = Bin2CSV(input_path,output_path, marte2_csv=False)
    binmain.main()
    with open(output_path, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')

    with pytest.raises(Bin2CSVError) as excinfo:
        input_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),'bad_descriptor.bin')
        output_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),'log2.csv')
        binmain = Bin2CSV(input_path,output_path, marte2_csv=False)
        binmain.main()
    assert str(excinfo.value) == 'Unknown TypeDescription code: 65284 for signal Counter'

    with pytest.raises(Bin2CSVError) as excinfo:
        input_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),'chopped_line.bin')
        output_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),'log2.csv')
        binmain = Bin2CSV(input_path,output_path, marte2_csv=False)
        binmain.main()
    assert str(excinfo.value) == 'Reached EOF with partial row: 4 leftover bytes'
    # clean up
    os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)),'log0.csv'))
    os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)),'log1.csv'))