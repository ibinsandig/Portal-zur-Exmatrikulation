from collections import deque

class PostProcessor:
    def __init__(self):
         # Puffer
        self.pending = {}
        # First in First out
        self.queue = deque()
        
        self.queued_ids = set()

    def add_obj_type(self, id, obj_type):
        """ObjType-Daten einpflegen."""
        if id not in self.pending:
            self.pending[id] = {}
        self.pending[id]['obj_type'] = obj_type
        self.try_merge(id)

    def add_position(self, id, pose2d, speed):
        """FuturePosition-Daten einpflegen."""
        if id not in self.pending:
            self.pending[id] = {}
        self.pending[id]['pose2d'] = pose2d
        self.pending[id]['speed'] = speed
        self.try_merge(id)

    def try_merge(self, id):
        """Wenn beide Topics für eine ID vorliegen → in Queue."""
        data = self.pending.get(id, {})
        if 'obj_type' in data and 'pose2d' in data and id not in self.queued_ids:
            self.queue.append(id)
            self.queued_ids.add(id)

    def get_next(self):
        """Gibt das älteste Objekt zurück (ohne es zu entfernen)."""
        if not self.queue:
            return None
        id = self.queue[0]
        return self.build_output(id)

    def finish_obj(self, id):
        """Objekt nach Bestätigung aus Queue und Puffer entfernen."""
        if id in self.queued_ids:
            self.queue.remove(id)
            self.queued_ids.discard(id)
        self.pending.pop(id, None)

    def build_output(self, id):
        data = self.pending[id]
        return {
            'id': id,
            'obj_type': data['obj_type'],
            'pose2d': data['pose2d'],
            'speed': data['speed'],
        }
    def calculate_grip_point(self, pose2d, type):
        #TODO ANhand des obj type und dem theta in pose2d wir ein neuer gripping point für das objekt berechnet
        pass