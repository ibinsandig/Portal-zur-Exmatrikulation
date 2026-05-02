import rclpy
from rclpy.node import Node
from chaos_interfaces.msg import ObjData 
from planner.preprocessing import PlanPreprocessor

class Planner(Node):
    def __init__(self):
        super().__init__('planner')

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