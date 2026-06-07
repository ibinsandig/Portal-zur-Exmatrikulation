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

        self.classifier = Classifier()

        self.get_logger().info("Machine Learning Node gestartet...")

    def listener_callback(self, msg):
        pub_data_before = msg

        label, confidence = self.classifier.classify(
            corners=msg.cornercount,
            fd_4=msg.fd_4,
            perimeter=msg.perimeter,
            circularity=msg.circularity,
            hu_4=msg.hu_4,
            fd_2=msg.fd_2,
            bbox_w=msg.bbox_w,
            fd_1=msg.fd_1,
            fd_3=msg.fd_3,
            fd_5=msg.fd_5,
            fd_7=msg.fd_7,
            fd_6=msg.fd_6,
            hu_1=msg.hu_1,
            hu_0=msg.hu_0,
            hu_2=msg.hu_2,
            hu_3=msg.hu_3,
            hu_5=msg.hu_5,
            hu_6=msg.hu_6,
            solidity=msg.solidity,
            area=msg.area
        )
        self.get_logger().info(f"Label: {label}, Confidence: {confidence}")
        # Daten in msg schreiben und publishen
        pub_data_test = ObjType()

        pub_data_test.id = msg.id
        pub_data_test.obj_type = int(label)


        self.pub_obj_type.publish(pub_data_test)

def main():
    rclpy.init(args=None)
    ml = Machine_learning()
    rclpy.spin(ml)
    ml.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()