import pandas as pd
import csv
from input_data import MachineInput, AiInput


class LoadFile:
    def __init__(self, file_name):
        self.data = []
        with open(file_name) as fp:
            delimiter = csv.Sniffer().sniff(fp.read(5000)).delimiter
        # Чтение данных из CSV файла в DataFrame
        self.data_in = pd.read_csv(file_name, delimiter=str(delimiter))
        if 'digest' in str(file_name):
            for index, row in self.data_in.iterrows():
                self.data.append(MachineInput(*list(row)))
        else:
            self.data_in = filenames_rename(self.data_in)
            for index, row in self.data_in.iterrows():
                self.data.append(AiInput(*list(row)))


def filenames_rename(data):
    # преобразование строки вида
    # "/mnt/lv.tmp.mts.signrecognition/tmp_tracks/59ede2cea7edb283be798f7c0a84a642b77854bb/3096_2.jpeg"
    # к виду "3096_2.jpeg"
    pd.options.mode.chained_assignment = None
    data_to_prepare = data
    for rows in range(len(data_to_prepare)):
        file_name = data_to_prepare['filename'][rows]
        new_file_name = file_name[file_name.rfind('/') + 1:]
        data_to_prepare['filename'][rows] = new_file_name
    data_to_prepare = data_to_prepare.rename(columns={'filename': 'file'})
    return data_to_prepare
