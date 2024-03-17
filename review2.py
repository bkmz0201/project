import pandas as pd
from math import *
from geopy.distance import geodesic
import random
import numpy
import folium
import requests
import polyline
import osmnx

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
        self.duplicates_x = []
        self.duplicates_y = []
        self.duplicates_file = []


class TrackLoader:
    def __init__(self):
        self.car_data = None
        self.sign_data = None
        self.combined_data_frame = None

    def load(self, file1, file2):
        self.car_data = pd.read_csv(file1, delimiter=',')
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

    def formatting(self):
        value = len(self.combined_data_frame.values)
        for k in range(value - 1):
            position1x = self.combined_data_frame['x'][k]
            position1y = self.combined_data_frame['y'][k]
            position2x = self.combined_data_frame['x'][k + 1]
            position2y = self.combined_data_frame['y'][k + 1]
            print(k, '/', value, '\n')
            route_url = ('http://router.project-osrm.org/route/v1/driving/'+str(position1y)+','+str(position1x)+';'
                         +str(position2y)+','+str(position2x)
                         +'?alternatives=true&geometries=polyline')
            r = requests.get(route_url)
            res = r.json()
            routes = polyline.decode(res['routes'][0]['geometry'])
            if k == 0:
                self.combined_data_frame['x'][k] = routes[0][0]
                self.combined_data_frame['y'][k] = routes[0][1]
                folium.CircleMarker(location=routes[0], radius=0.5, fill_color="green", color="green").add_to(map)
            self.combined_data_frame['x'][k + 1] = routes[-1][0]
            self.combined_data_frame['y'][k + 1] = routes[-1][1]
            folium.CircleMarker(location=routes[-1], radius=0.5, fill_color="green", color="green").add_to(map)
        print("good\n")

    # def formatting(self):
    #     g = osmnx.graph_from_bbox(43.6174656980281, 43.56382421404822, 39.76319575776185, 39.683864765642525, network_type='drive')
    #     value = len(self.combined_data_frame.values)
    #     route = []
    #     for k in range(value - 1):
    #         position_x = self.combined_data_frame['x'][k]
    #         position_y = self.combined_data_frame['y'][k]
    #         node = osmnx.nearest_nodes(g, position_x, position_y)
    #         route.append(node)
    #         edge_nodes = list(zip(route[:-1], route[1:]))
    #         print(edge_nodes)
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


class Ancestor:
    def __init__(self, file: str, x: float, y: float):
        self.file = file
        self.x = x
        self.y = y


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
                # folium.CircleMarker(location=[sign_1.x, sign_1.y], radius=1,
                #                     popup=sign_1.file + "\n" + sign_1.class_name, color=sign_1.color).add_to(map)
                sign_1.x_arr.append(sign_1.x)
            sign_1.y_arr.append(sign_1.y)
            for j in range(i + 1, length):
                sign_2 = self.signs[j]
                coordinate_sign_1 = (sign_1.x, sign_1.y)
                coordinate_sign_2 = (sign_2.x, sign_2.y)
                if sign_1.class_name == sign_2.class_name and \
                        geodesic(coordinate_sign_1, coordinate_sign_2).meters < max_distance:
                    sign_2.color = sign_1.color
                    # folium.CircleMarker(location=[sign_2.x, sign_2.y], radius=1,
                    #                     popup=sign_2.file + "\n" + sign_2.class_name, color=sign_2.color).add_to(map)
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

    def sorting1(self):
        length = len(self.signs)
        max_distance = 10
        i = 0
        weight_sign_1 = 0.5
        weight_sign_2 = 0.5
        while i != length:
            flag = True
            sign_1 = self.signs[i]
            if sign_1.color is None:
                sign_1.color = "#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])
                # folium.CircleMarker(location=[sign_1.x, sign_1.y], radius=1,
                #                     popup=sign_1.file + "\n" + sign_1.class_name, color=sign_1.color).add_to(map)
                sign_1.x_arr.append(sign_1.x)
            sign_1.y_arr.append(sign_1.y)
            for j in range(i + 1, length):
                sign_2 = self.signs[j]
                coordinate_sign_1 = (sign_1.x, sign_1.y)
                coordinate_sign_2 = (sign_2.x, sign_2.y)
                if sign_1.class_name == sign_2.class_name and \
                        geodesic(coordinate_sign_1, coordinate_sign_2).meters < max_distance:
                    sign_2.color = sign_1.color
                    # folium.CircleMarker(location=[sign_2.x, sign_2.y], radius=1,
                    #                     popup=sign_2.file + "\n" + sign_2.class_name, color=sign_2.color).add_to(map)
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

    def sorting2(self):
        length = len(self.signs)
        max_distance = 10
        flag_unique = 1
        while flag_unique:
            i = 0
            flag_unique = 0
            while i != length:
                flag = False
                sign_1 = self.signs[i]
                if sign_1.color is None:
                    sign_1.color = "#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])
                    # folium.CircleMarker(location=[sign_1.x, sign_1.y], radius=1,
                    #                     popup=sign_1.file + "\n" + sign_1.class_name, color=sign_1.color).add_to(map)
                sign_1.x_arr.append(sign_1.x)
                sign_1.y_arr.append(sign_1.y)
                for j in range(i + 1, length):
                    sign_2 = self.signs[j]
                    coordinate_sign_1 = (sign_1.x, sign_1.y)
                    coordinate_sign_2 = (sign_2.x, sign_2.y)
                    if sign_1.class_name == sign_2.class_name and \
                            geodesic(coordinate_sign_1, coordinate_sign_2).meters < max_distance:
                        # folium.CircleMarker(location=[sign_2.x, sign_2.y], radius=1,
                        #                     popup=sign_2.file + "\n" + sign_2.class_name, color=sign_1.color).add_to(map)
                        flag_unique = 1
                        sign_1.x_arr.extend(sign_2.x_arr)
                        sign_1.y_arr.extend(sign_2.y_arr)
                        flag = True
                        sign_1.x = (sign_2.x + sign_1.x) / 2
                        sign_1.y = (sign_2.y + sign_1.y) / 2
                        self.signs[i] = sign_1
                        self.signs.pop(j)
                        break
                if flag:
                    length = len(self.signs)
                i += 1





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


def visualization():
    return 0


file_1 = 'digest.csv'
file_2 = '20230520-203319_predictions.csv'
map = folium.Map(location=[43.595754, 39.734652], zoom_start=15)
a = TrackLoader()
a.load(file_1, file_2)
a.renaming()
a.merge_data_frames_and_del_duplicates()
# a.formatting()
b = a.fill_track()
b.sorting()
for sign in b.signs:
    size = len(sign.x_arr)
    print(size)
    x_z = numpy.average(sign.x_arr)
    y_z = numpy.average(sign.y_arr)
    for k in range(size):

        folium.PolyLine([(sign.x_arr[k], sign.y_arr[k]), (x_z, y_z)],
                        color=sign.color,
                        weight=1,
                        opacity=0.8).add_to(map)
    folium.CircleMarker(location=[x_z, y_z], radius=1,
                        popup=sign.file + "\n" + sign.class_name, color=sign.color).add_to(map)
map.save("hello4.html")
# c = b.fill_track_out_loader()
# c.to_csv()