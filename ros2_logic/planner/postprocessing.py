import time
from collections import OrderedDict

class PostProcessor:
    """
    Verwaltet eine geordnete Warteschlange von Objekten und berechnet deren aktuelle Position.

    Kombiniert Objekttyp, Pose, Geschwindigkeit und Zeitstempel zu einem vollständigen
    Ausgabedatensatz. Die aktuelle Position wird zum Abfragezeitpunkt live aus der
    gespeicherten Pose und Geschwindigkeit extrapoliert.
    """
    def __init__(self):
        self.queue = OrderedDict()

    def add_obj_type(self, id, obj_type):
        """
        Speichert den Objekttyp für eine gegebene ID in der Warteschlange.

        Objekte mit ID 0 (rejected) werden ignoriert.

        Args:
            id:       Eindeutige Objekt-ID.
            obj_type: Klassifikationsergebnis des Objekts (z.B. 'cat', 'unicorn').
        """

        if id == 0:
            print("type: rejected verworfen")
            return

        if id not in self.queue:
            self.queue[id] = {}

        self.queue[id]['obj_type'] = obj_type

    def add_future_position(self, id, pose2d, speed, timestamp):
        """
        Speichert Pose, Geschwindigkeit und Zeitstempel eines Objekts in der Warteschlange.

        Objekte mit ID 0 (rejected) werden ignoriert.

        Args:
            id:        Eindeutige Objekt-ID.
            pose2d:    Pose-Objekt mit x- und y-Koordinaten (Weltkoordinaten).
            speed:     Geschwindigkeit des Objekts in x-Richtung.
            timestamp: Zeitstempel der Messung (Unix-Zeit als float).
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
        """
        Gibt das nächste vollständige Objekt aus der Warteschlange zurück.

        Durchsucht die Warteschlange nach dem ersten Eintrag, der alle benötigten
        Felder (obj_type, pose2d, speed, timestamp) enthält, und gibt dessen
        berechnete Ausgabe zurück.

        Returns:
            dict | None: Ausgabe-Dictionary mit 'id', 'obj_type', 'speed' und
                         'grip_point', oder None wenn kein vollständiger Eintrag vorliegt.
        """
        for id, data in self.queue.items():
            if 'obj_type' in data and 'pose2d' in data and 'speed' in data and 'timestamp' in data:
                return self.build_output(id, data)
        print("Daten nicht vollständig")
        return None

    def finish_obj(self, id):
        """
        Entfernt ein abgearbeitetes Objekt aus der Warteschlange.

        Args:
            id: Eindeutige Objekt-ID, die entfernt werden soll.

        Raises:
            Exception: Wird weitergegeben, falls die ID bereits entfernt wurde.
        """
        try:
            self.queue.pop(id, None)
        except Exception as e:
            self.get_logger().error(f'ID:{str(id)} wurde schon entfernt')
            raise e

    def build_output(self, id, data):
        """
        Erstellt das Ausgabe-Dictionary für ein Objekt mit aktueller Greifposition.

        Args:
            id:   Eindeutige Objekt-ID.
            data: Dictionary mit 'pose2d', 'obj_type', 'timestamp' und 'speed'.

        Returns:
            dict | None: Dictionary mit 'id', 'obj_type', 'speed' und 'grip_point',
                         oder None wenn die Positionsberechnung fehlschlägt.
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
        """
        Extrapoliert die aktuelle Position eines Objekts zum jetzigen Zeitpunkt.

        Berechnet die verstrichene Zeit seit dem gespeicherten Zeitstempel und
        schätzt die aktuelle x-Position anhand der bekannten Geschwindigkeit.
        Die y-Position wird als konstant angenommen.

        Args:
            pose2d:    Pose-Objekt mit x- und y-Koordinaten der letzten Messung.
            timestamp: Zeitstempel der letzten Messung (Unix-Zeit als float).
            speed:     Geschwindigkeit des Objekts in x-Richtung.

        Returns:
            dict: Dictionary mit 'x', 'y' und 'theta' (aktuell immer 0).
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