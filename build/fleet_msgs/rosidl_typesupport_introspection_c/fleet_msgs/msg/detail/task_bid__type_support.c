// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from fleet_msgs:msg/TaskBid.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "fleet_msgs/msg/detail/task_bid__rosidl_typesupport_introspection_c.h"
#include "fleet_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "fleet_msgs/msg/detail/task_bid__functions.h"
#include "fleet_msgs/msg/detail/task_bid__struct.h"


// Include directives for member types
// Member `robot_id`
// Member `task_id`
#include "rosidl_runtime_c/string_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void fleet_msgs__msg__TaskBid__rosidl_typesupport_introspection_c__TaskBid_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  fleet_msgs__msg__TaskBid__init(message_memory);
}

void fleet_msgs__msg__TaskBid__rosidl_typesupport_introspection_c__TaskBid_fini_function(void * message_memory)
{
  fleet_msgs__msg__TaskBid__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember fleet_msgs__msg__TaskBid__rosidl_typesupport_introspection_c__TaskBid_message_member_array[6] = {
  {
    "robot_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fleet_msgs__msg__TaskBid, robot_id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL,  // resize(index) function pointer
    false  // is_rosidl_buffer
  },
  {
    "task_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fleet_msgs__msg__TaskBid, task_id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL,  // resize(index) function pointer
    false  // is_rosidl_buffer
  },
  {
    "estimated_time",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fleet_msgs__msg__TaskBid, estimated_time),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL,  // resize(index) function pointer
    false  // is_rosidl_buffer
  },
  {
    "distance",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fleet_msgs__msg__TaskBid, distance),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL,  // resize(index) function pointer
    false  // is_rosidl_buffer
  },
  {
    "battery_cost",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fleet_msgs__msg__TaskBid, battery_cost),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL,  // resize(index) function pointer
    false  // is_rosidl_buffer
  },
  {
    "confidence",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fleet_msgs__msg__TaskBid, confidence),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL,  // resize(index) function pointer
    false  // is_rosidl_buffer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers fleet_msgs__msg__TaskBid__rosidl_typesupport_introspection_c__TaskBid_message_members = {
  "fleet_msgs__msg",  // message namespace
  "TaskBid",  // message name
  6,  // number of fields
  sizeof(fleet_msgs__msg__TaskBid),
  false,  // has_any_key_member_
  fleet_msgs__msg__TaskBid__rosidl_typesupport_introspection_c__TaskBid_message_member_array,  // message members
  fleet_msgs__msg__TaskBid__rosidl_typesupport_introspection_c__TaskBid_init_function,  // function to initialize message memory (memory has to be allocated)
  fleet_msgs__msg__TaskBid__rosidl_typesupport_introspection_c__TaskBid_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t fleet_msgs__msg__TaskBid__rosidl_typesupport_introspection_c__TaskBid_message_type_support_handle = {
  0,
  &fleet_msgs__msg__TaskBid__rosidl_typesupport_introspection_c__TaskBid_message_members,
  get_message_typesupport_handle_function,
  &fleet_msgs__msg__TaskBid__get_type_hash,
  &fleet_msgs__msg__TaskBid__get_type_description,
  &fleet_msgs__msg__TaskBid__get_type_description_sources,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_fleet_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, fleet_msgs, msg, TaskBid)() {
  if (!fleet_msgs__msg__TaskBid__rosidl_typesupport_introspection_c__TaskBid_message_type_support_handle.typesupport_identifier) {
    fleet_msgs__msg__TaskBid__rosidl_typesupport_introspection_c__TaskBid_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &fleet_msgs__msg__TaskBid__rosidl_typesupport_introspection_c__TaskBid_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
