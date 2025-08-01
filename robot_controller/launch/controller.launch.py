import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, GroupAction, OpaqueFunction, IncludeLaunchDescription
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import LaunchConfiguration
from launch.substitutions import Command



def generate_launch_description():
    robot_description_package = 'robot_description'   # Change to your actual package name
    controller_package = 'robot_controller'           # Change if different

    # URDF (Xacro) path
    xacro_file = os.path.join(
        get_package_share_directory(robot_description_package),
        'urdf',
        'robot.urdf.xacro'
    )

    # Controller YAML config
    controller_yaml = os.path.join(
        get_package_share_directory(controller_package),
        'config',
        'controller.yaml'
    )

    # Convert xacro to robot description at launch time
    robot_description = Command(['xacro ', xacro_file])
    robot_description_param = {'robot_description': robot_description}

    # Declare launch argument (optional)
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation time if true'
    )

    ros2_control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_description_param, controller_yaml, {'use_sim_time': LaunchConfiguration('use_sim_time')}],
        output="screen"
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager",
        ],
        parameters=[{'use_sim_time': True}]
    )


    wheel_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["robot_controller", 
                   "--controller-manager", 
                   "/controller_manager"
        ],
        parameters=[{'use_sim_time': True}]
    )


    return LaunchDescription(
        [
            declare_use_sim_time,
            ros2_control_node,
            joint_state_broadcaster_spawner,
            wheel_controller_spawner,
        ]
    )