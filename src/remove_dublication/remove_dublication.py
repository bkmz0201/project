import numpy
from geopy.distance import geodesic


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
