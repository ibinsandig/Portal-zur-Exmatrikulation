import math
from collections import OrderedDict

GRIP_OFFSETS = {
    0:  (0.0,  0.0),   # rejected #TODO Kreise werden als einhörner erkannt
    1:  (0.0, 0.0),   # Cat
    2: (0.0, 0.0),  # Unicorn
}

class PostProcessor:
    def __init__(self):
        # Einzige Datenstruktur: geordnetes Dict {id: {obj_type, pose2d, speed}}
        # Reihenfolge des ersten Auftauchens bleibt erhalten
        self.queue = OrderedDict()

        self.previous_timestamp = None
        self.previous_x = None
        self.previous_y = None

    def add_obj_type(self, id, obj_type):

        if id == 0:
            print("type: rejected verworfen")
            return

        if id not in self.queue:
            self.queue[id] = {}

        self.queue[id]['obj_type'] = obj_type

    def add_future_position(self, id, pose2d, speed, timestamp):

        if id == 0:
            print("Pos: rejected verworfen")
            return

        if id not in self.queue:
            self.queue[id] = {}

        self.queue[id]['pose2d'] = pose2d
        self.queue[id]['speed'] = speed
        self.queue[id]['timestamp']  = timestamp

    def get_next(self):
        for id, data in self.queue.items():
            if 'obj_type' in data and 'pose2d' in data and 'speed' in data:
                return self.build_output(id, data)
        print("Daten nicht vollständig")
        return None

    def finish_obj(self, id):
        self.queue.pop(id, None)
        self.previous_y = None
        self.previous_x = None


    def build_output(self, id, data):
        pose2d = data['pose2d']
        obj_type = data['obj_type']
        timestamp = data['timestamp']
        speed = data['speed']

        grip = self.calculate_grip_point(pose2d, obj_type, timestamp, speed)

        if grip is None:
            return None

        return {
            'id': id,
            'obj_type': obj_type,
            'speed': data['speed'],
            'grip_point': grip
        }

    def calculate_grip_point(self, pose2d, obj_type, timestamp, speed):     #TODO
        
        if self.previous_timestamp is None and self.previous_y is None and self.previous_x is None:
            self.previous_timestamp = timestamp
            self.previous_x = pose2d.x
            self.previous_y = pose2d.y
            return None

        timestamp_diff = timestamp - self.previous_timestamp
        self.previous_timestamp = timestamp

        offset_x, offset_y = GRIP_OFFSETS.get(obj_type, (10.0, 0.0))
        theta_rad = math.radians(pose2d.theta)

        grip_x = self.previous_x + offset_x * math.cos(theta_rad) - offset_y * math.sin(theta_rad)
        grip_y = self.previous_y + offset_x * math.sin(theta_rad) + offset_y * math.cos(theta_rad)

        #aktuelle errechnete Position

        current_x = grip_x + speed * timestamp_diff
        current_y = grip_y + speed * timestamp_diff

        return {
            'x': current_x,
            'y': current_y,
            'theta': 0,
        }