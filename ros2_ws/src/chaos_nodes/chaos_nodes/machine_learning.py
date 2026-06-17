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

        smoothed_label, confidence = self.classifier.classify(
            id=msg.id,
            hu_2=msg.hu_2,
            hu_3=msg.hu_3,
        )

        self.get_logger().info(
            f"ID: {msg.id} | Label: {smoothed_label} | Confidence: {confidence:.4f}"
        )

        pub_data = ObjType()
        pub_data.id       = msg.id
        pub_data.obj_type = smoothed_label

        self.pub_obj_type.publish(pub_data)


def main():
    rclpy.init(args=None)
    ml = Machine_learning()
    rclpy.spin(ml)
    ml.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()