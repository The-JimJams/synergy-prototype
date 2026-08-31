// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from fleet_msgs:msg/TaskBid.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fleet_msgs/msg/task_bid.h"


#ifndef FLEET_MSGS__MSG__DETAIL__TASK_BID__STRUCT_H_
#define FLEET_MSGS__MSG__DETAIL__TASK_BID__STRUCT_H_

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
// Member 'task_id'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/TaskBid in the package fleet_msgs.
typedef struct fleet_msgs__msg__TaskBid
{
  rosidl_runtime_c__String robot_id;
  rosidl_runtime_c__String task_id;
  double estimated_time;
  double distance;
  double battery_cost;
  double confidence;
} fleet_msgs__msg__TaskBid;

// Struct for a sequence of fleet_msgs__msg__TaskBid.
typedef struct fleet_msgs__msg__TaskBid__Sequence
{
  fleet_msgs__msg__TaskBid * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} fleet_msgs__msg__TaskBid__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // FLEET_MSGS__MSG__DETAIL__TASK_BID__STRUCT_H_
