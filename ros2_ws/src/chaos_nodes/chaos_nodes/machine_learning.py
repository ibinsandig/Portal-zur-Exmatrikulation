import rclpy
from rclpy.node import Node
from chaos_topics.msg import ObjType
from chaos_topics.msg import ObjFeatures
from machine_learning.classify import Classifier

class Machine_learning(Node):
    
    def __init__(self):
        super().__init__('machine_learning')

        self.sub_obj_features = self.create_subscription(
            ObjFeatures,
            '/obj_features',
            self.listener_callback,
            10)
        self.sub_obj_features
        
        self.pub_obj_type = self.create_publisher(ObjType, '/obj_type', 10)

        self.get_logger().info("Machine Learning Node gestartet...")

    def listener_callback(self, msg):
        pub_data_before = msg

        pub_data_test = ObjDataDeluxe()

        self.pub_obj_type.publish(pub_data_test)

def main():
    rclpy.init(args=None)
    ml = Machine_learning()
    rclpy.spin(ml)
    ml.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()