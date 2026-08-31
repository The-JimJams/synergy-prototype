# Fleet Coordination — ROS 2 Interface Layer
#
# This is the ONLY package that imports rclpy and ROS 2 dependencies.
# It adapts between ROS 2 messages and the internal dataclass models
# used by the algorithm layer.
#
# Contains no algorithm logic — only message conversion and pub/sub plumbing.
