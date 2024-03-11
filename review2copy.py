import pandas as pd
from math import *
from geopy.distance import geodesic


class Machine_input:
    def __init__(self, file: str, y: float, x: float, heading: int, class_name: str, x_min: int, y_min: int, x_max: int,
                 y_max: int):
        self.file = file
        self.x = x
        self.y = y
        self.heading = heading
        self.class_name = class_name
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max


class Sign:
    def __init__(self, file: str, x: float, y: float, class_name: str, x_min: int, y_min: int, x_max: int, y_max: int):
        self.file = file
        self.x = x
        self.y = y
        self.class_name = class_name
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max
        self.x_arr = []
        self.y_arr = []


class TrackLoader:
    def __init__(self):
        self.car_data = None
        self.sign_data = None
        self.combined_data_frame = None

    def load(self, file1, file2):
        self.car_data = pd.read_csv(file1, delimiter=';')
        self.sign_data = pd.read_csv(file2, delimiter=',')

    def renaming(self):
        # этому тут не место, хардкод путей в коде - плохой тон
        # Done
        # prevent SettingWithCopyWarning message from appearing
        pd.options.mode.chained_assignment = None
        for i in range(len(self.sign_data)):
            self.sign_data['filename'][i] = self.sign_data['filename'][i][self.sign_data['filename'][i].rfind('/') + 1:]
        self.sign_data = self.sign_data.rename(columns={'filename': 'file'})

    def merge_data_frames_and_del_duplicates(self):
        self.combined_data_frame = pd.merge(self.car_data, self.sign_data, on='file', how='inner')
        self.combined_data_frame.drop(['offset', 'score', 'speed', 'time', 'altitude', 'class_id'],
                                      axis=1,
                                      inplace=True)
        columns_to_check = ['x', 'y', 'class_name']
        self.combined_data_frame.drop_duplicates(subset=columns_to_check, inplace=True)
        self.combined_data_frame = self.combined_data_frame.rename(columns={'x': 'y', 'y': 'x'})
        self.combined_data_frame.index = range(0, len(self.combined_data_frame.values), 1)

    def fill_track(self):
        # создаем объекты класса трек
        track = Track()
        for elem in self.combined_data_frame.values:
            data\
                = Machine_input(*elem)
            distance_to_sign = distance_to_sign_in_frame(data.x_min, data.x_max)
            new_heading = direction_offset(data.x_min, data.x_max, data.heading, data.file[-6])
            sign_x_coordinate, sign_y_coordinate = sign_coordinate_calculation(distance_to_sign, data.x, data.y,
                                                                               new_heading)
            track.add_sign(Sign(data.file, sign_x_coordinate, sign_y_coordinate, data.class_name, data.x_min,
                                data.y_min, data.x_max, data.y_max))
        return track


class Track:
    def __init__(self):
        self.signs = []

    def add_sign(self, sign):
        self.signs.append(sign)

    def output(self):
        for elem in self.signs:
            print(elem)

    def sorting(self):
        # В данном методе реализована сортировка знаков по двум признакам: 1) расстояние между знаками (max_distance)
        # меньше либо равно 5 метров 2) совпадают типы знаков (class_name_of_sign_...).
        # В случае выполнения обоих условий, знак, по которому производилась сверка (sign_1), удаляется, а информация
        # о знаке, с которым сверялись, обновляется, т.е. координата знака пересчитывается,
        # как среднее арифметическое между координатами двух знаков.
        max_distance = 6
        flag_merge = True
        length = len(self.signs)
        while flag_merge:
            flag_merge = False
            i = 0
            while i != length:
                flag = True
                sign_1 = self.signs[i]
                for j in range(i + 1, length):
                    sign_2 = self.signs[j]
                    coordinate_sign_1 = (sign_1.x, sign_1.y)
                    coordinate_sign_2 = (sign_2.x, sign_2.y)
                    if sign_1.class_name == sign_2.class_name and \
                            geodesic(coordinate_sign_1, coordinate_sign_2).meters < max_distance:
                        flag_merge = True
                        flag = False
                        sign_2.x = (sign_2.x + sign_1.x) / 2
                        sign_2.y = (sign_2.y + sign_1.y) / 2
                        self.signs[j] = sign_2
                        self.signs.pop(i)
                        break
                if flag:
                    i += 1
                else:
                    length = len(self.signs)

    def fill_track_out_loader(self):
        dataframe = TrakOutLoader()
        dataframe.add_data(self.signs)
        return dataframe


class TrakOutLoader:
    def __init__(self):
        self.signs = None

    def add_data(self, sign):
        self.signs = sign

    def to_csv(self):
        df = pd.DataFrame(self.signs, columns=['filename', 'x', 'y', 'class_name', 'x_min', 'y_min', 'x_max', 'y_max'])
        return df.to_csv('test_final.csv')


def distance_to_sign_in_frame(x_min, x_max):
    sign_width_metres = 0.7
    sign_width_pixel = x_max - x_min
    frame_width = 720
    camera_angle = 62
    distance = (sign_width_metres * frame_width / 2) / (
                sign_width_pixel * tan(radians(camera_angle / 2))) / 1000
    return distance


def direction_offset(rectangle_x_min, rectangle_x_max, car_azimuth, camera_number):
    shift_from_direction = 55
    frame_width = 720
    camera_angle = 62
    rectangle_x_average = (rectangle_x_min + rectangle_x_max) // 2
    projection = int((frame_width / 2) / tan(radians(camera_angle / 2)))
    offset = degrees(atan((rectangle_x_average - frame_width / 2) / projection))
    if camera_number == '3':
        car_azimuth -= 180
    elif camera_number == '0':
        car_azimuth -= shift_from_direction
    elif camera_number == '2':
        car_azimuth += shift_from_direction
    if car_azimuth > 360:
        car_azimuth -= 360
    elif car_azimuth < 0:
        car_azimuth += 360
    return car_azimuth + offset


def sign_coordinate_calculation(distance_to_sign, x_coordinate_of_the_car, y_coordinate_of_the_car, heading):
    one_km_in_one_degree_in_latitude = 111.32
    one_km_in_one_degree_in_longitude = 40075 * cos(radians(x_coordinate_of_the_car)) / 360
    x_coordinate_of_the_sign = round(((distance_to_sign * cos(radians(heading)) + x_coordinate_of_the_car *
                                       one_km_in_one_degree_in_latitude) /one_km_in_one_degree_in_latitude), 10)
    y_coordinate_of_the_sign = round(
        (distance_to_sign * sin(radians(heading)) + one_km_in_one_degree_in_longitude *
         y_coordinate_of_the_car) / one_km_in_one_degree_in_longitude, 10)
    return x_coordinate_of_the_sign, y_coordinate_of_the_sign


file_1 = 'digest.csv'
file_2 = '20230520-203319_predictions.csv'
a = TrackLoader()
a.load(file_1, file_2)
a.renaming()
a.merge_data_frames_and_del_duplicates()
b = a.fill_track()
b.output()
b.sorting()
# c = b.fill_track_out_loader()
# c.to_csv()
