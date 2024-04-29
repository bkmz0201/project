import math


def wgs84_to_mercator(latitude, longitude):
    large_semi_axis_mtr = 6378245
    x_coordinate = large_semi_axis_mtr * longitude
    try:
        y_coordinate = large_semi_axis_mtr * log(tan(radians(45 + latitude / 2)))
    except:
        y_coordinate = 0
        print(latitude, '-', math.tan(radians(45 + latitude / 2)))
        print(latitude, '-__-', tan(radians(45 + latitude / 2)))
    # y_coordinate = (large_semi_axis_mtr / 2) * log((1 + sin(radians(latitude)))/(1 - sin(radians(latitude))))
    print(x_coordinate, y_coordinate)
    return x_coordinate, y_coordinate


# Обратная Проекция Меркатора
def mercator_to_wgs84(x_coordinate, y_coordinate):
    large_semi_axis_mtr = 6378245
    longitude = x_coordinate / large_semi_axis_mtr
    latitude = degrees(pi / 2 - atan(exp(-y_coordinate / large_semi_axis_mtr)))
    return latitude, longitude
