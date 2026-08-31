// generated from rosidl_typesupport_fastrtps_c/resource/idl__rosidl_typesupport_fastrtps_c.h.em
// with input from fleet_msgs:msg/TaskBid.idl
// generated code does not contain a copyright notice
#ifndef FLEET_MSGS__MSG__DETAIL__TASK_BID__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_
#define FLEET_MSGS__MSG__DETAIL__TASK_BID__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_


#include <stddef.h>
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_interface/macros.h"
#include "fleet_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "fleet_msgs/msg/detail/task_bid__struct.h"
#include "fastcdr/Cdr.h"

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fleet_msgs
bool cdr_serialize_fleet_msgs__msg__TaskBid(
  const fleet_msgs__msg__TaskBid * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fleet_msgs
bool cdr_deserialize_fleet_msgs__msg__TaskBid(
  eprosima::fastcdr::Cdr &,
  fleet_msgs__msg__TaskBid * ros_message);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fleet_msgs
size_t get_serialized_size_fleet_msgs__msg__TaskBid(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fleet_msgs
size_t max_serialized_size_fleet_msgs__msg__TaskBid(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fleet_msgs
bool cdr_serialize_key_fleet_msgs__msg__TaskBid(
  const fleet_msgs__msg__TaskBid * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fleet_msgs
size_t get_serialized_size_key_fleet_msgs__msg__TaskBid(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fleet_msgs
size_t max_serialized_size_key_fleet_msgs__msg__TaskBid(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fleet_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, fleet_msgs, msg, TaskBid)();

#ifdef __cplusplus
}
#endif

#endif  // FLEET_MSGS__MSG__DETAIL__TASK_BID__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_
