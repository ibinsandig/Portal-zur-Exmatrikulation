import rclpy
from rclpy.node import Node
from chaos_topics.msg import FuturePosition
from chaos_topics.msg import ObjCoords
from coord_pred.coord_pred import CoordinatesPrediction

class CoordPred(Node):
    """ROS2-Node: Empfängt Objektkoordinaten auf '/obj_coords', berechnet die Objektgeschwindigkeit und publiziert Zukunftspositionen auf '/future_position'."""

    def __init__(self):
        """Initialisiert Subscriber für '/obj_coords', Publisher für '/future_position' und CoordinatesPrediction."""
        super().__init__('coord_pred')

        self.sub_obj_coords = self.create_subscription(
            ObjCoords,
            '/obj_coords',
            self.listener_callback,
            10)

        self.pub_future_position = self.create_publisher(FuturePosition, '/future_position', 10)

        self.PrePro = CoordinatesPrediction()

        self.get_logger().info('CoordPred-Node gestartet')

    def listener_callback(self, msg):
        """ROS2-Callback: Verarbeitet ObjCoords-Nachricht, berechnet Geschwindigkeit und publiziert FuturePosition.

        Args:
            msg (chaos_topics/ObjCoords): Eingehende Objektkoordinaten mit ID, Pose2D und Zeitstempel
        """
        result = self.PrePro.add_measurement(
            id = msg.id,
            x = msg.pose2d.x,
            t = msg.timestamp,
        )

        if result is None:
            self.get_logger().info("Keine Geschwindigkeit berechnet")
            return

        future_position = FuturePosition()
        future_position.id = result['id']
        future_position.pose2d = msg.pose2d
        future_position.timestamp = msg.timestamp
        future_position.speed = float(result['speed'])

        self.get_logger().info(
            f"Speed: {future_position.speed:.8f}; ID: {future_position.id}; "
            f"X: {future_position.pose2d.x:.8f}; Y: {future_position.pose2d.y:.8f}"
        )

        self.pub_future_position.publish(future_position)
        self.get_logger().info(f"RAW obj_coords: id={msg.id}, x={msg.pose2d.x:.6f}, t={msg.timestamp:.6f}")
        self.get_logger().info('Future_position gepublished')

def main(args=None):
    rclpy.init(args=args)
    coord_pred = CoordPred()
    rclpy.spin(coord_pred)
    coord_pred.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()