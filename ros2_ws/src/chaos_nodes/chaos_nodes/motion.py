import rclpy
from rclpy.node import Node
from chaos_interfaces.msg import GoalData
from chaos_interfaces.msg import GoalState
from ro45_portalrobot_interfaces.msg import RobotCmd
from ro45_portalrobot_interfaces.msg import RobotPos
from motion_controller.move_logic import MotionOrder #Hier nochmal schauen ob nicht doch ros2_logic.move_logic....

class Motion(Node):
    def __init__(self):
        super().__init__('Motion')

        self.sub_goal_data = self.create_subscription(
            GoalData,
            '/goal_data',
            self.callback1,
            10)
        self.sub_robot_position = self.create_subscription(
            RobotPos,
            '/robot_position',
            self.callback2,
            10)
        
        self.current_pos = None

        self.publisher_cmd = self.create_publisher(RobotCmd, '/robot_command', 10)
        self.publisher_state = self.create_publisher(GoalState, '/goal_state', 10)

        self.robot_cmd = RobotCmd()
        self.goal_state = GoalState() #Warum brauchen wir ne CustomMSG für EINEN BOOL

        self.motion_order = MotionOrder()

        self.ontheway = False
        self.gripper_soll = False

        self.get_logger().info("Motion Node gestartet...")

    def callback1(self, msg):
        '''
        Bringt den Auftragseingang. Setzt bei noch nicht erreichtem Ziel ein Flag. 
        Gripper FLAG für AN/AUS wird in Instanzvariable gesetzt. 
        '''
        Xr_soll = msg.x
        Yr_soll = msg.y
        Zr_soll = msg.z
        self.gripper_soll = msg.grip
        self.motion_order.getter_should_pos(Xr_soll, Yr_soll, Zr_soll)
        
        if self.motion_order.should_is_comp(): 
            self.robot_cmd.accel_x = 0.0
            self.robot_cmd.accel_y = 0.0
            self.robot_cmd.accel_z = 0.0
            self.robot_cmd.activate_gripper = gripper_soll
            self.publisher_cmd.publish(self.robot_cmd)

            self.goal_state.job_finished = True
            self.publisher_state.publish(self.goal_state)          
            
        else:
            self.ontheway = True


            
    def callback2(self, msg):       #TODO: HIER KOMMEN VERMUTLICH NUR INDIREKTE DATEN AN.... heißt heir muss eine sauber vorverarbeitung mit evt umrechnung ins Koordinatensystem erfolgen.... danke benji
        Xr_ist = msg.pos_x
        Yr_ist = msg.pos_y
        Zr_ist = msg.pos_z
        self.motion_order.getter_is_pos(Xr_ist, Yr_ist, Zr_ist)


        if self.ontheway == True: 

            if not self.motion_order.should_is_comp():
                accelofx, accelofy, accelofz = self.motion_order.wanted_accel()

                if accelofx >= 0.1 or accelofy >= 0.1 or accelofz >= 0.1:
                    self.get_logger().info("Berechnete Beschleunigung ist ueber 0.1!")
                    return
                
                else:
                    self.robot_cmd.accel_x = accelofx
                    self.robot_cmd.accel_y = accelofy
                    self.robot_com.accel_z = accelofz
                    self.robot_cmd.activate_gripper = self.gripper_soll     #TODO: Kann evt auch als einzele Logic optimiert werden.
                    self.publisher_cmd.publish(self.robot_cmd)
            
            else:
                self.ontheway = False
                self.goal_state.job_finished = True
                self.publisher_state.publish(self.goal_state)


#   def send_state(self, state):
#       self.goal_state.job_finished = state
#       self.publisher_state.publish(self.goal_state)


def main():
    rclpy.init(args=None)
    motion = Motion()
    rclpy.spin(motion)
    motion.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()