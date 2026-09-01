// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from fleet_msgs:msg/TaskAnnouncement.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fleet_msgs/msg/task_announcement.h"


#ifndef FLEET_MSGS__MSG__DETAIL__TASK_ANNOUNCEMENT__STRUCT_H_
#define FLEET_MSGS__MSG__DETAIL__TASK_ANNOUNCEMENT__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

// Include directives for member types
// Member 'task_id'
// Member 'pickup'
// Member 'dropoff'
// Member 'capability_requirements'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/TaskAnnouncement in the package fleet_msgs.
typedef struct fleet_msgs__msg__TaskAnnouncement
{
  rosidl_runtime_c__String task_id;
  rosidl_runtime_c__String pickup;
  rosidl_runtime_c__String dropoff;
  double deadline;
  int32_t priority;
  rosidl_runtime_c__String__Sequence capability_requirements;
} fleet_msgs__msg__TaskAnnouncement;

// Struct for a sequence of fleet_msgs__msg__TaskAnnouncement.
typedef struct fleet_msgs__msg__TaskAnnouncement__Sequence
{
  fleet_msgs__msg__TaskAnnouncement * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} fleet_msgs__msg__TaskAnnouncement__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // FLEET_MSGS__MSG__DETAIL__TASK_ANNOUNCEMENT__STRUCT_H_
