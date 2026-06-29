import time
from collections import OrderedDict

class PostProcessor:
    def __init__(self):
        self.queue = OrderedDict()

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
            if 'obj_type' in data and 'pose2d' in data and 'speed' in data and 'timestamp' in data:
                return self.build_output(id, data)
        print("Daten nicht vollständig")
        return None

    def finish_obj(self, id):
        self.queue.pop(id, None)


    def build_output(self, id, data):
        pose2d = data['pose2d']
        obj_type = data['obj_type']
        timestamp = data['timestamp']
        speed = data['speed']

        grip = self.calculate_current_position(pose2d, timestamp, speed)

        if grip is None:
            return
        
        if grip['x'] < 0:
            self.finish_obj(id)
            print('Objekt ist außer Reichweite und wurde entfernt!!!')
            return

        return {
            'id': id,
            'obj_type': obj_type,
            'speed': data['speed'],
            'grip_point': grip
        }

    def calculate_current_position(self, pose2d,  timestamp, speed):
        timestamp_aktuell = time.time()

        timestamp_diff = timestamp_aktuell - timestamp

        current_x = pose2d.x + speed * timestamp_diff
        current_y = pose2d.y 

        return {
            'x': current_x,
            'y': current_y,
            'theta': 0,
        }