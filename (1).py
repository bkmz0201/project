# подключение библиотек
import argparse
import pandas as pd
from math import *
from geopy.distance import geodesic
import random
import numpy
import folium
import csv
import time

from dataclasses import dataclass


@dataclass
class BBox:
    x_min: int
    x_max: int
    y_min: int
    y_max: int


@dataclass
class Coord:
    x: float
    y: float


@dataclass
class MachineInput:
    file: str
    coord: Coord
    bbox: BBox


# Класс для представления данных полученных с машины
class MachineInput:
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


# Класс для представления данных полученных в результате работы ИИ
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
        self.x_arr = [x]
        self.y_arr = [y]
        self.files = [file]


# Класс для преобразования данных из CSV файлов в DataFrame через библиотеку pandas
class ReceiveData:
    @staticmethod
    def load(file):
        with open(file) as fp:
            delimiter = csv.Sniffer().sniff(fp.read(5000)).delimiter
        data = pd.read_csv(file, delimiter=str(delimiter))
        return data


def read_csv():
    """
    eta funca delaet to-to
    """
    pass


# Поскольку для дальнейшей более удобной работы с полученными данными их нужно объединить в один DataFrame.
# Для этого нам нужно подготовить данные полученные с машины.
class PrepareData:
    @staticmethod
    def filenames_rename(data):
        # преобразование строки вида
        # "/mnt/lv.tmp.mts.signrecognition/tmp_tracks/59ede2cea7edb283be798f7c0a84a642b77854bb/3096_2.jpeg"
        # к виду "3096_2.jpeg"
        pd.options.mode.chained_assignment = None
        # исправить срочно
        data_to_prepare = data
        for index in range(len(data_to_prepare)):
            new_file_name = data_to_prepare['filename'][index]
            new_file_name = new_file_name[new_file_name.rfind('/') + 1:]
            data_to_prepare['filename'][index] = new_file_name
        data_to_prepare = data_to_prepare.rename(columns={'filename': 'file'})
        return data_to_prepare


# Класс для объединения данных с машины и результатов работы ИИ в один DataFrame и
# удаления дубликатов информации в этом DataFrame
class ProcessData:
    def __init__(self):
        self.combined_data_frame = None

    def merge(self, car_data, sign_data):
        # объединение входных данных в один DataFrame
        self.combined_data_frame = pd.merge(car_data, sign_data, on='file', how='inner')
        self.combined_data_frame.drop(
            ['offset', 'score', 'speed', 'time', 'altitude', 'class_id'],
            axis=1,
            inplace=True,
        )

    def delete_duplicates(self):
        columns_to_check = ['x', 'y', 'class_name']
        self.combined_data_frame.drop_duplicates(subset=columns_to_check, inplace=True)
        self.combined_data_frame = self.combined_data_frame.rename(columns={'x': 'y', 'y': 'x'}).reset_index(drop=True)

    def get_data(self):
        return self.combined_data_frame


# Класс для вычисления координат знаков из полученных данных
class ReceiveSign:
    def __init__(self):
        self.signs = []

    def calculation_sign(self, data):
        for elem in data.values:
            data = MachineInput(*elem)
            distance_to_sign = distance_to_sign_in_frame(data.x_min, data.x_max)
            camera_direction = data.file[-6]
            new_heading = direction_offset(data.x_min, data.x_max, data.heading, camera_direction)
            sign_x_coordinate, sign_y_coordinate = sign_coordinate_calculation(distance_to_sign, data.x, data.y,
                                                                               new_heading)
            self.signs.append(Sign(data.file, sign_x_coordinate, sign_y_coordinate, data.class_name, data.x_min,
                                   data.y_min, data.x_max, data.y_max))
        return self.signs


# Класс для удаления дубликатов знаков и вычисления конечного месторасположения знака
class RemoveDuplicatesSign:
    def __init__(self):
        self.signs = None

    def get_signs(self):
        for elem in self.signs:
            print(elem)

    def merge_similar_signs(self, data):
        self.signs = data
        length = len(self.signs)
        max_distance = 5
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
                    sign_2.x_arr.extend(sign_1.x_arr)
                    sign_2.y_arr.extend(sign_1.y_arr)
                    sign_2.files.extend(sign_1.files)
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
        for i in range(length):
            sign = self.signs[i]
            sign.x = numpy.average(sign.x_arr)
            sign.y = numpy.average(sign.y_arr)
            self.signs[i] = sign
        return self.signs

        # второй алгоритм сортировки (представлен для сравнения с первым)

    def merge_similar_signs_1(self, data):
        self.signs = data
        length = len(self.signs)
        max_distance = 10
        flag_unique = 1
        while flag_unique:
            i = 0
            flag_unique = 0
            while i != length:
                flag = False
                sign_1 = self.signs[i]
                for j in range(i + 1, length):
                    sign_2 = self.signs[j]
                    coordinate_sign_1 = (sign_1.x, sign_1.y)
                    coordinate_sign_2 = (sign_2.x, sign_2.y)
                    if sign_1.class_name == sign_2.class_name and \
                            geodesic(coordinate_sign_1, coordinate_sign_2).meters < max_distance:
                        flag_unique = 1
                        sign_1.x_arr.extend(sign_2.x_arr)
                        sign_1.y_arr.extend(sign_2.y_arr)
                        sign_1.files.extend(sign_2.files)
                        flag = True
                        sign_1.x = (sign_2.x + sign_1.x) / 2
                        sign_1.y = (sign_2.y + sign_1.y) / 2
                        self.signs[i] = sign_1
                        self.signs.pop(j)
                        break
                if flag:
                    length = len(self.signs)
                i += 1
        for i in range(length):
            sign = self.signs[i]
            sign.x = numpy.average(sign.x_arr)
            sign.y = numpy.average(sign.y_arr)
            self.signs[i] = sign
        return self.signs


# Класс для сохранения знаков в выходной CSV файл
class SignsSave:
    @staticmethod
    def save(file, sign_group):
        df = pd.DataFrame(columns=['filename', 'x', 'y', 'class_name', 'x_min', 'y_min', 'x_max', 'y_max'])
        for sign in sign_group:
            df.loc[len(df.index)] = [sign.file, sign.x, sign.y, sign.class_name, sign.x_min, sign.y_min, sign.x_max,
                                     sign.y_max]
        df.to_csv(file)


# Вычисление дистанции до знака в кадре
def distance_to_sign_in_frame(x_min, x_max):
    sign_width_metres = 0.7
    sign_width_pixel = x_max - x_min
    frame_width = 720
    camera_angle = 62
    distance = (sign_width_metres * frame_width / 2) / (sign_width_pixel * tan(radians(camera_angle / 2))) / 1000
    return distance


# расчет азимута от машины до знака по азимуту движения машины и расположению знака в кадре
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


# Вычисление координаты знака
def sign_coordinate_calculation(distance_to_sign, x_coordinate_of_the_car, y_coordinate_of_the_car, heading):
    one_km_in_one_degree_in_latitude = 111.32
    one_km_in_one_degree_in_longitude = 40075 * cos(radians(x_coordinate_of_the_car)) / 360
    x_coordinate_of_the_sign = round(((distance_to_sign * cos(radians(heading)) + x_coordinate_of_the_car *
                                       one_km_in_one_degree_in_latitude) / one_km_in_one_degree_in_latitude), 10)
    y_coordinate_of_the_sign = round(
        (distance_to_sign * sin(radians(heading)) + one_km_in_one_degree_in_longitude *
         y_coordinate_of_the_car) / one_km_in_one_degree_in_longitude, 10)
    return x_coordinate_of_the_sign, y_coordinate_of_the_sign


# Визуализация результатов работы алгоритма на карте
def visualization(signs_group):
    sign_map = folium.Map(location=[signs_group[0].x, signs_group[0].y], zoom_start=15)
    for sign in signs_group:
        color = "#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])
        size = len(sign.x_arr)
        for i in range(size):
            x = sign.x_arr[i]
            y = sign.y_arr[i]
            folium.PolyLine([(x, y), (sign.x, sign.y)],
                            tooltip=sign.files[i] + "\n" + sign.class_name,
                            color=color,
                            weight=1,
                            opacity=0.8).add_to(sign_map)
        folium.CircleMarker(location=[sign.x, sign.y], radius=1,
                            popup=sign.file + "\n" + sign.class_name + '\n' + '\n'.join(sign.files),
                            color=color).add_to(sign_map)
    # На карте вы увидите точки и исходящие из них отрезки, то где раньше располагался распознанный знак. Точка на карте
    # это конечный знак, который пошел в выходной файл
    sign_map.save("test_final.html")


parser = argparse.ArgumentParser(description='Process some files.')
parser.add_argument('--file_in_1', type=str, help='Input file path for car data')
parser.add_argument('--file_in_2', type=str, help='Input file path for sign data')
parser.add_argument('--file_out', type=str, help='Input file path for sign data')
args = parser.parse_args()

if args.file_in_1 and args.file_in_2 and args.file_out:
    file_1 = args.file_in_1
    file_2 = args.file_in_2
    file_3 = args.file_out
else:
    print("Please provide both input and output file paths using --file_in and --file_out options.")
    exit()

start = time.time()

# исправить неймнинг переменных
loader = ReceiveData()
car_data = loader.load(file_1)
sign_data = loader.load(file_2)
prepare = PrepareData()
sign_data = prepare.filenames_rename(sign_data)
combined_data = ProcessData()
combined_data.merge(car_data, sign_data)
combined_data.delete_duplicates()
# задолбали со своей датой
data1 = combined_data.get_data()
convertor = ReceiveSign()
calculation_sign = convertor.calculation_sign(data1)
sign = calculation_sign
remover = RemoveDuplicatesSign()
sign = remover.merge_similar_signs(sign)
outload = SignsSave()
outload.save(file_3, sign)

visualization(sign)
end = time.time()

print('TIME: ', end - start)
# python review_4.py --file_in_1 digest.csv --file_in_2 20230520-203319_predictions.csv --file_out test_final.csv
