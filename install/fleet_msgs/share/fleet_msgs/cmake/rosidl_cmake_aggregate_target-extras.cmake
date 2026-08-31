# generated from rosidl_cmake/cmake/rosidl_cmake_aggregate_target-extras.cmake.in

# Create a convenience aggregate target fleet_msgs::fleet_msgs
# that links all generated interface targets, so downstream packages can use
# a single modern CMake target name instead of ${fleet_msgs_TARGETS}.
if(fleet_msgs_TARGETS AND NOT TARGET fleet_msgs::fleet_msgs)
  add_library(fleet_msgs::fleet_msgs INTERFACE IMPORTED)
  set_target_properties(fleet_msgs::fleet_msgs PROPERTIES
    INTERFACE_LINK_LIBRARIES "${fleet_msgs_TARGETS}")
endif()
