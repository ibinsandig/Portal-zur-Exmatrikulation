import rclpy
from rclpy.node import Node
from chaos_interfaces.msg import ObjDataDeluxe
from std_msgs.msg import Bool
from geometry_msgs.msg import Point32
from ros2_logic.mainy import mainy_logic


#================================================================================================================

class Mainy(Node):
    def __init__(self):

        super().__init__('Mainy')

        self.sub_obj_data_deluxe = self.create_subscription(
            ObjDataDeluxe,
            '/obj_data_deluxe',
            self.obj_data_delux,
            10)
        
        self.sub_goal_reached = self.create_subscription(
            Bool,
            '/goal_reached',
            self.goal_reached,
            10)
        
        self.sub_init_done = self.create_subscription(
            Bool,
            '/init_done',
            self.init_done,
            10)
        
        #   TIMER CALLBAXK als haupttaktgeber in MAINY
        
        #========================================================================================================

        self.pub_goal_coordinates = self.create_publisher(Point32, '/goal_coordinates', 10)
        self.pub_goal_gripper = self.create_publisher(Bool, '/goal_gripper', 10)

        #========================================================================================================
        
        self.timer_StateMachine = self.create_timer(0.1, self.timer_StateMachine)

        #========================================================================================================
        self.goal_reached = False
        self.init_done = False

        self.v_obj = None
        self.typ_obj = None
        self.id_obj = None
        self.t_obj = None
        self.goal_coord_x = None
        self.goal_coord_y = None
        self.goal_coord_z = None


        self.mainylogic = MainyLogic()

        #========================================================================================================

        self.get_logger().info("Mainy Node gestartet...")

#================================================================================================================

    def goal_reached(self, msg):
        self.goal_reached = msg.data

#================================================================================================================

    def init_done(self, msg):
        self.init_done = msg.data

#================================================================================================================

    def obj_data_delux(self, msg):
        self.v_obj = msg.v_obj      #TODO: Hier muss der Richtige CUSTOM-MSG Typ hin!!
        self.typ_obj = msg.obj_typ
        self.id_obj = msg.id_obj
        self.t_obj = msg.t_obj
        self.goal_coord_x = msg.coord_x
        self.goal_coord_y = msg.coord_y
        self.goal_coord_z = msg.coord_z
        
        self.mainylogic.auftragseingang(self.id_obj, )
#================================================================================================================



def main():
    rclpy.init(args=None)
    main = Mainy()
    rclpy.spin(main)
    main.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()