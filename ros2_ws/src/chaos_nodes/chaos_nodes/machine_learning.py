import rclpy
from rclpy.node import Node
from chaos_interfaces.msg import ObjDataDeluxe
from chaos_interfaces.msg import ObjData

class Machine_learning(Node):
    
    def __init__(self):
        super().__init__('machine_learning')

        self.sub_obj_data = self.create_subscription(
            ObjData,
            '/obj_data',
            self.listener_callback,
            10)
        self.sub_obj_data
        
        self.pub_obj_data_deluxe = self.create_publisher(ObjDataDeluxe, '/obj_data_deluxe', 10)

        self.get_logger().info("Machine Learning Node gestartet...")

    def listener_callback(self, msg):
        pub_data_before = msg

        pub_data_test = ObjDataDeluxe()

        self.pub_obj_data_deluxe.publish(pub_data_test)

def main():
    rclpy.init(args=None)
    ml = Machine_learning()
    rclpy.spin(ml)
    ml.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()