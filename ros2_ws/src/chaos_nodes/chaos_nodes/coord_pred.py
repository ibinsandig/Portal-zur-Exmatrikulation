import rclpy
from rclpy.node import Node
from chaos_topics.msg import FuturePosition
from chaos_topics.msg import ObjCoords
from coord_pred.coord_pred import CoordinatesPrediction

class CoordPred(Node):
    def __init__(self):
        super().__init__('coord_pred')

        self.sub_obj_coords = self.create_subscription(
            ObjCoords,
            '/obj_coords',
            self.listener_callback,
            10)
        self.sub_obj_features

        self.pub_future_postion = self.create_publisher(FuturePosition, '/future_position', 10)
        timer_time = 1/30   # sek

        self.PrePro = CoordinatesPrediction()

        self.data = self.create_timer(timer_time, self.timer_callback)
        self.get_logger().info('CoordPred-Node gestartet')

    def timer_callback(self):
        """Timer Callback - führt die Koordinatenprädiktionslogik aus"""
        # Hier wird die Logik zum Prädizieren der Koordinaten basierend auf den empfangenen Daten implementiert
        
        # Beispiel: Generiere einen Dummy-Objektdaten-String
        dummy_obj_data = ObjData()
        dummy_obj_data.name = "dummy_object"
        dummy_obj_data.x = 0.5
        dummy_obj_data.y = 0.5
        dummy_obj_data.z = 0.0
        
        self.pub_obj_data.publish(dummy_obj_data)

def main(args=None):
    rclpy.init(args=args)
    coord_pred = CoordPred()
    rclpy.spin(coord_pred)
    coord_pred.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()