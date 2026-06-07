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
        
        classifier = Classifier()

        self.pub_obj_type = self.create_publisher(ObjType, '/obj_type', 10)

        self.get_logger().info("Machine Learning Node gestartet...")

    def listener_callback(self, msg):
        pub_data_before = msg

        label, confidence = classifier.classify(
            circularity=msg.circularity,
            hu_4=msg.hu_4,
            fd_2=msg.fd_2,
            fd_6=msg.fd_6,
            hu_1=msg.hu_1,
            hu_0=msg.hu_0,
            hu_5=msg.hu_5,
            hu_6=msg.hu_6,
            solidity=msg.solidity,
            area=msg.area
        )

        # Daten in msg schreiben und publishen
        pub_data_test = ObjType()

        pub_data_test.id = msg.id
        pub_data_test.obj_typ = label


        self.pub_obj_type.publish(pub_data_test)

def main():
    rclpy.init(args=None)
    ml = Machine_learning()
    rclpy.spin(ml)
    ml.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()