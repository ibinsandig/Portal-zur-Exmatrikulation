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

        self.get_logger().info("Motion Node gestartet...")

    def callback1(self, msg):
        Xr_soll = msg.accel_x
        Yr_soll = msg.accel_y
        Zr_soll = msg.accel_z
        gripper_soll = msg.activate_gripper
        motion_order.getter_should_pos(Xr_soll, Yr_soll, Zr_soll, gripper_soll)
        if (should_is_comp == True) {
            self.robot_cmd.accel_x = 0.0
            self.robot_cmd.accel_y = 0.0
            self.robot_cmd.accel_z = 0.0
            self.robot_cmd.activate_gripper = gripper_soll
            self.publisher_cmd.publish(self.robot_cmd)
            self.goal_state.job_finished = True
            self.publisher_state.publish(self.goal_state)          
        }
        else {
            #Funktion zur errechnung der Beschleunigung aller Achsen
            self.robot_cmd.accel_x = x
            self.robot_cmd.accel_y = y
            self.robot_cmd.accel_z = z
            self.robot_cmd.activate_gripper = picky 
            
            self.publisher_cmd.publish(self.robot_cmd)
        }

    def callback2(self, msg):
        Xr_ist = msg.pos_x
        Yr_ist = msg.pos_y
        Zr_ist = msg.pos_z
        motion_order.getter_is_pos(Xr_ist, Yr_ist, Zr_ist)


#    def send_it_accel(self,x,y,z,picky):       "Wird vorrausichlicht oben in die Callback1 integriert"
#        self.robot_cmd.accel_x = x
#        self.robot_cmd.accel_y = y
#        self.robot_cmd.accel_z = z
#        self.robot_cmd.activate_gripper = picky
#        self.publisher_cmd.publish(self.robot_cmd)


    def send_state(self, state):
        self.goal_state.job_finished = state

        self.publisher_state.publish(self.goal_state)

def main():
    rclpy.init(args=None)
    glados = Portal()
    rclpy.spin(glados)
    glados.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()