// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from fleet_msgs:msg/ResourceClaim.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fleet_msgs/msg/resource_claim.h"


#ifndef FLEET_MSGS__MSG__DETAIL__RESOURCE_CLAIM__STRUCT_H_
#define FLEET_MSGS__MSG__DETAIL__RESOURCE_CLAIM__STRUCT_H_

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
// Member 'resource'
// Member 'claim_id'
// Member 'status'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/ResourceClaim in the package fleet_msgs.
typedef struct fleet_msgs__msg__ResourceClaim
{
  rosidl_runtime_c__String robot_id;
  rosidl_runtime_c__String resource;
  double start_time;
  double end_time;
  int32_t priority;
  rosidl_runtime_c__String claim_id;
  rosidl_runtime_c__String status;
} fleet_msgs__msg__ResourceClaim;

// Struct for a sequence of fleet_msgs__msg__ResourceClaim.
typedef struct fleet_msgs__msg__ResourceClaim__Sequence
{
  fleet_msgs__msg__ResourceClaim * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} fleet_msgs__msg__ResourceClaim__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // FLEET_MSGS__MSG__DETAIL__RESOURCE_CLAIM__STRUCT_H_
