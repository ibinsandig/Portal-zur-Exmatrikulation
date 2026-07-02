
class Controller():
    def __init__(self, kp, kd):
        self.last_error = 0.0
        self.first = True
        self.kp = kp
        self.kd = kd

    def compute(self, goal_pos, curr_pos, delta_t):
        error = goal_pos - curr_pos

        if self.first:
            speed = 0.0
            self.first = False
        else:
            speed = (error - self.last_error) / delta_t

        self.last_error = error

        accel = self.kp * error + self.kd * speed

        return accel
    
    

