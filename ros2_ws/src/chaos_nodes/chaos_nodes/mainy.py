import rclpy
from rclpy.node import Node
from chaos_interfaces.msg import ObjDataDeluxe
from std_msgs.msg import Bool
from std_msgs.msg import Int16
from geometry_msgs.msg import Point32
from ros2_logic.mainy import mainy_logic


#================================================================================================================

class Mainy(Node):
    def __init__(self):

        super().__init__('Mainy')

        self.sub_obj_data_deluxe = self.create_subscription(
            ObjDataDeluxe,
            '/obj_data_deluxe',
            self.set_obj_data_delux,
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
        self.pub_obj_finished = self.create_publisher(Int16, '/obj_finished', 10)

        #========================================================================================================
        
        self.timer_StateMachine = self.create_timer(0.1, self.timer_StateMachine)

        #========================================================================================================

        self.mainylogic = MainyLogic()

        #========================================================================================================

        self.get_logger().info("Mainy Node gestartet...")

#================================================================================================================
    def timer_StateMachine(self):

        #TODO abfrage zum verhindern, dass ohne statewechsel mehr als einmal zielcoordinaten gepublished werden
        x,y,z,gripper = self.mainylogic.state_machine() 
        work_done, obj_id = self.mainylogic.work_done()

        if work_done:
            done_obj_id = Int16()
            done_obj_id.data = obj_id
            self.pub_obj_finished(done_obj_id)

        goal_coordinates = Point32()
        goal_coordinates.x = x
        goal_coordinates.y = y
        goal_coordinates.z = z
        self.pub_goal_coordinates(goal_coordinates)

        goal_gripper = Bool()
        goal_gripper.data = gripper
        self.pub_goal_gripper(goal_gripper)




#================================================================================================================

    def goal_reached(self, msg):
        goal_reached = msg.data
        self.mainylogic.goal_reached(goal_reached)

#================================================================================================================

    def init_done(self, msg):
        init_done = msg.data
        self.mainylogic.init_abfrage(init_done)

#================================================================================================================

    def set_obj_data_delux(self, msg):
        obj_id = msg.obj_id
        obj_typ = msg.obj_typ
        goal_coord_x = msg.coord_x
        goal_coord_y = msg.coord_y
        goal_theta = msg.theta
        self.mainylogic.auftragseingang_main(
            obj_id, 
            obj_typ, 
            goal_coord_x, 
            goal_coord_y,
            goal_theta)



#================================================================================================================



def main():
    rclpy.init(args=None)
    main = Mainy()
    rclpy.spin(main)
    main.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()