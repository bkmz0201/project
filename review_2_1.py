import pandas as pd
from math import *
from geopy.distance import geodesic
import random
import numpy
import folium
import argparse


# уже лучше.
# TrackLoader содержит какоую-то логику, не связанную с загрузкой данных - он должен вернуть ровно те данные,
# которые содержатся в файле в виде объектной модели. вся логика постобработки и трансфомрации данных в пригодный
# для аналища вид, должна быть реализованна в отдлельном классе.
# все, что касается самой математики, для этого нужна еще одна сущность которая будет заниматся только этим,
# на основе моделей полученных после постобработки.

# главная мысль: не надо сувать код в какой-то класс, если он логически не имеет к нему отношения, например
# метод - sorting в классе Track, зачем он там ? класс Track икапсулирует данные и способ доступа к ним, а
# sorting это уже частный случай обоботки этих данных.
#
#общая логика программы в идеале должна быть примерно такой
#
# получаем объектную модель исходных данных
#loader = TrackLoader()
#source_track = loader.load(args.track_file)
#source_signs = loader.load(args.signs_file)
#
# получаем объектную модель, пригодную для анализа
#track = TrackWithSigns(source_track, source_signs)
#
# выполняем анализ
#merger = SignsMerger()
#sign_groups = merger.merge_similar_signs(merger)
#
# пишем результат
#writer = SigsnWriter()
#writer.save(args.file_out, sign_groups)
#
# воспульзуйтесь модулем argparse дабы вот такого прелести не было
#file_1 = 'digest.csv'
#file_2 = '20230520-203319_predictions.csv'

# import argparse
# parser = argparse.ArgumentParser()
# parser.add_argument("--file_in")
# parser.add_argument("--file_out")
# args = parser.parse_args()
# args.file_in, args.file_out

# не делеайте таких конструкци - можно же self.sign_data['filename'][i] вынести в отдельную переменную и это станет в мильен раз наглдней
#self.sign_data['filename'][i] = self.sign_data['filename'][i][self.sign_data['filename'][i].rfind('/') + 1:]

# еще было бы крайне неплохо подготовить мааааленький экзампл - тестовый кейс 2-3 группы занков по 2-3 в каждом,
# написать bash (или питон) скрипт, который бы запускал скрипт и показывал результат, запаковать это в архив в таком виде,
# чтобы можно было на любой машине в любой директории распаковать, запустить и он бы корректно отработал


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
    def __init__(self, file: str, x: float, y: float, class_name: str, x_min: int, y_min: int, x_max: int, y_max: int,
                 color):
        self.file = file
        self.x = x
        self.y = y
        self.class_name = class_name
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max
        self.color = color
        self.x_arr = []
        self.y_arr = []

    def fill_color(self, clr):
        self.color = clr


class TrackLoader:
    def __init__(self):
        self.car_data = None
        self.sign_data = None
        self.combined_data_frame = None

    def load(self, file1, file2):
        self.car_data = pd.read_csv(file1, delimiter=';')
        self.sign_data = pd.read_csv(file2, delimiter=',')

    def renaming(self):
        # преобразование строки вида
        # "/mnt/lv.tmp.mts.signrecognition/tmp_tracks/59ede2cea7edb283be798f7c0a84a642b77854bb/3096_2.jpeg"
        # к виду "3096_2.jpeg"
        # prevent SettingWithCopyWarning message from appearing
        pd.options.mode.chained_assignment = None
        for i in range(len(self.sign_data)):
            self.sign_data['filename'][i] = self.sign_data['filename'][i][self.sign_data['filename'][i].rfind('/') + 1:]
        self.sign_data = self.sign_data.rename(columns={'filename': 'file'})

    def merge_data_frames_and_del_duplicates(self):
        # объединение входных данных в один DataFrame
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
            data = Machine_input(*elem)
            distance_to_sign = distance_to_sign_in_frame(data.x_min, data.x_max)
            new_heading = direction_offset(data.x_min, data.x_max, data.heading, data.file[-6])
            sign_x_coordinate, sign_y_coordinate = sign_coordinate_calculation(distance_to_sign, data.x, data.y,
                                                                               new_heading)
            track.add_sign(Sign(data.file, sign_x_coordinate, sign_y_coordinate, data.class_name, data.x_min,
                                data.y_min, data.x_max, data.y_max, None))
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
        length = len(self.signs)
        max_distance = 10
        i = 0
        while i != length:
            flag = True
            sign_1 = self.signs[i]
            if sign_1.color is None:
                sign_1.color = "#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])
                folium.CircleMarker(location=[sign_1.x, sign_1.y], radius=1,
                                    popup=sign_1.file + "\n" + sign_1.class_name, color=sign_1.color).add_to(map)
            sign_1.x_arr.append(sign_1.x)
            sign_1.y_arr.append(sign_1.y)
            for j in range(i + 1, length):
                sign_2 = self.signs[j]
                coordinate_sign_1 = (sign_1.x, sign_1.y)
                coordinate_sign_2 = (sign_2.x, sign_2.y)
                if sign_1.class_name == sign_2.class_name and \
                        geodesic(coordinate_sign_1, coordinate_sign_2).meters < max_distance:
                    sign_2.color = sign_1.color
                    folium.CircleMarker(location=[sign_2.x, sign_2.y], radius=1,
                                        popup=sign_2.file + "\n" + sign_2.class_name, color=sign_2.color).add_to(map)
                    sign_2.x_arr.extend(sign_1.x_arr)
                    sign_2.y_arr.extend(sign_1.y_arr)
                    sign_2.x_arr.append(sign_2.x)
                    sign_2.y_arr.append(sign_2.y)
                    flag = False
                    sign_2.x = (sign_2.x + sign_1.x) / 2
                    sign_2.y = (sign_2.y + sign_1.y) / 2
                    self.signs[j] = sign_2
                    self.signs.pop(i)
                    break
            if flag:
                self.signs[i] = sign_1
                i += 1
            else:
                length = len(self.signs)

    def fill_track_out_loader(self):
        dataframe = TrakOutLoader()
        dataframe.add_data(self.signs)
        return dataframe


# требует доработки
class TrakOutLoader:
    def __init__(self):
        self.signs = None

    def add_data(self, sign):
        self.signs = sign

    def to_csv(self):
        df = pd.DataFrame(self.signs, columns=['filename', 'x', 'y', 'class_name', 'x_min', 'y_min', 'x_max', 'y_max',
                                               'color'])
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

parser = argparse.ArgumentParser(description='Process some files.')
parser.add_argument('--file_in', type=str, help='Input file path for car data')
parser.add_argument('--file_out', type=str, help='Input file path for sign data')
args = parser.parse_args()

if args.file_in and args.file_out:
    file_1 = args.file_in
    file_2 = args.file_out
else:
    print("Please provide both input and output file paths using --file_in and --file_out options.")
    exit()
#file_1 = 'digest.csv'
#file_2 = '20230520-203319_predictions.csv'
a = TrackLoader()
a.load(file_1, file_2)
a.renaming()
a.merge_data_frames_and_del_duplicates()
b = a.fill_track()
map = folium.Map(location=[43.595754, 39.734652], zoom_start=15)
b.sorting()
for sign in b.signs:
    folium.CircleMarker(location=[numpy.average(sign.x_arr), numpy.average(sign.y_arr)], radius=4,
                        popup=sign.file + "\n" + sign.class_name, color=sign.color).add_to(map)
map.save("hello.html")
c = b.fill_track_out_loader()
c.to_csv()