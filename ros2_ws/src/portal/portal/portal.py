import rclpy
from rclpy.node import Node
from chaos_interfaces.msg import GoalData
from ro45_portalrobot_interfaces.msg import RobotCmd
from ro45_portalrobot_interfaces.msg import RobotPos
class Portal(Node):
    def __init__(self):
        super().__init__('Portal')

        self.sub1 = self.create_subscription(
            GoalData,
            '/goal_data',
            self.callback1,
            10)
        self.sub2 = self.create_subscription(
            RobotPos,
            '/robot_position',
            self.callback2,
            10)

        self.publisher = self.create_publisher(RobotCmd, 'robot_command', 10)

        self.get_logger().info("Portal Node gestartet...")

    def callback1(self, msg):
        pass

    def callback2(self, msg):
        pass

def main():
    rclpy.init(args=None)
    glados = Portal()
    rclpy.spin(glados)
    glados.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()