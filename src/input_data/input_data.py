class MachineInput:
    def __init__(self, file: str, x: float, y: float, time: int, speed: float, heading: float, altitude: float,
                 offset: int):
        self.file = file
        self.x = x
        self.y = y
        self.time = time
        self.speed = speed
        self.heading = heading
        self.altitude = altitude
        self.offset = offset


# Класс для представления данных полученных в результате работы ИИ
class AiInput:
    def __init__(self, filename: str, class_id: int, class_name: str, x_min: int, y_min: int, x_max: int, y_max: int,
                 score: float):
        self.file = filename
        self.class_id = class_id
        self.class_name = class_name
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max
        self.score = score
