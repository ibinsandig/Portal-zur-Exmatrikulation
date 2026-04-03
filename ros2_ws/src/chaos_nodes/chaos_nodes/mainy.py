import rclpy
from rclpy.node import Node
from chaos_interfaces.msg import GoalData, ObjDataDeluxe,  GoalState

class Mainy(Node):
    def __init__(self):

        super().__init__('Mainy')

        self.sub_obj_data_deluxe = self.create_subscription(
            ObjDataDeluxe,
            '/obj_data_deluxe',
            self.listener_callback,
            10)
        
        self.sub_goal_state = self.create_subscription(
            GoalState,
            '/goal_state',
            self.listener_callback,
            10)
        
        self.sub_obj_data_deluxe
        self.sub_goal_state

        self.pub_goal_data = self.create_publisher(GoalData, '/goal_data', 10)

        self.get_logger().info("Mainy Node gestartet...")

    def listener_callback(self, msg):
        self.pub_data_before = msg

        self.pub_data_test = GoalData()

        self.pub_goal_data.publish(self.pub_data_test)

def main():
    rclpy.init(args=None)
    main = Mainy()
    rclpy.spin(main)
    main.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()