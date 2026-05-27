import rclpy
from rclpy.node import Node
from chaos_interfaces.msg import ObjDataDeluxe
from std_msgs.msg import Bool
from geometry_msgs.msg import Point32


#================================================================================================================

class Mainy(Node):
    def __init__(self):

        super().__init__('Mainy')

        self.sub_obj_data_deluxe = self.create_subscription(
            ObjDataDeluxe,
            '/obj_data_deluxe',
            self.listener_callback,
            10)
        
        self.sub_goal_reached = self.create_subscription(
            Bool,
            '/goal_reached',
            self.goal_reached,
            10)
        
        self.sub_init_done = self.create_subscription(
            Bool,
            '/init_done',
            10)
        
        #========================================================================================================

        self.pub_goal_coodrinates = self.create_publisher(Point32, '/goal_coordinates', 10)
        self.pub_goal_gripper = self.create_publisher(Bool, '/goal_gripper', 10)

        #========================================================================================================
        
        self.goal_reached = None


        #========================================================================================================

        self.get_logger().info("Mainy Node gestartet...")

#================================================================================================================

    def goal_reached(self, msg):
        self.goal_reached = msg.data
      

#================================================================================================================

def main():
    rclpy.init(args=None)
    main = Mainy()
    rclpy.spin(main)
    main.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()