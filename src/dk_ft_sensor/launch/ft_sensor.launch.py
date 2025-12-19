from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    # Declare launch arguments
    host_arg = DeclareLaunchArgument(
        'host',
        default_value='0.0.0.0',
        description='UDP host address to bind to'
    )
    
    port_arg = DeclareLaunchArgument(
        'port',
        default_value='5566',
        description='UDP port number to listen on'
    )
    
    topic_name_arg = DeclareLaunchArgument(
        'topic_name',
        default_value='ft_sensor_raw',
        description='Topic name for publishing force/torque data'
    )
    
    # Create node with parameters
    ft_sensor_node = Node(
        package='dk_ft_sensor',
        executable='ft_sensor_node',
        name='ft_sensor_node',
        output='screen',
        parameters=[{
            'host': LaunchConfiguration('host'),
            'port': LaunchConfiguration('port'),
            'topic_name': LaunchConfiguration('topic_name'),
        }],
    )
    
    return LaunchDescription([
        host_arg,
        port_arg,
        topic_name_arg,
        ft_sensor_node,
    ])
