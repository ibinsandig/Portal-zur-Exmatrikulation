from collections import deque
import statistics

class CoordinatesPrediction:
    """
    Schätzt die Geschwindigkeit eines sich bewegenden Objekts aus aufeinanderfolgenden Messungen.

    Puffert Positions- und Zeitmessungen pro Objekt-ID und berechnet eine
    geglättete Geschwindigkeit mittels Median über einen gleitenden Buffer.
    """
    def __init__(self):
        self.buffer_size = 5
        self.current_id = None
        self.queue = deque()        # speichert (x, t) Tupel
        self.speed_buffer = deque() # speichert berechnete Einzelgeschwindigkeiten

    def add_measurement(self, id, x, t):
        """
        Fügt eine neue Positionsmessung hinzu und berechnet die geglättete Geschwindigkeit.

        Bei einer neuen ID werden alle bisherigen Puffer geleert. Die Geschwindigkeit
        wird aus den letzten zwei Messpunkten berechnet und über einen Median-Filter
        der Größe buffer_size geglättet.

        Args:
            id:  Eindeutige Objekt-ID.
            x:   Aktuelle x-Position des Objekts (in Weltkoordinaten).
            t:   Aktueller Zeitstempel der Messung.

        Returns:
            dict | None: Dictionary mit 'id' und 'speed' (geglättete Geschwindigkeit),
                         oder None wenn noch keine zwei Messpunkte vorliegen bzw.
                         der Zeitunterschied null ist.
        """

        # Neue ID -> Queue wird geleert
        if id != self.current_id:
            self.queue.clear()
            self.speed_buffer.clear()
            self.current_id = id

        self.queue.append((x, t))

        # Abbruch bei zu wenig ids
        if len(self.queue) < 2:
            return None

        # Geschwindigkeit zwischen den letzten zwei Punkten berechnen
        x_prev, t_prev = self.queue[-2]
        x_curr, t_curr = self.queue[-1]

        if t_curr == t_prev:
            return None  # Division durch 0 verhindern!!!!!!

        speed = (x_curr - x_prev) / (t_curr - t_prev)

        # begrenzter buffer 
        self.speed_buffer.append(speed)
        if len(self.speed_buffer) > self.buffer_size:
            self.speed_buffer.popleft()

        # Median über alles aus speed_buffer
        smoothed_speed = statistics.median(self.speed_buffer)

        return {
            'id': id,
            'speed': smoothed_speed,
        }