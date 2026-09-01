// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from fleet_msgs:msg/RobotState.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fleet_msgs/msg/robot_state.h"


#ifndef FLEET_MSGS__MSG__DETAIL__ROBOT_STATE__STRUCT_H_
#define FLEET_MSGS__MSG__DETAIL__ROBOT_STATE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

// Include directives for member types
// Member 'robot_id'
// Member 'current_task'
// Member 'status'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/RobotState in the package fleet_msgs.
typedef struct fleet_msgs__msg__RobotState
{
  rosidl_runtime_c__String robot_id;
  double timestamp;
  double position[2];
  double velocity;
  double battery;
  rosidl_runtime_c__String current_task;
  rosidl_runtime_c__String status;
} fleet_msgs__msg__RobotState;

// Struct for a sequence of fleet_msgs__msg__RobotState.
typedef struct fleet_msgs__msg__RobotState__Sequence
{
  fleet_msgs__msg__RobotState * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} fleet_msgs__msg__RobotState__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // FLEET_MSGS__MSG__DETAIL__ROBOT_STATE__STRUCT_H_
