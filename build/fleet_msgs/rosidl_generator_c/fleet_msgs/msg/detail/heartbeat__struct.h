// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from fleet_msgs:msg/Heartbeat.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fleet_msgs/msg/heartbeat.h"


#ifndef FLEET_MSGS__MSG__DETAIL__HEARTBEAT__STRUCT_H_
#define FLEET_MSGS__MSG__DETAIL__HEARTBEAT__STRUCT_H_

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
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/Heartbeat in the package fleet_msgs.
typedef struct fleet_msgs__msg__Heartbeat
{
  rosidl_runtime_c__String robot_id;
  double timestamp;
} fleet_msgs__msg__Heartbeat;

// Struct for a sequence of fleet_msgs__msg__Heartbeat.
typedef struct fleet_msgs__msg__Heartbeat__Sequence
{
  fleet_msgs__msg__Heartbeat * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} fleet_msgs__msg__Heartbeat__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // FLEET_MSGS__MSG__DETAIL__HEARTBEAT__STRUCT_H_
