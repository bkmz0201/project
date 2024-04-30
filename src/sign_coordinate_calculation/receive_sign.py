from mercator import wgs84_to_mercator, mercator_to_wgs84
from math import *
from merge_file import MergeFile, InformationForCalculation

import math
from geopy.distance import geodesic


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


# Класс для вычисления координат знаков из полученных данных
class ReceiveSign:
    def __init__(self):
        self.signs = []

    def calculation_sign(self, input: MergeFile):
        file = input.get_data()
        for data in file:
            camera_direction = data.file[-6]
            new_heading = direction_offset(data.x_min, data.x_max, data.heading, camera_direction)
            distance_to_sign = distance_to_sign_in_frame(data.x_min, data.x_max)
            print(data.x, 'fff', data.y)
            sign_x_coordinate, sign_y_coordinate = sign_coordinate_calculation(distance_to_sign, data.y, data.x,
                                                                               new_heading)
            self.signs.append(Sign(data.file, sign_x_coordinate, sign_y_coordinate, data.class_name, data.x_min,
                                   data.y_min, data.x_max, data.y_max))

    def get_data(self):
        return self.signs


def distance_to_sign_in_frame(rectangle_x_min, rectangle_x_max):
    sign_width_metres = 0.7
    sign_width_pixel = rectangle_x_max - rectangle_x_min
    frame_width = 720
    camera_angle = 62
    rectangle_x_average = (rectangle_x_min + rectangle_x_max) // 2
    center_to_average = abs(rectangle_x_average - frame_width / 2)
    projection = int((frame_width / 2) / tan(radians(camera_angle / 2)))
    distance = (sign_width_metres / sign_width_pixel) * sqrt(projection ** 2 + center_to_average ** 2)
    # pro = (sign_width_metres * frame_width / 2) / (sign_width_pixel * tan(radians(camera_angle / 2))) / 1000
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
def sign_coordinate_calculation(distance_to_sign, latitude_car, longitude_car, heading):
    x_coordinate_car, y_coordinate_car = wgs84_to_mercator(latitude_car, longitude_car)
    x_coordinate_sign = distance_to_sign * cos(radians(heading)) + x_coordinate_car
    y_coordinate_sign = distance_to_sign * sin(radians(heading)) + y_coordinate_car
    latitude_sign, longitude_sign = mercator_to_wgs84(x_coordinate_sign, y_coordinate_sign)
    return latitude_sign, longitude_sign
