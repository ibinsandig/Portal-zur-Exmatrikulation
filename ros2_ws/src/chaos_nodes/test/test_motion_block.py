import rclpy
from rclpy.node import Node
from chaos_interfaces.msg import GoalData
from chaos_interfaces.msg import GoalState

#Testversion OHNE Klasse 
# Aufruf im terminal: "python3 test_motion_block.py" (vorher sourcen dikka)

rclpy.init()
node = rclpy.create_node('test_motion_block')

publisher = node.create_publisher(
    GoalData,
    '/goal_data',
    10
)

x = float(input("X: "))
y = float(input("Y: "))
z = float(input("Z: "))
gripper = bool(input("Gripper (True/Flase): "))

msg = GoalData()
msg.x = x
msg.y = y
msg.z = z
msg.grip = gripper

publisher.publish(msg)

rclpy.spin(node)
node.destroy_node()
rclpy.shutdown()

