// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from fleet_msgs:msg/TaskAnnouncement.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "fleet_msgs/msg/detail/task_announcement__rosidl_typesupport_introspection_c.h"
#include "fleet_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "fleet_msgs/msg/detail/task_announcement__functions.h"
#include "fleet_msgs/msg/detail/task_announcement__struct.h"


// Include directives for member types
// Member `task_id`
// Member `pickup`
// Member `dropoff`
// Member `capability_requirements`
#include "rosidl_runtime_c/string_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void fleet_msgs__msg__TaskAnnouncement__rosidl_typesupport_introspection_c__TaskAnnouncement_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  fleet_msgs__msg__TaskAnnouncement__init(message_memory);
}

void fleet_msgs__msg__TaskAnnouncement__rosidl_typesupport_introspection_c__TaskAnnouncement_fini_function(void * message_memory)
{
  fleet_msgs__msg__TaskAnnouncement__fini(message_memory);
}

size_t fleet_msgs__msg__TaskAnnouncement__rosidl_typesupport_introspection_c__size_function__TaskAnnouncement__capability_requirements(
  const void * untyped_member)
{
  const rosidl_runtime_c__String__Sequence * member =
    (const rosidl_runtime_c__String__Sequence *)(untyped_member);
  return member->size;
}

const void * fleet_msgs__msg__TaskAnnouncement__rosidl_typesupport_introspection_c__get_const_function__TaskAnnouncement__capability_requirements(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__String__Sequence * member =
    (const rosidl_runtime_c__String__Sequence *)(untyped_member);
  return &member->data[index];
}

void * fleet_msgs__msg__TaskAnnouncement__rosidl_typesupport_introspection_c__get_function__TaskAnnouncement__capability_requirements(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__String__Sequence * member =
    (rosidl_runtime_c__String__Sequence *)(untyped_member);
  return &member->data[index];
}

void fleet_msgs__msg__TaskAnnouncement__rosidl_typesupport_introspection_c__fetch_function__TaskAnnouncement__capability_requirements(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const rosidl_runtime_c__String * item =
    ((const rosidl_runtime_c__String *)
    fleet_msgs__msg__TaskAnnouncement__rosidl_typesupport_introspection_c__get_const_function__TaskAnnouncement__capability_requirements(untyped_member, index));
  rosidl_runtime_c__String * value =
    (rosidl_runtime_c__String *)(untyped_value);
  *value = *item;
}

void fleet_msgs__msg__TaskAnnouncement__rosidl_typesupport_introspection_c__assign_function__TaskAnnouncement__capability_requirements(
  void * untyped_member, size_t index, const void * untyped_value)
{
  rosidl_runtime_c__String * item =
    ((rosidl_runtime_c__String *)
    fleet_msgs__msg__TaskAnnouncement__rosidl_typesupport_introspection_c__get_function__TaskAnnouncement__capability_requirements(untyped_member, index));
  const rosidl_runtime_c__String * value =
    (const rosidl_runtime_c__String *)(untyped_value);
  *item = *value;
}

bool fleet_msgs__msg__TaskAnnouncement__rosidl_typesupport_introspection_c__resize_function__TaskAnnouncement__capability_requirements(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__String__Sequence * member =
    (rosidl_runtime_c__String__Sequence *)(untyped_member);
  rosidl_runtime_c__String__Sequence__fini(member);
  return rosidl_runtime_c__String__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember fleet_msgs__msg__TaskAnnouncement__rosidl_typesupport_introspection_c__TaskAnnouncement_message_member_array[6] = {
  {
    "task_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fleet_msgs__msg__TaskAnnouncement, task_id),  // bytes offset in struct
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
    "pickup",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fleet_msgs__msg__TaskAnnouncement, pickup),  // bytes offset in struct
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
    "dropoff",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fleet_msgs__msg__TaskAnnouncement, dropoff),  // bytes offset in struct
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
    "deadline",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fleet_msgs__msg__TaskAnnouncement, deadline),  // bytes offset in struct
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
    "priority",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fleet_msgs__msg__TaskAnnouncement, priority),  // bytes offset in struct
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
    "capability_requirements",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(fleet_msgs__msg__TaskAnnouncement, capability_requirements),  // bytes offset in struct
    NULL,  // default value
    fleet_msgs__msg__TaskAnnouncement__rosidl_typesupport_introspection_c__size_function__TaskAnnouncement__capability_requirements,  // size() function pointer
    fleet_msgs__msg__TaskAnnouncement__rosidl_typesupport_introspection_c__get_const_function__TaskAnnouncement__capability_requirements,  // get_const(index) function pointer
    fleet_msgs__msg__TaskAnnouncement__rosidl_typesupport_introspection_c__get_function__TaskAnnouncement__capability_requirements,  // get(index) function pointer
    fleet_msgs__msg__TaskAnnouncement__rosidl_typesupport_introspection_c__fetch_function__TaskAnnouncement__capability_requirements,  // fetch(index, &value) function pointer
    fleet_msgs__msg__TaskAnnouncement__rosidl_typesupport_introspection_c__assign_function__TaskAnnouncement__capability_requirements,  // assign(index, value) function pointer
    fleet_msgs__msg__TaskAnnouncement__rosidl_typesupport_introspection_c__resize_function__TaskAnnouncement__capability_requirements,  // resize(index) function pointer
    false  // is_rosidl_buffer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers fleet_msgs__msg__TaskAnnouncement__rosidl_typesupport_introspection_c__TaskAnnouncement_message_members = {
  "fleet_msgs__msg",  // message namespace
  "TaskAnnouncement",  // message name
  6,  // number of fields
  sizeof(fleet_msgs__msg__TaskAnnouncement),
  false,  // has_any_key_member_
  fleet_msgs__msg__TaskAnnouncement__rosidl_typesupport_introspection_c__TaskAnnouncement_message_member_array,  // message members
  fleet_msgs__msg__TaskAnnouncement__rosidl_typesupport_introspection_c__TaskAnnouncement_init_function,  // function to initialize message memory (memory has to be allocated)
  fleet_msgs__msg__TaskAnnouncement__rosidl_typesupport_introspection_c__TaskAnnouncement_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t fleet_msgs__msg__TaskAnnouncement__rosidl_typesupport_introspection_c__TaskAnnouncement_message_type_support_handle = {
  0,
  &fleet_msgs__msg__TaskAnnouncement__rosidl_typesupport_introspection_c__TaskAnnouncement_message_members,
  get_message_typesupport_handle_function,
  &fleet_msgs__msg__TaskAnnouncement__get_type_hash,
  &fleet_msgs__msg__TaskAnnouncement__get_type_description,
  &fleet_msgs__msg__TaskAnnouncement__get_type_description_sources,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_fleet_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, fleet_msgs, msg, TaskAnnouncement)() {
  if (!fleet_msgs__msg__TaskAnnouncement__rosidl_typesupport_introspection_c__TaskAnnouncement_message_type_support_handle.typesupport_identifier) {
    fleet_msgs__msg__TaskAnnouncement__rosidl_typesupport_introspection_c__TaskAnnouncement_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &fleet_msgs__msg__TaskAnnouncement__rosidl_typesupport_introspection_c__TaskAnnouncement_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
