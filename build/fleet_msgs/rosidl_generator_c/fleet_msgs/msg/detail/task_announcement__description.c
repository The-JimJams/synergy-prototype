// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from fleet_msgs:msg/TaskAnnouncement.idl
// generated code does not contain a copyright notice

#include "fleet_msgs/msg/detail/task_announcement__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_fleet_msgs
const rosidl_type_hash_t *
fleet_msgs__msg__TaskAnnouncement__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x70, 0xa8, 0x51, 0x89, 0x2d, 0x98, 0x66, 0x77,
      0xe2, 0x35, 0xf6, 0x65, 0x1d, 0x05, 0x61, 0xfd,
      0x9f, 0x73, 0x94, 0xb2, 0xea, 0x8e, 0x3b, 0x66,
      0x19, 0x54, 0xd9, 0xd3, 0xc4, 0x1f, 0xd6, 0x26,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char fleet_msgs__msg__TaskAnnouncement__TYPE_NAME[] = "fleet_msgs/msg/TaskAnnouncement";

// Define type names, field names, and default values
static char fleet_msgs__msg__TaskAnnouncement__FIELD_NAME__task_id[] = "task_id";
static char fleet_msgs__msg__TaskAnnouncement__FIELD_NAME__pickup[] = "pickup";
static char fleet_msgs__msg__TaskAnnouncement__FIELD_NAME__dropoff[] = "dropoff";
static char fleet_msgs__msg__TaskAnnouncement__FIELD_NAME__deadline[] = "deadline";
static char fleet_msgs__msg__TaskAnnouncement__FIELD_NAME__priority[] = "priority";
static char fleet_msgs__msg__TaskAnnouncement__FIELD_NAME__capability_requirements[] = "capability_requirements";

static rosidl_runtime_c__type_description__Field fleet_msgs__msg__TaskAnnouncement__FIELDS[] = {
  {
    {fleet_msgs__msg__TaskAnnouncement__FIELD_NAME__task_id, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fleet_msgs__msg__TaskAnnouncement__FIELD_NAME__pickup, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fleet_msgs__msg__TaskAnnouncement__FIELD_NAME__dropoff, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fleet_msgs__msg__TaskAnnouncement__FIELD_NAME__deadline, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fleet_msgs__msg__TaskAnnouncement__FIELD_NAME__priority, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {fleet_msgs__msg__TaskAnnouncement__FIELD_NAME__capability_requirements, 23, 23},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING_UNBOUNDED_SEQUENCE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
fleet_msgs__msg__TaskAnnouncement__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {fleet_msgs__msg__TaskAnnouncement__TYPE_NAME, 31, 31},
      {fleet_msgs__msg__TaskAnnouncement__FIELDS, 6, 6},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "string task_id\n"
  "string pickup\n"
  "string dropoff\n"
  "float64 deadline\n"
  "int32 priority\n"
  "string[] capability_requirements";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
fleet_msgs__msg__TaskAnnouncement__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {fleet_msgs__msg__TaskAnnouncement__TYPE_NAME, 31, 31},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 109, 109},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
fleet_msgs__msg__TaskAnnouncement__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *fleet_msgs__msg__TaskAnnouncement__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
