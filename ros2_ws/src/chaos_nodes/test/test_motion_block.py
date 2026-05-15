import rclpy
import pytest
import time
from rclpy.node import Node
from std_msgs.msg import Bool
from geometry_msgs.msg import Point32





def test_motion_block():

    rclpy.init()
    node = rclpy.create_node('test_motion_point')

    goal_reached = False

    def goal(msg):
        global goal_reached         
        goal_reached = msg.data

    goal_sub = node.create_subscription(Bool, '/GoalState', goal, 10)

    time.sleep(0.5)

    goal_pub = node.create_publisher(Point32, '/goal_data', 10)

    msg = Point32()
    msg.x = 0.10
    msg.y = -0.10
    msg.z = 0.040
    goal_pub.publish(msg)


    for _ in range(80):             # 80 mal 0.1s = 8sek
        rclpy.spin_once(node, timeout_sec=0.1)
        if goal_reached == True:
            break


    assert goal_reached, "Ziel wurde nicht erreicht innerhalb 8 Sekunden"

    node.destroy_node()
    rclpy.shutdown()




