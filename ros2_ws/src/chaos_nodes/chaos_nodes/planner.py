import rclpy
from rclpy.node import Node
from chaos_topics.msg import ObjType, FuturePosition, ObjData
from std_msgs.msg import Int16
from geometry_msgs.msg import Point
from planner.postprocessing import PostProcessor
from functools import partial

class Planner(Node):
    
    def __init__(self):
        super().__init__('planner')

        self.sub_obj_type = self.create_subscription(
            ObjType, '/obj_type', self.callback_obj_type, 10)

        self.sub_future_position = self.create_subscription(
            FuturePosition, '/future_position', self.callback_future_position, 10)

        self.sub_obj_finished = self.create_subscription(
            Int16, '/obj_finished', self.callback_obj_finished, 10)

        self.pub_obj_data = self.create_publisher(ObjData, '/obj_data', 10)

        self.timer_time = 0.1
        self.timer = self.create_timer(self.timer_time, self.timer_callback)

        self.PostPro = PostProcessor()
        self.get_logger().info('Planner-Node gestartet')

    def callback_obj_type(self, msg):
        self.get_logger().info("Objekttyp empfangen")
        self.PostPro.add_obj_type(msg.id, msg.obj_type)

    def callback_future_position(self, msg):
        self.get_logger().info("Futureposition empfangen")
        self.PostPro.add_future_position(msg.id, msg.pose2d, msg.speed, msg.timestamp)

    def callback_obj_finished(self, msg):
        finished_id = msg.data

        self.PostPro.finish_obj(finished_id)
        self.get_logger().info(f'Objekt {finished_id} abgeschlossen und entfernt')

    def timer_callback(self):
        obj = self.PostPro.get_next()
        if obj is None:
            return

        if obj['obj_type'] == 0:
            self.PostPro.finish_obj(obj['id'])
            self.get_logger().info(f"Objekt {obj['id']} ist rejected, wird gelöscht")
            return

        pub_data = ObjData()
        pub_data.id      = obj['id']
        pub_data.obj_typ = obj['obj_type']
        
        p = Point()
        p.x = float(obj['grip_point']['x'])
        p.y = float(obj['grip_point']['y'])
        p.z = 0.0
        pub_data.point = p
        pub_data.obj_speed = float(obj['speed']) 
        
        self.pub_obj_data.publish(pub_data)
        self.get_logger().info(
            f"Published: ID={pub_data.id}, Typ={pub_data.obj_typ}, "
            f"x={pub_data.point.x:.2f}, y={pub_data.point.y:.2f}"
        )

def main(args=None):
    rclpy.init(args=args)
    planner = Planner()
    rclpy.spin(planner)
    planner.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()