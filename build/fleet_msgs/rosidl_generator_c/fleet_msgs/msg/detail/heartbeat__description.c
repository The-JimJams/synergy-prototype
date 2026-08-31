// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from fleet_msgs:msg/Heartbeat.idl
// generated code does not contain a copyright notice

#include "fleet_msgs/msg/detail/heartbeat__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_fleet_msgs
const rosidl_type_hash_t *
fleet_msgs__msg__Heartbeat__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x48, 0x17, 0xfd, 0x0e, 0xba, 0x66, 0x3a, 0x31,
      0x1f, 0x50, 0x72, 0x4f, 0x42, 0xd0, 0x89, 0xc8,
      0x3d, 0x7d, 0xc6, 0x87, 0x62, 0x7c, 0xd1, 0x69,
      0x19, 0xbe, 0xbb, 0x19, 0x50, 0x1f, 0x71, 0x66,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char fleet_msgs__msg__Heartbeat__TYPE_NAME[] = "fleet_msgs/msg/Heartbeat";

// Define type names, field names, and default values
static char fleet_msgs__msg__Heartbeat__FIELD_NAME__robot_id[] = "robot_id";
static char fleet_msgs__msg__Heartbeat__FIELD_NAME__timestamp[] = "timestamp";

static rosidl_runtime_c__type_description__Field fleet_msgs__msg__Heartbeat__FIELDS[] = {
  {
    {fleet_msgs__msg__Heartbeat__FIELD_NAME__robot_id, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fleet_msgs__msg__Heartbeat__FIELD_NAME__timestamp, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
fleet_msgs__msg__Heartbeat__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {fleet_msgs__msg__Heartbeat__TYPE_NAME, 24, 24},
      {fleet_msgs__msg__Heartbeat__FIELDS, 2, 2},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "string robot_id\n"
  "float64 timestamp";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
fleet_msgs__msg__Heartbeat__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {fleet_msgs__msg__Heartbeat__TYPE_NAME, 24, 24},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 34, 34},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
fleet_msgs__msg__Heartbeat__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *fleet_msgs__msg__Heartbeat__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
