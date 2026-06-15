import math
from collections import deque

#
GRIP_OFFSETS = {
    0:  (0.0,  0.0),   # rejected
    1:  (15.0, 5.0),   # Cat
    27: (20.0, 10.0),  # Unicorn
}

class PostProcessor:
    def __init__(self):
        self.pending = {}
        self.queue = deque()
        self.queued_ids = set()

    def add_obj_type(self, id, obj_type):
        if id not in self.pending:
            self.pending[id] = {}
        self.pending[id]['obj_type'] = obj_type

        # Direkt verwerfen wenn rejected
        if obj_type == 0:
            self.pending.pop(id, None)
            return

        self.try_merge(id)

    def add_future_position(self, id, pose2d, speed):
        # Nicht hinzufügen wenn bereits als rejected verworfen
        if id not in self.pending and id not in self.queued_ids:
            self.pending[id] = {}

        self.pending[id]['pose2d'] = pose2d
        self.pending[id]['speed'] = speed
        self.try_merge(id)

    def try_merge(self, id):
        data = self.pending.get(id, {})
        if 'obj_type' in data and 'pose2d' in data and id not in self.queued_ids:
            self.queue.append(id)
            self.queued_ids.add(id)

    def get_next(self):
        if not self.queue:
            return None
        id = self.queue[0]
        return self.build_output(id)

    def finish_obj(self, id):
        if id in self.queued_ids:
            self.queue.remove(id)
            self.queued_ids.discard(id)
        self.pending.pop(id, None)

    def build_output(self, id):
        data = self.pending[id]
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

        # Offset wird entlang der Objektausrichtung rotiert
        grip_x = pose2d.x + offset_x * math.cos(theta_rad) - offset_y * math.sin(theta_rad)
        grip_y = pose2d.y + offset_x * math.sin(theta_rad) + offset_y * math.cos(theta_rad)

        return {
            'x': grip_x,
            'y': grip_y,
            'theta': 0,
        }