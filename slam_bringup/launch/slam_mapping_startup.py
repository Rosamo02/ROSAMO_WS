from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    slam_node = Node(
        package='slam_toolbox',
        executable='map_and_localization_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            {'odom_frame': 'odom'},
            {'map_frame': 'map'},
            {'base_frame': 'base_link'},
            {'scan_topic': '/scan'},
            {'mode': 'mapping'},
            {'map_update_interval': 0.1},
            {'throttle_scans': 1},
            {'transform_publish_period': 0.02},
        ]
    )

    return LaunchDescription([slam_node])
