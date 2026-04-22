from ro45_portalrobot_interfaces.msg import RobotCmd
from ro45_portalrobot_interfaces.msg import RobotPos
import logging

class Init():
    def __init__(self):
        
        self.sub_robot_position = self.create_subscription(
            RobotPos,
            '/goal_data',
            self.set_rob_is_pos,
            10
        )   

        self.pub_robot_acc = self.create_publisher(RobotCmd, '/robot_command', 10)



        self.rob_is_pos = None

     def set_rob_is_pos(self, msg):       
        Xr_ist = msg.pos_x
        Yr_ist = msg.pos_y
        Zr_ist = msg.pos_z
        


    def endpunkt_anfahren():

        
        