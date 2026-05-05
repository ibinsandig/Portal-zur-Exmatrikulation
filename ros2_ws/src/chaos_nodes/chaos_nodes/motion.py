import rclpy

from rclpy.node import Node
from geometry_msgs.msg import Point32
from std_msgs.msg import Bool

from ro45_portalrobot_interfaces.msg import RobotCmd
from ro45_portalrobot_interfaces.msg import RobotPos

from motion_controller.move_logic import MotionOrder # Benötigt 'pip install -e .'
from motion_controller.init import Init

# Bei Verbingungsproblemem mit dem Microcontrollern: > sudo apt-get remove -y brltty (bereits passiert bei PaW)

#================================================================================================================
class Motion(Node):
    def __init__(self):
        super().__init__('Motion')

        #========================================================

        self.sub_goal_coordinates = self.create_subscription(
            Point32,   
            '/goal_coordinates',
            self.auftragseingang,
            10)
        self.sub_robot_position = self.create_subscription(
            RobotPos,
            '/robot_position',
            self.ist_pos_uebergabe,
            10)
        self.sub_goal_gripper = self.create_subscription(
            Bool,
            '/goal_gripper',
            callbackIII,    #Name kommt, bei erstellung der Funktion
            10)

        #========================================================

        self.publisher_cmd = self.create_publisher(RobotCmd, '/robot_command', 10)
        self.publisher_state = self.create_publisher(Bool, '/goal_state', 10)
        self.publisher_init = self.create_publisher(Bool, '/init_done', 10)

        #========================================================

        self.motion_order = MotionOrder()
        self.init_order = Init()    
        
        #========================================================
        self.current_pos = None
        self.has_goal = False
        self.gripper_soll = False
        
        self.init_state = "init_rise"
        self.pos_x_offset = 0.0
        self.pos_y_offset = 0.0
        self.pos_z_offset = 0.0

        #========================================================   


        #========================================================
        self.get_logger().info("Motion Node gestartet...")

#================================================================================================================

    def auftragseingang(self, msg):
        '''
        Bringt den Auftragseingang. Setzt bei noch nicht erreichtem Ziel ein Flag. 
        Gripper FLAG für AN/AUS wird in Instanzvariable gesetzt. 
        '''
        Xr_soll = msg.x
        Yr_soll = msg.y
        Zr_soll = msg.z
        self.gripper_soll = msg.grip
        self.motion_order.set_should_pos(Xr_soll, Yr_soll, Zr_soll)

        if self.motion_order.should_is_comp():
            robot_cmd = RobotCmd()
            robot_cmd.accel_x = 0.0
            robot_cmd.accel_y = 0.0
            robot_cmd.accel_z = 0.0
            robot_cmd.activate_gripper = self.gripper_soll
            self.publisher_cmd.publish(robot_cmd)

            self.goal_state.job_finished = True
            self.publisher_state.publish(self.goal_state)  
            #self.has_goal = True ? TODO:
            self.get_logger().info("auftragseingang: Roboter ist an bereits an Zielpos! x-0=0, y-0=0, z-0=0")        
            
        else:
            self.has_goal = True
            self.get_logger().info("auftragseingang: has_goal Flag ist gesetzt")

#================================================================================================================
            
    def ist_pos_uebergabe(self, msg):       #TODO: HIER KOMMEN VERMUTLICH NUR INDIREKTE DATEN AN. Umrechnen oder glätten der Werte?
        '''
        Empfängt die IST_Position des Portalroboters. 
        Erfüllt die Funktion für die Initialsisierung und den normalen ablauf.

        '''


        if self.init_state == "init_done":
            Xr_ist_offset = msg.pos_x - self.pos_x_offset
            Yr_ist_offset = -(msg.pos_y - self.pos_y_offset) #TODO Testen ob beim verfahren vom NULLPUNKT die Zahl kleiner wird!
            Zr_ist_offset = msg.pos_z - self.pos_z_offset
            self.motion_order.set_is_pos(Xr_ist_offset, Yr_ist_offset, Zr_ist_offset)
            self.get_logger().info("============== RoboKoordinaten+Offset: ==============")
            self.get_logger().info(f"Xr+offset: {Xr_ist_offset}, Yr+offset: {Yr_ist_offset}, Zr+offset: {Zr_ist_offset}")

#----------------Ab-hier-INIT-------------------------------------------------------

        if not self.init_state == "init_done":
            Xr_ist_raw = msg.pos_x
            Yr_ist_raw = msg.pos_y
            Zr_ist_raw = msg.pos_z
            self.init_order.set_init_is_pos(Xr_ist_raw, Yr_ist_raw, Zr_ist_raw)

        if self.init_state == "init_rise":
            accel_x, accel_y, accel_z = self.init_order.endpoint_accel_rise()
            robot_cmd = RobotCmd()
            robot_cmd.accel_x = accel_x
            robot_cmd.accel_y = accel_y
            robot_cmd.accel_z = accel_z
            robot_cmd.activate_gripper = self.gripper_soll
            self.publisher_cmd.publish(robot_cmd)

            if self.init_order.counter_start() == True:
                self.init_state = "init_zero"
                self.get_logger().info("state -> init_zero")

        elif self.init_state == "init_zero": 
            accel_x, accel_y, accel_z = self.init_order.endpoint_accel_zero()
            robot_cmd = RobotCmd()
            robot_cmd.accel_x = accel_x
            robot_cmd.accel_y = accel_y
            robot_cmd.accel_z = accel_z
            robot_cmd.activate_gripper = self.gripper_soll
            self.publisher_cmd.publish(robot_cmd)

            if self.init_order.counter_rise() == True:
                self.init_state = "init_endpoint"
                self.get_logger().info("state -> init_endpoint")

        elif self.init_state == "init_endpoint":
            self.init_order.endablagenabfrage()
            endlagenerreicht = self.init_order.endablageerreicht()
            if endlagenerreicht == True:
                self.pos_x_offset, self.pos_y_offset, self.pos_z_offset = self.init_order.offset_calc()
                #TODO: In der MAINY jetzt noch bei der init phase auf Default_POS fahren! Oder Doch hier?
                self.init_state = "init_done"
                self.get_logger().info("state -> init_done")
                msg = Bool()
                msg.data = True
                self.publisher_init.publish(msg) 
            else: 
                pass

#----------------Bis-hier-INIT-------------------------------------------------------
#----------------Ab-hier-Punkt-anfahren----------------------------------------------

        elif self.init_state == "init_done": 
            if self.has_goal == True: 

                if not self.motion_order.should_is_comp():
                    accelofx, accelofy, accelofz = self.motion_order.wanted_accel()

                    if (abs(accelofx) >= 0.1) or (abs(accelofy) >= 0.1) or (abs(accelofz) >= 0.1):
                        self.get_logger().info("Berechnete Beschleunigung ist ueber 0.1!")
                        # TODO: klammern weg. Hier soll beschleunigung eher begrenzt und weiter gegeben werden. Nicht einfach weggeschluckt. Werte würden ignoieriert und die Geschwindigkeit unverändert!
                        return
                    
                    else:
                        self.robot_cmd.accel_x = accelofx
                        self.robot_cmd.accel_y = accelofy
                        self.robot_cmd.accel_z = accelofz
                        self.robot_cmd.activate_gripper = self.gripper_soll     #TODO: Greifer-schließ logic muss überdacht werden - evt eigene Funktion
                        self.publisher_cmd.publish(self.robot_cmd)
                        self.get_logger().info("CB2: Neue Beschleunigung wurde übergeben")
                        self.get_logger().info(str(self.robot_cmd))
                
                else:
                    self.goal_state.job_finished = True
                    self.publisher_state.publish(self.goal_state)

#================================================================================================================

def callbackIII():
    pass

#================================================================================================================

def main():
    rclpy.init(args=None)
    motion = Motion()
    rclpy.spin(motion)
    motion.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()