import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point32
from std_msgs.msg import Bool

from ro45_portalrobot_interfaces.msg import RobotCmd
from ro45_portalrobot_interfaces.msg import RobotPos

from motion_controller.move_logic import MotionOrder #Hier nochmal schauen ob nicht doch ros2_logic.move_logic....
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
        self.sub_init_run = self.create_subscription(
            Bool,
            '/init_run',
            self.init_run,
            10)

        #========================================================

        self.publisher_cmd = self.create_publisher(RobotCmd, '/robot_command', 10)
        self.publisher_state = self.create_publisher(bool, '/goal_state', 10)

        #========================================================

        self.robot_cmd = RobotCmd()
        self.motion_order = MotionOrder()
        self.init_order = Init()    
        
        #========================================================
        self.current_pos = None
        self.has_goal = False
        self.gripper_soll = False
        
        self.init_state = "init_start"
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
            self.robot_cmd.accel_x = 0.0
            self.robot_cmd.accel_y = 0.0
            self.robot_cmd.accel_z = 0.0
            self.robot_cmd.activate_gripper = self.gripper_soll
            self.publisher_cmd.publish(self.robot_cmd)

            self.goal_state.job_finished = True
            self.publisher_state.publish(self.goal_state)  
            #self.has_goal = True ? TODO:
            self.get_logger().info("CB1: Robter ist bereits am Ziel ")        
            
        else:
            self.has_goal = True
            self.get_logger().info("CB1: Onetheway-flag ist True")

#================================================================================================================
            
    def ist_pos_uebergabe(self, msg):       #TODO: HIER KOMMEN VERMUTLICH NUR INDIREKTE DATEN AN. Umrechnen oder glätten der Werte?
        Xr_ist = msg.pos_x
        Yr_ist = msg.pos_y
        Zr_ist = msg.pos_z
        self.motion_order.set_is_pos(Xr_ist, Yr_ist, Zr_ist)
        self.init_order.set_rob_is_pos(Xr_ist, Yr_ist, Zr_ist)
        self.get_logger().info("========  Roboterdaten: ")
        self.get_logger().info(str(msg))

#----------------Ab-hier-INIT-------------------------------------------------------

        if self.init_state == "init_start":
            accel_x, accel_y, accel_z = self.init_order.endpoint_accel_rise()
            self.publisher_cmd(accel_x, accel_y, accel_z, False)
            self.init_state == "accel_rise"

        elif self.init_state == "accel_rise":
            accel_x, accel_y, accel_z = self.init_order.endpoint_accel_zero()
            self.publisher_cmd(accel_x, accel_y, accel_z, False)
            self.init_state == "accel_zero"

        elif self.init_state == "accel_zero":
            endlagenerreicht = self.init_order.endablageerreicht()
            if endlagenerreicht == True:
                self.pos_x_offset, self.pos_y_offset, self.pos_z_offset = self.init_order.offset_calc()
                #TODO: In der MAINY jetzt noch bei der init phase auf Default_POS fahren!
                self.init_state == "init_done"
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

    def init_run(self, msg):
        if msg.data == True:
        
            init_accel_x, init_accel_y, init_accel_z  = self.init_order.endpunkt_anfahren()  #Ab hier wird die Flag "endlagenabfrage" =True gesetzt.
            self.robot_cmd.accel_x = init_accel_x
            self.robot_cmd.accel_y = init_accel_y
            self.robot_cmd.accel_z = init_accel_z
            self.publisher_cmd.publish(self.robot_cmd)

            

#================================================================================================================

def main():
    rclpy.init(args=None)
    motion = Motion()
    rclpy.spin(motion)
    motion.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()