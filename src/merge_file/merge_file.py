import pandas as pd
from load_file import LoadFile


class InformationForCalculation:
    def __init__(self, file: str, y: float, x: float, heading: float, class_name: str, x_min: int, y_min: int,
                 x_max: int, y_max: int):
        self.file = file
        self.x = x
        self.y = y
        self.heading = heading
        self.class_name = class_name
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max


class MergeFile:
    def __init__(self, file_1: LoadFile, file_2: LoadFile):
        self.combined_data_frame = None
        self.combined = []
        car_data = file_1.get_data_in_dataframe()
        sign_data = file_2.get_data_in_dataframe()
        # объединение входных данных в один DataFrame
        self.combined_data_frame = pd.merge(car_data, sign_data, on='file', how='inner')
        self.combined_data_frame.drop(['offset', 'score', 'speed', 'time', 'altitude', 'class_id'],
                                      axis=1,
                                      inplace=True)
        # удаление дубликатов
        columns_to_check = ['x', 'y', 'class_name']
        self.combined_data_frame.drop_duplicates(subset=columns_to_check, inplace=True)
        self.combined_data_frame = self.combined_data_frame.rename(columns={'x': 'y', 'y': 'x'})
        self.combined_data_frame.index = range(0, len(self.combined_data_frame.values), 1)
        for index, row in self.combined_data_frame.iterrows():
            self.combined.append(InformationForCalculation(*list(row)))

    def get_data(self):
        return self.combined

    def get_data_in_dataframe(self):
        return self.combined_data_frame
