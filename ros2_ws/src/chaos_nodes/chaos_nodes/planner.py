import rclpy
from rclpy.node import Node
from chaos_topics.msg import ObjType
from chaos_topics.msg import FuturePosition
from chaos_topics.msg import ObjData
from planner.postprocessing import PostProcessor
from functools import partial


class Planner(Node):
    def __init__(self):
        super().__init__('planner')

        self.sub_obj_type = self.create_subscription(
            ObjType, '/objType', partial(self.listener_callback, topic_name='0'), 10)

        
        self.sub_future_position = self.create_subscription(
            FuturePosition, '/future_position', partial(self.listener_callback, topic_name='1'), 10)

        self.pub_obj_data = self.create_publisher(ObjData, '/obj_data', 10)

        self.PrePro = PostProcessor()

        self.get_logger().info('Planner-Node gestartet')

    def listener_callback(self, topic_name):

        #TODO Hier sollen Daten aus den beiden nodes ankommen. 1. Die erhaltenen DAten muss zueinander zu geordnet werden anhand der IDs. Sowie die Berechnung des Offfsets zum greifen des objekt (id, theta) 2. wenn die das erste passiert ist werden die DAten in eine wartschlange gestellt wo das älteste Objekt als erstes an oberster Stell esteht. Neue Objekte werden hinten angestellt. 3. mit jedem durchlauf wird geschaut ob mit dem ersten objekt in der warteschlange eine geschwindigkeit berechnet werden aknn. wenn dies der fall ist wird dies gemacht und die DAten davon gepublished 4. die DAten werden solange gepublished, solange bis vom topic obj_finished die jeweilige ID zurückgegeben wird, dann wird das Objekt von der Lsite gelöscht.


        pub_data = None
        self.pub_obj_data.publish()

def main(args=None):
    rclpy.init(args=args)
    planner = Planner()
    rclpy.spin(planner)
    planner.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()