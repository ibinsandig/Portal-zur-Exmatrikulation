"""
Launch the nodes to communicate with the pickrobot used in the RO45 project.
This will launch
- a position_publisher node that publishes the position of the 3 axes of the pickrobot
- a command_subscriber node that subscribes to pickrobot commands that are sent to robot
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    config = os.path.join(
            get_package_share_directory('ro45_ros2_pickrobot_serial'),
            'config', 'ro45_params.yaml')

    nodes = [
            Node(
                package='ro45_ros2_pickrobot_serial',
                executable='ros2_to_serial_bridge_node',
                #namespace='ro45',
                name='position_publisher',
                parameters=[config]
                ),
            Node(
                package='ro45_ros2_pickrobot_serial',
                executable='ros2_to_serial_bridge_node',
                #namespace='ro45',
                name='command_subscriber',
                parameters=[config]
                )
            ]

    return LaunchDescription(nodes)

