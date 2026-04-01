import rclpy
from rclpy.node import Node
from chaos_interfaces.msg import GoalData
class Portal(Node):
    def __init__(self):
        super().__init__('Portal')

        self.subscription = self.create_subscription(
            GoalData,
            '/goal_data',
            self.listener_callback,
            10)
        self.subscription


        self.get_logger().info("Portal Node gestartet...")

    def listener_callback(self, msg):
        pass

def main():
    rclpy.init(args=None)
    glados = Portal()
    rclpy.spin(glados)
    glados.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()