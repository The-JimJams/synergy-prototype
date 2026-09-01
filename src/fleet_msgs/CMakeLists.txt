cmake_minimum_required(VERSION 3.10)
project(fleet_msgs)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/RobotState.msg"
  "msg/RobotIntent.msg"
  "msg/ResourceClaim.msg"
  "msg/TaskAnnouncement.msg"
  "msg/TaskBid.msg"
  "msg/Heartbeat.msg"
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
