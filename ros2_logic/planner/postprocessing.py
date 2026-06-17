import math
from collections import OrderedDict

GRIP_OFFSETS = {
    0:  (0.0,  0.0),   # rejected
    1:  (15.0, 5.0),   # Cat
    27: (20.0, 10.0),  # Unicorn
}

class PostProcessor:
    def __init__(self):
        # Einzige Datenstruktur: geordnetes Dict {id: {obj_type, pose2d, speed}}
        # Reihenfolge des ersten Auftauchens bleibt erhalten
        self.queue = OrderedDict()

    def add_obj_type(self, id, obj_type):
        if id not in self.queue:
            self.queue[id] = {}

        self.queue[id]['obj_type'] = obj_type

    def add_future_position(self, id, pose2d, speed):
        if id not in self.queue:
            self.queue[id] = {}

        self.queue[id]['pose2d'] = pose2d
        self.queue[id]['speed'] = speed

    def get_next(self):
        for id, data in self.queue.items():
            if 'obj_type' in data and 'pose2d' in data and 'speed' in data:
                return self.build_output(id, data)
        return None

    def finish_obj(self, id):
        self.queue.pop(id, None)

    def build_output(self, id, data):
        pose2d = data['pose2d']
        obj_type = data['obj_type']
        grip = self.calculate_grip_point(pose2d, obj_type)

        return {
            'id': id,
            'obj_type': obj_type,
            'pose2d': pose2d,
            'speed': data['speed'],
            'grip_point': grip,
        }

    def calculate_grip_point(self, pose2d, obj_type):
        offset_x, offset_y = GRIP_OFFSETS.get(obj_type, (10.0, 0.0))
        theta_rad = math.radians(pose2d.theta)

        grip_x = pose2d.x + offset_x * math.cos(theta_rad) - offset_y * math.sin(theta_rad)
        grip_y = pose2d.y + offset_x * math.sin(theta_rad) + offset_y * math.cos(theta_rad)

        return {
            'x': grip_x,
            'y': grip_y,
            'theta': 0,
        }