#!/usr/bin/env python3
"""
Cartesian Controller Launch File for DUCO GCR5-910 Robot

This launch file starts the DUCO robot with Cartesian controllers for
motion, force, and compliance control. It integrates:
- DUCO hardware interface (via ros2_control)
- Cartesian controllers (motion, force, compliance)
- Robot state publisher
- Static TF transforms

Usage:
    ros2 launch duco_gcr5_910_moveit_config cartesian_controller.launch.py robot_ip:=192.168.1.10

Arguments:
    robot_ip: IP address of the robot controller (default: 192.168.1.10)
    robot_port: Port number for robot communication (default: 7003)
    use_rviz: Launch RViz for visualization (default: true)
    db: Start warehouse database (default: false)
    debug: Enable debug mode (default: false)
"""

import os
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution
from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launch_utils import DeclareBooleanLaunchArg


def generate_demo_launch(moveit_config, launch_package_path=None, declared_arguments=None):
    """
    Launches a self-contained demo with Cartesian controllers

    Includes:
     * static_virtual_joint_tfs
     * robot_state_publisher
     * ros2_control_node with DUCO hardware interface + Cartesian controllers
     * controller spawners
    """
    if launch_package_path is None:
        launch_package_path = moveit_config.package_path
    
    ld = LaunchDescription()
    
    # Add declared arguments if provided
    if declared_arguments:
        for arg in declared_arguments:
            ld.add_action(arg)
    
    ld.add_action(
        DeclareBooleanLaunchArg(
            "db",
            default_value=False,
            description="By default, we do not start a database (it can be large)",
        )
    )
    ld.add_action(
        DeclareBooleanLaunchArg(
            "debug",
            default_value=False,
            description="By default, we are not in debug mode",
        )
    )
    ld.add_action(
        DeclareBooleanLaunchArg(
            "use_rviz", 
            default_value=True,
            description="Start RViz for visualization"
        )
    )
    
    # If there are virtual joints, broadcast static tf by including virtual_joints launch
    virtual_joints_launch = (
        launch_package_path / "launch/static_virtual_joint_tfs.launch.py"
    )

    if virtual_joints_launch.exists():
        ld.add_action(
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(str(virtual_joints_launch)),
            )
        )

    # Given the published joint states, publish tf for the robot links
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                str(launch_package_path / "launch/rsp.launch.py")
            ),
        )
    )

    # Build robot description with network parameters for DUCO hardware interface
    robot_description_content = Command([
        "xacro ", str(moveit_config.package_path / "config/gcr5_910.urdf.xacro"),
        " robot_ip:=", LaunchConfiguration("robot_ip"),
        " robot_port:=", LaunchConfiguration("robot_port")
    ])
    
    robot_description_param = {
        "robot_description": ParameterValue(robot_description_content, value_type=str)
    }
    
    # Cartesian controller configuration
    robot_pkg = FindPackageShare("duco_gcr5_910_moveit_config")
    ros2_controllers = PathJoinSubstitution([
        robot_pkg, 
        "config", 
        "cartesian_controller_manager.yaml"
    ])
    
    # ROS2 Control Node with DUCO hardware interface and Cartesian controllers
    # Topic remappings ensure controllers can communicate with each other and external nodes
    ros2_control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_description_param, ros2_controllers],
        output="both",
        remappings=[
            ("motion_control_handle/target_frame", "target_frame"),
            ("cartesian_motion_controller/target_frame", "target_frame"),
            ("cartesian_compliance_controller/target_frame", "target_frame"),
            ("cartesian_force_controller/target_wrench", "target_wrench"),
            ("cartesian_compliance_controller/target_wrench", "target_wrench"),
            ("cartesian_force_controller/ft_sensor_wrench", "ft_sensor_wrench"),
            ("cartesian_compliance_controller/ft_sensor_wrench", "ft_sensor_wrench"),
        ],
    )
    ld.add_action(ros2_control_node)

    # Joint state broadcaster - publishes joint states to /joint_states
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )
    ld.add_action(joint_state_broadcaster_spawner)
    
    # Cartesian controller spawner helper function
    def controller_spawner(name, *extra_args):
        return Node(
            package="controller_manager",
            executable="spawner",
            arguments=[name, "--controller-manager", "/controller_manager", *extra_args],
            output="screen",
        )

    # Active controllers at startup
    # By default, start with compliance controller for safe operation
    active_list = ["cartesian_motion_controller"]
    active_spawners = [controller_spawner(c) for c in active_list]
    
    # Inactive controllers - can be switched to later using controller_manager services
    inactive_list = [
        "cartesian_compliance_controller",
        "cartesian_force_controller",
        # "motion_control_handle",  # Uncomment if using interactive markers in RViz
    ]
    inactive_spawners = [controller_spawner(c, "--inactive") for c in inactive_list]
    
    for spawner in active_spawners + inactive_spawners:
        ld.add_action(spawner)

    return ld


def generate_launch_description():
    """
    Generate launch description for DUCO robot with Cartesian controllers
    """
    # Declare launch arguments for network configuration
    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            "robot_ip",
            default_value="192.168.1.10",
            description="IP address of the DUCO robot controller",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "robot_port", 
            default_value="7003",
            description="Port number for robot communication",
        )
    )
    
    # Build MoveIt configuration
    moveit_config = MoveItConfigsBuilder(
        "gcr5_910", 
        package_name="duco_gcr5_910_moveit_config"
    ).to_moveit_configs()
    
    # Generate launch description
    launch_description = generate_demo_launch(
        moveit_config, 
        declared_arguments=declared_arguments
    )
    
    return launch_description
