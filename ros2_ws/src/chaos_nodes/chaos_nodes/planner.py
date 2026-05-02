import rclpy
from rclpy.node import Node
from chaos_topics.msg import ObjType
from chaos_topics.msg import FuturePosition
from chaos_topics.msg import ObjData
from planner.preprocessing import PostProcessor

class Planner(Node):
    def __init__(self):
        super().__init__('planner')

        self.sub_obj_type = self.create_subscription(
            ObjType,
            '/obj_type',
            self.timer_callback,
            10)
        
        self.sub_future_position = self.create_subscription(
            FuturePosition,
            '/future_position',
            self.timer_callback_callback,
            10
        ) 

        self.pub_obj_data = self.create_publisher(ObjData, '/obj_data', 10)
        timer_time = 1/30   # sek

        self.PrePro = PlanPreprocessor()

        self.data = self.create_timer(timer_time, self.timer_callback)
        self.get_logger().info('Planner-Node gestartet')

    def timer_callback(self):
        """Timer Callback - führt die Planungslogik aus"""
        # Hier wird die Logik zum Planen basierend auf den empfangenen Daten implementiert
        
        # Beispiel: Generiere einen Dummy-Objektdaten-String
        dummy_obj_data = ObjData()
        dummy_obj_data.name = "dummy_object"
        dummy_obj_data.x = 0.5
        dummy_obj_data.y = 0.5
        dummy_obj_data.z = 0.0
        
        self.pub_obj_data.publish(dummy_obj_data)

def main(args=None):
    rclpy.init(args=args)
    planner = Planner()
    rclpy.spin(planner)
    planner.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()