// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from fleet_msgs:msg/RobotIntent.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fleet_msgs/msg/robot_intent.h"


#ifndef FLEET_MSGS__MSG__DETAIL__ROBOT_INTENT__STRUCT_H_
#define FLEET_MSGS__MSG__DETAIL__ROBOT_INTENT__STRUCT_H_

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
// Member 'planned_path'
// Member 'target_intersection'
// Member 'task_id'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/RobotIntent in the package fleet_msgs.
typedef struct fleet_msgs__msg__RobotIntent
{
  rosidl_runtime_c__String robot_id;
  rosidl_runtime_c__String__Sequence planned_path;
  rosidl_runtime_c__String target_intersection;
  double eta;
  int32_t priority;
  rosidl_runtime_c__String task_id;
} fleet_msgs__msg__RobotIntent;

// Struct for a sequence of fleet_msgs__msg__RobotIntent.
typedef struct fleet_msgs__msg__RobotIntent__Sequence
{
  fleet_msgs__msg__RobotIntent * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} fleet_msgs__msg__RobotIntent__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // FLEET_MSGS__MSG__DETAIL__ROBOT_INTENT__STRUCT_H_
