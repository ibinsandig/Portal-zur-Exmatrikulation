import rclpy
from rclpy.node import Node
from chaos_interfaces.msg import GoalData
from chaos_interfaces.msg import GoalState
from ro45_portalrobot_interfaces.msg import RobotCmd
from ro45_portalrobot_interfaces.msg import RobotPos

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
        
        #self.sub_goal_data
        #self.sub_robot_position

        self.publisher_cmd = self.create_publisher(RobotCmd, '/robot_command', 10)
        self.publisher_state = self.create_publisher(GoalState, '/goal_state', 10)

        self.robot_cmd = RobotCmd()
        self.goal_state = GoalState()



        self.get_logger().info("Motion Node gestartet...")

    def callback1(self, msg):
        #goal_data kommt rein
        #Funktionsaufruf von move_logic mit (msg) übergabe
        pass

    def callback2(self, msg):
        pass

    def send_it_accel(self,x,y,z,picky):
        self.robot_cmd.accel_x = x
        self.robot_cmd.accel_y = y
        self.robot_cmd.accel_z = z
        self.robot_cmd.activate_gripper = picky

        self.publisher_cmd.publish(self.robot_cmd)

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