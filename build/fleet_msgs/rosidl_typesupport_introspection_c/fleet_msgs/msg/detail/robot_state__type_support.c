// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from fleet_msgs:msg/RobotState.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "fleet_msgs/msg/detail/robot_state__rosidl_typesupport_introspection_c.h"
#include "fleet_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "fleet_msgs/msg/detail/robot_state__functions.h"
#include "fleet_msgs/msg/detail/robot_state__struct.h"


// Include directives for member types
// Member `robot_id`
// Member `current_task`
// Member `status`
#include "rosidl_runtime_c/string_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void fleet_msgs__msg__RobotState__rosidl_typesupport_introspection_c__RobotState_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  fleet_msgs__msg__RobotState__init(message_memory);
}

void fleet_msgs__msg__RobotState__rosidl_typesupport_introspection_c__RobotState_fini_function(void * message_memory)
{
  fleet_msgs__msg__RobotState__fini(message_memory);
}

size_t fleet_msgs__msg__RobotState__rosidl_typesupport_introspection_c__size_function__RobotState__position(
  const void * untyped_member)
{
  (void)untyped_member;
  return 2;
}

const void * fleet_msgs__msg__RobotState__rosidl_typesupport_introspection_c__get_const_function__RobotState__position(
  const void * untyped_member, size_t index)
{
  const double * member =
    (const double *)(untyped_member);
  return &member[index];
}

void * fleet_msgs__msg__RobotState__rosidl_typesupport_introspection_c__get_function__RobotState__position(
  void * untyped_member, size_t index)
{
  double * member =
    (double *)(untyped_member);
  return &member[index];
}

void fleet_msgs__msg__RobotState__rosidl_typesupport_introspection_c__fetch_function__RobotState__position(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const double * item =
    ((const double *)
    fleet_msgs__msg__RobotState__rosidl_typesupport_introspection_c__get_const_function__RobotState__position(untyped_member, index));
  double * value =
    (double *)(untyped_value);
  *value = *item;
}

void fleet_msgs__msg__RobotState__rosidl_typesupport_introspection_c__assign_function__RobotState__position(
  void * untyped_member, size_t index, const void * untyped_value)
{
  double * item =
    ((double *)
    fleet_msgs__msg__RobotState__rosidl_typesupport_introspection_c__get_function__RobotState__position(untyped_member, index));
  const double * value =
    (const double *)(untyped_value);
  *item = *value;
}

static rosidl_typesupport_introspection_c__MessageMember fleet_msgs__msg__RobotState__rosidl_typesupport_introspection_c__RobotState_message_member_array[7] = {
  {
    "robot_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fleet_msgs__msg__RobotState, robot_id),  // bytes offset in struct
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
    "timestamp",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fleet_msgs__msg__RobotState, timestamp),  // bytes offset in struct
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
    "position",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    true,  // is array
    2,  // array size
    false,  // is upper bound
    offsetof(fleet_msgs__msg__RobotState, position),  // bytes offset in struct
    NULL,  // default value
    fleet_msgs__msg__RobotState__rosidl_typesupport_introspection_c__size_function__RobotState__position,  // size() function pointer
    fleet_msgs__msg__RobotState__rosidl_typesupport_introspection_c__get_const_function__RobotState__position,  // get_const(index) function pointer
    fleet_msgs__msg__RobotState__rosidl_typesupport_introspection_c__get_function__RobotState__position,  // get(index) function pointer
    fleet_msgs__msg__RobotState__rosidl_typesupport_introspection_c__fetch_function__RobotState__position,  // fetch(index, &value) function pointer
    fleet_msgs__msg__RobotState__rosidl_typesupport_introspection_c__assign_function__RobotState__position,  // assign(index, value) function pointer
    NULL,  // resize(index) function pointer
    false  // is_rosidl_buffer
  },
  {
    "velocity",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fleet_msgs__msg__RobotState, velocity),  // bytes offset in struct
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
    "battery",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fleet_msgs__msg__RobotState, battery),  // bytes offset in struct
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
    "current_task",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fleet_msgs__msg__RobotState, current_task),  // bytes offset in struct
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
    "status",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fleet_msgs__msg__RobotState, status),  // bytes offset in struct
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

static const rosidl_typesupport_introspection_c__MessageMembers fleet_msgs__msg__RobotState__rosidl_typesupport_introspection_c__RobotState_message_members = {
  "fleet_msgs__msg",  // message namespace
  "RobotState",  // message name
  7,  // number of fields
  sizeof(fleet_msgs__msg__RobotState),
  false,  // has_any_key_member_
  fleet_msgs__msg__RobotState__rosidl_typesupport_introspection_c__RobotState_message_member_array,  // message members
  fleet_msgs__msg__RobotState__rosidl_typesupport_introspection_c__RobotState_init_function,  // function to initialize message memory (memory has to be allocated)
  fleet_msgs__msg__RobotState__rosidl_typesupport_introspection_c__RobotState_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t fleet_msgs__msg__RobotState__rosidl_typesupport_introspection_c__RobotState_message_type_support_handle = {
  0,
  &fleet_msgs__msg__RobotState__rosidl_typesupport_introspection_c__RobotState_message_members,
  get_message_typesupport_handle_function,
  &fleet_msgs__msg__RobotState__get_type_hash,
  &fleet_msgs__msg__RobotState__get_type_description,
  &fleet_msgs__msg__RobotState__get_type_description_sources,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_fleet_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, fleet_msgs, msg, RobotState)() {
  if (!fleet_msgs__msg__RobotState__rosidl_typesupport_introspection_c__RobotState_message_type_support_handle.typesupport_identifier) {
    fleet_msgs__msg__RobotState__rosidl_typesupport_introspection_c__RobotState_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &fleet_msgs__msg__RobotState__rosidl_typesupport_introspection_c__RobotState_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
