import rclpy
from rclpy.node import Node
from chaos_interfaces.msg import ObjDataDeluxe
from chaos_interfaces.msg import ObjData

class Machine_learning(Node):
    def __init__(self):
        super().__init__('machine_learning')

        self.subscription = self.create_subscription(
            ObjData,
            '/obj_data',
            self.listener_callback,
            10)
        self.subscription
        
        self.publisher = self.create_publisher(ObjDataDeluxe, '/obj_data_deluxe', 10)

        self.get_logger().info("Machine Learning Node gestartet...")

    def listener_callback(self, msg):
        pub_data = msg
        self.publisher.publish(pub_data)

def main():
    rclpy.init(args=None)
    ml = Machine_learning()
    rclpy.spin(ml)
    ml.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()