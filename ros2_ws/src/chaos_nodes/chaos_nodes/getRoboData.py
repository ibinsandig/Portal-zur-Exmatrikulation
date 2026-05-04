import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point32
from std_msgs.msg import Bool

from ro45_portalrobot_interfaces.msg import RobotCmd
from ro45_portalrobot_interfaces.msg import RobotPos

#================================================================================================================
#   Diese Datei ist aussschließlich um zu Testen, ob Daten vom Robi ankommen. 
#   Startbefehel Terminal nach sourcen: 'ros2 run chaos_nodes getRoboData'
#================================================================================================================

class RoboData(Node):
    def __init__(self):
        super().__init__('RoboData')

        self.get_logger().info("RoboData Node gestartet...")

        #=======================================

        self.robo_data = self.create_subscription(
            RobotPos,
            '/robot_position',
            self.roboDataXYZ,
            10)
        


    def roboDataXYZ(self, msg):
        x = msg.pos_x
        y = msg.pos_y
        z = msg.pos_z
        self.get_logger().info(str(msg))
        self.get_logger().info(f("Info über die Koordinaten:{msg}"))

#====================================================================================


def main():
    rclpy.init(args=None)
    roboData = RoboData()
    rclpy.spin(roboData)
    roboData.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()