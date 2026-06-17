import math
from collections import deque
import config_vm as cfg

class PostProcessor:
    def __init__(self):
        self.waitlist = {}
        self.main_queue = deque()


    def add_obj_type(self, id, obj_type):
        pass

    def add_future_position(self, id, pose2d, speed):
        pass

    def finish_obj(self, id):
        pass

    def get_next(self):
        pass

    def try_merge(self, id):
        pass

    def calculate_grip_point(self, pose2d, obj_type):
        pass
