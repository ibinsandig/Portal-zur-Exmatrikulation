class CoordinatesPrediction:
    def __init__(self):
        self.history = {}  # Maps id -> (last_x, last_t)


    def calculate_speed_with_ID(self, id, x, t):
        if id not in self.history:
            self.history[id] = (x, t)
            return -100

        last_x, last_t = self.history[id]
        if t == last_t:
            return -100  # zero devision verhindern
        speed = (x - last_x) / (t - last_t)
        self.history[id] = (x, t)

        return speed