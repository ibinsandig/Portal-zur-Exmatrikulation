import rclpy
from rclpy.node import Node
from chaos_topics.msg import ObjData
from std_msgs.msg import Bool
from std_msgs.msg import Int16
from geometry_msgs.msg import Point32
from mainy.mainy_logic import MainyLogic


#================================================================================================================

class Mainy(Node):
    def __init__(self):

        super().__init__('Mainy')

        self.sub_obj_data = self.create_subscription(
            ObjData,
            '/obj_data',
            self.set_obj_data,
            10)
        
        self.sub_goal_reached = self.create_subscription(
            Bool,
            '/goal_reached',
            self.goal_reached_request,
            10)
        
        self.sub_init_done = self.create_subscription(
            Bool,
            '/init_done',
            self.init_done_request,
            10)
        
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

        x,y,z,gripper,pub_block = self.mainylogic.state_machine() 
        print(f"{x},{y},{z},{gripper},{pub_block}")

        work_done, obj_id = self.mainylogic.work_done_flag()
        print(f"Auftragsabschluss:{work_done},id:{obj_id}")

        if work_done:
            done_obj_id = Int16()
            done_obj_id.data = obj_id
            self.pub_obj_finished.publish(done_obj_id)

        if pub_block:
            goal_coordinates = Point32()
            goal_coordinates.x = x
            goal_coordinates.y = y
            goal_coordinates.z = z
            self.pub_goal_coordinates.publish(goal_coordinates)
            
            print("pub_block if erfüllt")
            goal_gripper = Bool()
            goal_gripper.data = gripper
            self.pub_goal_gripper.publish(goal_gripper)




#================================================================================================================

    def goal_reached_request(self, msg):
        goal_reached = msg.data
        self.mainylogic.goal_reached_flag(goal_reached)

#================================================================================================================

    def init_done_request(self, msg):
        init_done = msg.data
        self.mainylogic.init_abfrage(init_done)

#================================================================================================================

    def set_obj_data(self, msg):
        obj_id = msg.id
        obj_typ = msg.obj_typ
        goal_coord_x = msg.coord_x
        goal_coord_y = msg.coord_y
        goal_theta = msg.theta
        self.mainylogic.auftragseingang_main(obj_id)
        self.mainylogic.obj_current_pos( 
            obj_typ, 
            goal_coord_x, 
            goal_coord_y,
            goal_theta)
        self.mainylogic.extrapolation()       #TODO Sinnhaftigkeit Prüfen! Sonst in timer_StateMaschine



#================================================================================================================



def main():
    rclpy.init(args=None)
    main = Mainy()
    rclpy.spin(main)
    main.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()