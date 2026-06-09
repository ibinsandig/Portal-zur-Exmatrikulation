class CoordinatesPrediction:
    def __init__(self):
        self.last_x = None
        self.last_t = None
        self.last_id = None


    def calculate_speed_with_ID(self, id, x, t):
        if self.last_id is None or self.last_id != id:
            self.last_id = id
            self.last_x = x
            self.last_t = t
            return -100

        if self.last_x is not None and self.last_t is not None:  # ← or → and
            if t == self.last_t:                                  # ← guard against zero division
                return -100
            speed = (x - self.last_x) / (t - self.last_t)
            self.last_x = x
            self.last_t = t
            return speed

        return -100  # ← fallback if somehow neither condition hit