import rclpy
from rclpy.node import Node
from chaos_topics.msg import FuturePosition
from chaos_topics.msg import ObjCoords
from geometry_msgs.msg import Pose2D
from coord_pred.coord_pred import CoordinatesPrediction

class CoordPred(Node):
    def __init__(self):
        super().__init__('coord_pred')

        self.sub_obj_coords = self.create_subscription(
            ObjCoords,
            '/obj_coords',
            self.listener_callback,
            10)
        self.sub_obj_coords

        self.pub_future_postion = self.create_publisher(FuturePosition, '/future_position', 10)

        self.PrePro = CoordinatesPrediction()

        self.get_logger().info('CoordPred-Node gestartet')

    def listener_callback(self, msg):
        future_position = FuturePosition()
        future_position.id = msg.id
        future_position.pose2d = msg.pose2d
        future_position.timestamp = msg.timestamp  

        speed = self.PrePro.calculate_speed_with_ID(
            msg.id, msg.pose2d.x, msg.timestamp
        )

        if speed != -100:
            future_position.speed = float(speed)

        self.get_logger().info(
            f"Speed: {future_position.speed}; ID: {future_position.id}; "
            f"X: {future_position.pose2d.x}; Y: {future_position.pose2d.y};"
        )

        self.pub_future_postion.publish(future_position)

def main(args=None):
    rclpy.init(args=args)
    coord_pred = CoordPred()
    rclpy.spin(coord_pred)
    coord_pred.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()