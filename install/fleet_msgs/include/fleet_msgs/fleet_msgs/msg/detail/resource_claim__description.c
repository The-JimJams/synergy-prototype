// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from fleet_msgs:msg/ResourceClaim.idl
// generated code does not contain a copyright notice

#include "fleet_msgs/msg/detail/resource_claim__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_fleet_msgs
const rosidl_type_hash_t *
fleet_msgs__msg__ResourceClaim__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xc3, 0xa4, 0xf4, 0x72, 0x4e, 0xc3, 0x79, 0x1f,
      0xe8, 0xf7, 0x7a, 0x63, 0xfe, 0xc7, 0x1f, 0x3c,
      0x9b, 0xbe, 0xbb, 0x98, 0x4a, 0x11, 0x89, 0x92,
      0xee, 0x78, 0xc5, 0xbf, 0x0c, 0x5c, 0x07, 0x59,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char fleet_msgs__msg__ResourceClaim__TYPE_NAME[] = "fleet_msgs/msg/ResourceClaim";

// Define type names, field names, and default values
static char fleet_msgs__msg__ResourceClaim__FIELD_NAME__robot_id[] = "robot_id";
static char fleet_msgs__msg__ResourceClaim__FIELD_NAME__resource[] = "resource";
static char fleet_msgs__msg__ResourceClaim__FIELD_NAME__start_time[] = "start_time";
static char fleet_msgs__msg__ResourceClaim__FIELD_NAME__end_time[] = "end_time";
static char fleet_msgs__msg__ResourceClaim__FIELD_NAME__priority[] = "priority";
static char fleet_msgs__msg__ResourceClaim__FIELD_NAME__claim_id[] = "claim_id";
static char fleet_msgs__msg__ResourceClaim__FIELD_NAME__status[] = "status";

static rosidl_runtime_c__type_description__Field fleet_msgs__msg__ResourceClaim__FIELDS[] = {
  {
    {fleet_msgs__msg__ResourceClaim__FIELD_NAME__robot_id, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fleet_msgs__msg__ResourceClaim__FIELD_NAME__resource, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fleet_msgs__msg__ResourceClaim__FIELD_NAME__start_time, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fleet_msgs__msg__ResourceClaim__FIELD_NAME__end_time, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fleet_msgs__msg__ResourceClaim__FIELD_NAME__priority, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fleet_msgs__msg__ResourceClaim__FIELD_NAME__claim_id, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fleet_msgs__msg__ResourceClaim__FIELD_NAME__status, 6, 6},
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
fleet_msgs__msg__ResourceClaim__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {fleet_msgs__msg__ResourceClaim__TYPE_NAME, 28, 28},
      {fleet_msgs__msg__ResourceClaim__FIELDS, 7, 7},
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
  "string resource\n"
  "float64 start_time\n"
  "float64 end_time\n"
  "int32 priority\n"
  "string claim_id\n"
  "string status";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
fleet_msgs__msg__ResourceClaim__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {fleet_msgs__msg__ResourceClaim__TYPE_NAME, 28, 28},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 113, 113},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
fleet_msgs__msg__ResourceClaim__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *fleet_msgs__msg__ResourceClaim__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
