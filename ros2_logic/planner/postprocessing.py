import time
from collections import OrderedDict

class PostProcessor:
    """Verwaltet eine geordnete Queue von Objekten und berechnet deren aktuellen Greifpunkt auf Basis von Geschwindigkeit und verstrichener Zeit."""

    def __init__(self):
        """Initialisiert die geordnete Objekt-Queue."""
        self.queue = OrderedDict()

    def add_obj_type(self, id, obj_type):
        """Fügt den Objekttyp eines Eintrags in die Queue ein oder aktualisiert ihn.

        Args:
            id (int): Objekt-ID (ID 0 wird verworfen)
            obj_type (int): Objekttyp (0=rejected, 1=cat, 2=unicorn)
        """

        if id == 0:
            print("type: rejected verworfen")
            return

        if id not in self.queue:
            self.queue[id] = {}

        self.queue[id]['obj_type'] = obj_type

    def add_future_position(self, id, pose2d, speed, timestamp):
        """Fügt Pose, Geschwindigkeit und Zeitstempel eines Eintrags in die Queue ein oder aktualisiert sie.

        Args:
            id (int): Objekt-ID (ID 0 wird verworfen)
            pose2d (geometry_msgs/Pose2D): Aktuelle 2D-Position
            speed (float): Objektgeschwindigkeit in m/s
            timestamp (float): Unix-Zeitstempel der Messung
        """

        if id == 0:
            print("Pos: rejected verworfen")
            return

        if id not in self.queue:
            self.queue[id] = {}

        self.queue[id]['pose2d'] = pose2d
        self.queue[id]['speed'] = speed
        self.queue[id]['timestamp']  = timestamp 

    def get_next(self):
        """Gibt das nächste vollständig beschriebene Objekt (Typ + Pose + Speed + Timestamp) als Dict zurück.

        Returns:
            dict: Ausgabe-Dict von build_output() oder None wenn kein vollständiges Objekt vorhanden
        """

        for id, data in self.queue.items():
            if 'obj_type' in data and 'pose2d' in data and 'speed' in data and 'timestamp' in data:
                return self.build_output(id, data)
        print("Daten nicht vollständig")
        return None

    def finish_obj(self, id):
        """Entfernt ein Objekt anhand seiner ID aus der Queue.

        Args:
            id (int): ID des abzuschließenden Objekts
        """

        try:
            self.queue.pop(id, None)
        except Exception as e:
            self.get_logger().error(f'ID:{str(id)} wurde schon entfernt')
            raise e

    def build_output(self, id, data):
        """Erstellt das Ausgabe-Dict mit berechnetem Greifpunkt für ein Objekt.

        Args:
            id (int): Objekt-ID
            data (dict): Queue-Eintrag mit 'obj_type', 'pose2d', 'speed', 'timestamp'

        Returns:
            dict: {'id', 'obj_type', 'speed', 'grip_point'} oder None wenn Greifpunkt nicht berechenbar
        """

        pose2d = data['pose2d']
        obj_type = data['obj_type']
        timestamp = data['timestamp']
        speed = data['speed']

        grip = self.calculate_current_position(pose2d, timestamp, speed)

        if grip is None:
            return
        
        #if grip['x'] < 0:
        #    self.finish_obj(id)
        #    print('Objekt ist außer Reichweite und wurde entfernt!!!')
        #    return

        return {
            'id': id,
            'obj_type': obj_type,
            'speed': data['speed'],
            'grip_point': grip
        }

    def calculate_current_position(self, pose2d, timestamp, speed):
        """Berechnet die aktuelle X-Position anhand von Ausgangsposition, Geschwindigkeit und verstrichener Zeit.

        Args:
            pose2d (geometry_msgs/Pose2D): Ausgangsposition mit x und y
            timestamp (float): Unix-Zeitstempel der Ausgangsposition
            speed (float): Objektgeschwindigkeit in m/s

        Returns:
            dict: {'x': float, 'y': float, 'theta': 0}
        """

        timestamp_aktuell = time.time()

        timestamp_diff = timestamp_aktuell - timestamp

        current_x = pose2d.x + speed * timestamp_diff
        current_y = pose2d.y 

        return {
            'x': current_x,
            'y': current_y,
            'theta': 0,
        }