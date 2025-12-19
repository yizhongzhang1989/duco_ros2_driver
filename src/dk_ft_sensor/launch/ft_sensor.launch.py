from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='dk_ft_sensor',
            executable='ft_sensor_node',
            name='ft_sensor_node',
            output='screen',
            parameters=[],
        )
    ])
