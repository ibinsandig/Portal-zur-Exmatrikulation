import rclpy

from rclpy.node import Node
from geometry_msgs.msg import Point32
from std_msgs.msg import Bool

from ro45_portalrobot_interfaces.msg import RobotCmd
from ro45_portalrobot_interfaces.msg import RobotPos

from motion_controller.move_logic import MotionOrder # Benötigt 'pip install -e .'
from motion_controller.init import Init

# Bei Verbingungsproblemem mit dem Microcontrollern: > sudo apt-get remove -y brltty 

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
            self.gripper,    
            10)

        #========================================================

        self.publisher_cmd = self.create_publisher(RobotCmd, '/robot_command', 10)
        self.publisher_goal_reached = self.create_publisher(Bool, '/goal_reached', 10)
        self.publisher_init = self.create_publisher(Bool, '/init_done', 10)

        #========================================================
        
        #        Default Position des Roboters nach der INIT: 
        self.default_x_pos = 0.20
        self.default_y_pos = -0.08
        self.default_z_pos = 0.07               #Z-Achse nur zwischen 0.07 und 0.095
        
        #========================================================
        self.current_pos = None
        self.gripper_soll = False
        self.goal_reached = False
        
        self.init_state = "init_rise"
        self.pos_x_offset = 0.0
        self.pos_y_offset = 0.0
        self.pos_z_offset = 0.0

        #========================================================   
            
        self.motion_order = MotionOrder()
        self.init_order = Init() 

        #========================================================

        self.accel_x_over = 0.05
        self.accel_y_over = 0.05
        self.accel_z_over = 0.05
    

        #========================================================
        self.get_logger().info("Motion Node gestartet...")

        self.last_is_pos = None

#================================================================================================================

    def auftragseingang(self, msg):
        '''
        Callback-Funktion für eingehende Bewegungsaufträge via ROS-Topic /goal_coordinates.

        Empfängt eine Zielpositon (x, y, z) aus einer ROS-Nachricht und übergibt
        diese an die Funktion set_should_pos des motion_order-Objekts. Anschließend wird geprüft, ob der Roboter
        bereits an der Zielposition steht.

        Falls Soll- und Ist-Position übereinstimmen:
            - Sendet einen RobotCmd mit Beschleunigung 0 und aktuellem Greiferzustand
            - Veröffentlicht goal_reached = True auf dem entsprechenden Topic
            - Setzt has_goal auf False (kein aktiver Auftrag mehr)

        Falls Soll- und Ist-Position NICHT übereinstimmen:
            - Setzt has_goal auf True (Auftrag ist aktiv, Roboter muss noch fahren)

        '''
        Xr_soll = msg.x * 0.8
        Yr_soll = msg.y * 0.8 
        Zr_soll = msg.z
        self.motion_order.set_should_pos(Xr_soll, Yr_soll, Zr_soll)

       # if self.motion_order.should_is_comp():

       #     self.goal_reached = Bool()
       #     self.goal_reached.data = True
       #     self.publisher_goal_reached.publish(self.goal_reached)
       #     self.get_logger().info("auftragseingang: Roboter ist an Zielpos! x-0=0, y-0=0, z-0=0")        

#================================================================================================================
            
    def ist_pos_uebergabe(self, msg):       
        '''
        Callback für eingehende Ist-Positionen des Portalroboters via ROS-Topic /RobotPos.
        Taktgeber des gesamten Motion-Blocks auf Basis der eingehenden Portalroboter-Positionsdaten.

        Verarbeitet die Rohposition je nach aktuellem Initialisierungszustand (init_state):

        Einmalige Initialisierungsphasen:
            - 'init_rise'     : Beschleunigt Achsen für die Fahrt zur Startposition 
            - 'init_zero'     : Setzt Beschleunigung wieder auf 0
            - 'init_endpoint' : Erkennt Endlage und berechnet Offsets → wechselt zu 'init_done'

        Hauptloop:
            - 'init_done'     : Normalbetrieb. 
                                Rechnet Offset raus und übergibt Daten an Funktion set_is_pos des Motion_Order Objekts.
                                Berechnung der Beschleunigung über Reglerfunktion wanted_accel() im Motion_Order Objekt
                                Beschleunigungen werden auf ±0.1 begrenzt.
                                Bei erreichter Zielposition wird goal_reached publiziert.
        '''

        if self.init_state == "init_done":
            Xr_ist = msg.pos_x
            Yr_ist = msg.pos_y 
            Zr_ist = msg.pos_z 
            Xr_ist_offset = msg.pos_x - self.pos_x_offset
            Yr_ist_offset = msg.pos_y - self.pos_y_offset
            Zr_ist_offset = msg.pos_z - self.pos_z_offset
            self.motion_order.set_is_pos(Xr_ist_offset, Yr_ist_offset, Zr_ist_offset)
            self.get_logger().info("============== RoboKoordinaten+Offset: ==============")
            #self.get_logger().info(f"Xr+offset: {Xr_ist_offset}, Yr+offset: {Yr_ist_offset}, Zr+offset: {Zr_ist_offset}")
            #self.get_logger().info(f"Xr: {Xr_ist}, Yr: {Yr_ist}, Zr: {Zr_ist}")

#----------------Ab-hier-INIT-------------------------------------------------------

        if not self.init_state == "init_done":
            Xr_ist_raw = msg.pos_x
            Yr_ist_raw = msg.pos_y
            Zr_ist_raw = msg.pos_z
            self.init_order.set_init_is_pos(Xr_ist_raw, Yr_ist_raw, Zr_ist_raw)
            #self.get_logger().info(f"Bot-Rohwerte: {Xr_ist_raw}, {Yr_ist_raw}, {Zr_ist_raw}")

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
                
                default = Point32()
                default.x = self.default_x_pos
                default.y = self.default_y_pos
                default.z = self.default_z_pos
                self.auftragseingang(default)
                self.get_logger().info(f"Endlagen-Auftragseingang: {self.default_x_pos}, {self.default_y_pos}, {self.default_z_pos}")

                # default = Point32()
                # default.x = self.default_x_pos
                # default.y = self.default_y_pos
                # default.z = self.default_z_pos
                # self.auftragseingang(default)
                # self.get_logger().info(f"Endlagen-Auftragseingang: {self.default_x_pos}, {self.default_y_pos}, {self.default_z_pos}")
                #TODO: Anfahren des Default Punktes hat nicht direkt geklappt. Für den Meilenstein, ist er erstmal aber irrelevant. Das Problem hier könnte das Aufrufen der Callback-Funktion aus dieser hier sein. Evt noch mal testen.

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
            accelofx, accelofy, accelofz = self.motion_order.wanted_accel()

            if (accelofx) >= 0.08:
                self.accel_x_over = 0.08
                #self.get_logger().info("accel_x > 0.08!")
            elif (accelofx <= -0.08):
                self.accel_x_over = -0.08
                #self.get_logger().info("accel_x < -0.08!")
            else: 
                self.accel_x_over = accelofx

            if (accelofy) >= 0.08:
                self.accel_y_over = 0.08
                #self.get_logger().info("accel_y > 0.08!")
            elif (accelofy <= -0.08):
                self.accel_y_over = -0.08
                #self.get_logger().info("accel_y < -0.08!")
            else: 
                self.accel_y_over = accelofy

            if (accelofz) >= 0.08:
                self.accel_z_over = 0.08
                #self.get_logger().info("accel_z > 0.08!")
            elif (accelofz <= -0.08):
                self.accel_z_over = -0.08
                #self.get_logger().info("accel_z < -0.08!")
            else: 
                self.accel_z_over = accelofz


            robot_cmd = RobotCmd()
            robot_cmd.accel_x = self.accel_x_over
            robot_cmd.accel_y = self.accel_y_over
            robot_cmd.accel_z = self.accel_z_over
            robot_cmd.activate_gripper = self.gripper_soll     
            self.publisher_cmd.publish(robot_cmd)
            self.get_logger().info("Ist_Pos_übergabe: accel x,y,z übergeben")

            self.publish_reached(self.motion_order.should_is_comp())

  #===============================================================================================================

    def publish_reached(self, reached):
        goal_reached = Bool()
        goal_reached.data = reached
        self.publisher_goal_reached.publish(goal_reached)

#================================================================================================================

    def gripper(self, msg):
        '''
        Empfangen des Greiferzustands über ROS-Topic /goal_gripper.
        '''
        self.gripper_soll = msg.data

#================================================================================================================

def main():
    rclpy.init(args=None)
    motion = Motion()
    rclpy.spin(motion)
    motion.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()