// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from fleet_msgs:msg/TaskBid.idl
// generated code does not contain a copyright notice

#include "fleet_msgs/msg/detail/task_bid__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_fleet_msgs
const rosidl_type_hash_t *
fleet_msgs__msg__TaskBid__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x89, 0xac, 0xb4, 0x94, 0xaf, 0x1e, 0x29, 0xd3,
      0x01, 0x28, 0xf2, 0x08, 0x6f, 0xe8, 0xd3, 0xe1,
      0xe5, 0xe1, 0x51, 0x94, 0x3d, 0x91, 0x82, 0xa9,
      0x24, 0x30, 0x40, 0xa3, 0x97, 0x70, 0x74, 0xdb,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char fleet_msgs__msg__TaskBid__TYPE_NAME[] = "fleet_msgs/msg/TaskBid";

// Define type names, field names, and default values
static char fleet_msgs__msg__TaskBid__FIELD_NAME__robot_id[] = "robot_id";
static char fleet_msgs__msg__TaskBid__FIELD_NAME__task_id[] = "task_id";
static char fleet_msgs__msg__TaskBid__FIELD_NAME__estimated_time[] = "estimated_time";
static char fleet_msgs__msg__TaskBid__FIELD_NAME__distance[] = "distance";
static char fleet_msgs__msg__TaskBid__FIELD_NAME__battery_cost[] = "battery_cost";
static char fleet_msgs__msg__TaskBid__FIELD_NAME__confidence[] = "confidence";

static rosidl_runtime_c__type_description__Field fleet_msgs__msg__TaskBid__FIELDS[] = {
  {
    {fleet_msgs__msg__TaskBid__FIELD_NAME__robot_id, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fleet_msgs__msg__TaskBid__FIELD_NAME__task_id, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fleet_msgs__msg__TaskBid__FIELD_NAME__estimated_time, 14, 14},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fleet_msgs__msg__TaskBid__FIELD_NAME__distance, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fleet_msgs__msg__TaskBid__FIELD_NAME__battery_cost, 12, 12},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fleet_msgs__msg__TaskBid__FIELD_NAME__confidence, 10, 10},
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
fleet_msgs__msg__TaskBid__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {fleet_msgs__msg__TaskBid__TYPE_NAME, 22, 22},
      {fleet_msgs__msg__TaskBid__FIELDS, 6, 6},
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
  "string task_id\n"
  "float64 estimated_time\n"
  "float64 distance\n"
  "float64 battery_cost\n"
  "float64 confidence";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
fleet_msgs__msg__TaskBid__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {fleet_msgs__msg__TaskBid__TYPE_NAME, 22, 22},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 111, 111},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
fleet_msgs__msg__TaskBid__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *fleet_msgs__msg__TaskBid__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
