from collections import deque
import statistics

class CoordinatesPrediction:
    """Schätzt die Objektgeschwindigkeit aus X-Koordinatenmessungen mittels gleitendem Median-Filter."""

    def __init__(self):
        """Initialisiert Mess-Queue, Geschwindigkeits-Buffer (Größe 5) und aktuelle Objekt-ID."""
        self.buffer_size = 5
        self.current_id = None
        self.queue = deque()        # speichert (x, t) Tupel
        self.speed_buffer = deque() # speichert berechnete Einzelgeschwindigkeiten

    def add_measurement(self, id, x, t):
        """Fügt eine Messung hinzu und gibt die per Median geglättete Geschwindigkeit zurück.

        Args:
            id (int): Objekt-ID (Queue wird bei neuer ID geleert)
            x (float): X-Weltkoordinate in Metern
            t (float): Zeitstempel in Sekunden

        Returns:
            dict: {'id': int, 'speed': float} oder None bei zu wenig Messungen / identischen Zeitstempeln
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