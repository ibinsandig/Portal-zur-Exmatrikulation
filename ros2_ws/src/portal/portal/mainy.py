import rclpy
from rclpy.node import Node
from chaos_interfaces.msg import GoalData, GoalDataDeluxe
class Mainy(Node):
    def __init__(self):

        super().__init__('Mainy')

        self.subscription = self.create_subscription(
            GoalDataDeluxe,
            '/obj_data_deluxe',
            self.listener_callback,
            10)
        
        self.subscription
        
        self.publisher = self.create_publisher(GoalData, '/goal_data', 10)

        self.get_logger().info("Mainy Node gestartet...")

    def listener_callback(self, msg):
        pub_data = msg
        self.publisher.publish(pub_data)

def main():
    rclpy.init(args=None)
    main = Mainy()
    rclpy.spin(main)
    main.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()