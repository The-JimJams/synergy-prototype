// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from fleet_msgs:msg/RobotIntent.idl
// generated code does not contain a copyright notice

#include "fleet_msgs/msg/detail/robot_intent__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_fleet_msgs
const rosidl_type_hash_t *
fleet_msgs__msg__RobotIntent__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x78, 0x5c, 0x97, 0x58, 0x27, 0x4f, 0x2b, 0x02,
      0x3c, 0xed, 0x07, 0xb5, 0xa0, 0x04, 0x58, 0x83,
      0x53, 0xf4, 0x4d, 0x72, 0x73, 0x4f, 0xf7, 0x16,
      0xd2, 0xba, 0x61, 0xb5, 0x7c, 0xd7, 0xd1, 0x70,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char fleet_msgs__msg__RobotIntent__TYPE_NAME[] = "fleet_msgs/msg/RobotIntent";

// Define type names, field names, and default values
static char fleet_msgs__msg__RobotIntent__FIELD_NAME__robot_id[] = "robot_id";
static char fleet_msgs__msg__RobotIntent__FIELD_NAME__planned_path[] = "planned_path";
static char fleet_msgs__msg__RobotIntent__FIELD_NAME__target_intersection[] = "target_intersection";
static char fleet_msgs__msg__RobotIntent__FIELD_NAME__eta[] = "eta";
static char fleet_msgs__msg__RobotIntent__FIELD_NAME__priority[] = "priority";
static char fleet_msgs__msg__RobotIntent__FIELD_NAME__task_id[] = "task_id";

static rosidl_runtime_c__type_description__Field fleet_msgs__msg__RobotIntent__FIELDS[] = {
  {
    {fleet_msgs__msg__RobotIntent__FIELD_NAME__robot_id, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fleet_msgs__msg__RobotIntent__FIELD_NAME__planned_path, 12, 12},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING_UNBOUNDED_SEQUENCE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fleet_msgs__msg__RobotIntent__FIELD_NAME__target_intersection, 19, 19},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fleet_msgs__msg__RobotIntent__FIELD_NAME__eta, 3, 3},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fleet_msgs__msg__RobotIntent__FIELD_NAME__priority, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fleet_msgs__msg__RobotIntent__FIELD_NAME__task_id, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
fleet_msgs__msg__RobotIntent__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {fleet_msgs__msg__RobotIntent__TYPE_NAME, 26, 26},
      {fleet_msgs__msg__RobotIntent__FIELDS, 6, 6},
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
  "string[] planned_path\n"
  "string target_intersection\n"
  "float64 eta\n"
  "int32 priority\n"
  "string task_id";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
fleet_msgs__msg__RobotIntent__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {fleet_msgs__msg__RobotIntent__TYPE_NAME, 26, 26},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 107, 107},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
fleet_msgs__msg__RobotIntent__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *fleet_msgs__msg__RobotIntent__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
