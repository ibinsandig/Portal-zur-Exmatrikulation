from ro45_portalrobot_interfaces.msg import RobotCmd
from ro45_portalrobot_interfaces.msg import RobotPos
import logging

#========================================================
    #Endpunktanfahren Beschleunigung: 
init_accel_x = 0.005
init_accel_y = 0.005
init_accel_z = -0.005   #Bei Z-Positiv nach unten! KEIN ANSCHLAG!

    #Threshhold für Bewegungsabfrage:
th = 0.001

#========================================================
class Init():
    def __init__(self):
        
    #========================================================
    
        self.logger = logging.getLogger("Init")
        logging.basicConfig(level=logging.INFO)

    #========================================================
        self.sub_robot_position = self.create_subscription(
            RobotPos,
            '/robot_position',
            self.set_rob_is_pos,
            10
        )   

        self.Xr_ist = 0.0
        self.Yr_ist = 0.0
        self.Zr_ist = 0.0
    #========================================================

        self.pub_robot_acc = self.create_publisher(RobotCmd, '/robot_command', 10)

        self.counter = 0
        self.endlageerreicht = False
        self.endlagenabfrage = False
        

    def set_rob_is_pos(self, msg): 
        if self.endlagenabfrage:
            if ((abs(msg.pos_x - self.Xr_ist) < th) 
                or (abs(msg.pos_y - self.Yr_ist) < th) 
                or (abs(msg.pos_z - self.Zr_ist) < th)):  
                self.counter += 1
                if self.counter >= 3:
                    self.endlageerreicht = True

        self.Xr_ist = msg.pos_x
        self.Yr_ist = msg.pos_y
        self.Zr_ist = msg.pos_z
        


    def endpunkt_anfahren(self):
        robot_cmd = RobotCmd()
        self.robot_cmd.accel_x = init_accel_x
        self.robot_cmd.accel_y = init_accel_y
        self.robot_cmd.accel_z = init_accel_z
        self.pub_robot_acc.publish(robot_cmd)
        self.logger.info(f"Endpunkte werden angefahren. Beschleunigung = {init_accel}")
        self.endlagenabfrage = True #Solange dieses Flag nicht gesetzt ist, wird die "set_rob_is_pos"-Funktion niemals "self.endlageereicht = True" setzten




