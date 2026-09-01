// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from fleet_msgs:msg/TaskAnnouncement.idl
// generated code does not contain a copyright notice
#include "fleet_msgs/msg/detail/task_announcement__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <cstddef>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/serialization_helpers.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "fleet_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "fleet_msgs/msg/detail/task_announcement__struct.h"
#include "fleet_msgs/msg/detail/task_announcement__functions.h"
#include "fastcdr/Cdr.h"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

// includes and forward declarations of message dependencies and their conversion functions

#if defined(__cplusplus)
extern "C"
{
#endif

#include "rosidl_runtime_c/string.h"  // capability_requirements, dropoff, pickup, task_id
#include "rosidl_runtime_c/string_functions.h"  // capability_requirements, dropoff, pickup, task_id

// forward declare type support functions


using _TaskAnnouncement__ros_msg_type = fleet_msgs__msg__TaskAnnouncement;


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fleet_msgs
bool cdr_serialize_fleet_msgs__msg__TaskAnnouncement(
  const fleet_msgs__msg__TaskAnnouncement * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: task_id
  {
    const rosidl_runtime_c__String * str = &ros_message->task_id;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  // Field name: pickup
  {
    const rosidl_runtime_c__String * str = &ros_message->pickup;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  // Field name: dropoff
  {
    const rosidl_runtime_c__String * str = &ros_message->dropoff;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  // Field name: deadline
  {
    cdr << ros_message->deadline;
  }

  // Field name: priority
  {
    cdr << ros_message->priority;
  }

  // Field name: capability_requirements
  {
    size_t size = ros_message->capability_requirements.size;
    auto array_ptr = ros_message->capability_requirements.data;
    cdr << static_cast<uint32_t>(size);
    for (size_t i = 0; i < size; ++i) {
      const rosidl_runtime_c__String * str = &array_ptr[i];
      if (str->capacity == 0 || str->capacity <= str->size) {
        fprintf(stderr, "string capacity not greater than size\n");
        return false;
      }
      if (str->data[str->size] != '\0') {
        fprintf(stderr, "string not null-terminated\n");
        return false;
      }
      cdr << str->data;
    }
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fleet_msgs
bool cdr_deserialize_fleet_msgs__msg__TaskAnnouncement(
  eprosima::fastcdr::Cdr & cdr,
  fleet_msgs__msg__TaskAnnouncement * ros_message)
{
  // Field name: task_id
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->task_id.data) {
      rosidl_runtime_c__String__init(&ros_message->task_id);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->task_id,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'task_id'\n");
      return false;
    }
  }

  // Field name: pickup
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->pickup.data) {
      rosidl_runtime_c__String__init(&ros_message->pickup);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->pickup,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'pickup'\n");
      return false;
    }
  }

  // Field name: dropoff
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->dropoff.data) {
      rosidl_runtime_c__String__init(&ros_message->dropoff);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->dropoff,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'dropoff'\n");
      return false;
    }
  }

  // Field name: deadline
  {
    cdr >> ros_message->deadline;
  }

  // Field name: priority
  {
    cdr >> ros_message->priority;
  }

  // Field name: capability_requirements
  {
    uint32_t cdrSize;
    cdr >> cdrSize;
    size_t size = static_cast<size_t>(cdrSize);

    // Check there are at least 'size' remaining bytes in the CDR stream before resizing
    auto old_state = cdr.get_state();
    bool correct_size = cdr.jump(size);
    cdr.set_state(old_state);
    if (!correct_size) {
      fprintf(stderr, "sequence size exceeds remaining buffer\n");
      return false;
    }

    if (ros_message->capability_requirements.data) {
      rosidl_runtime_c__String__Sequence__fini(&ros_message->capability_requirements);
    }
    if (!rosidl_runtime_c__String__Sequence__init(&ros_message->capability_requirements, size)) {
      fprintf(stderr, "failed to create array for field 'capability_requirements'");
      return false;
    }
    auto array_ptr = ros_message->capability_requirements.data;
    for (size_t i = 0; i < size; ++i) {
      std::string tmp;
      cdr >> tmp;
      auto & ros_i = array_ptr[i];
      if (!ros_i.data) {
        rosidl_runtime_c__String__init(&ros_i);
      }
      bool succeeded = rosidl_runtime_c__String__assign(&ros_i, tmp.c_str());
      if (!succeeded) {
        fprintf(stderr, "failed to assign string into field 'capability_requirements'\n");
        return false;
      }
    }
  }

  return true;
}  // NOLINT(readability/fn_size)


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fleet_msgs
size_t get_serialized_size_fleet_msgs__msg__TaskAnnouncement(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _TaskAnnouncement__ros_msg_type * ros_message = static_cast<const _TaskAnnouncement__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: task_id
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->task_id.size + 1);

  // Field name: pickup
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->pickup.size + 1);

  // Field name: dropoff
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->dropoff.size + 1);

  // Field name: deadline
  {
    size_t item_size = sizeof(ros_message->deadline);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: priority
  {
    size_t item_size = sizeof(ros_message->priority);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: capability_requirements
  {
    size_t array_size = ros_message->capability_requirements.size;
    auto array_ptr = ros_message->capability_requirements.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        (array_ptr[index].size + 1);
    }
  }

  return current_alignment - initial_alignment;
}


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fleet_msgs
size_t max_serialized_size_fleet_msgs__msg__TaskAnnouncement(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;

  // Field name: task_id
  {
    size_t array_size = 1;
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  // Field name: pickup
  {
    size_t array_size = 1;
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  // Field name: dropoff
  {
    size_t array_size = 1;
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  // Field name: deadline
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint64_t);
    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }

  // Field name: priority
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: capability_requirements
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }


  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = fleet_msgs__msg__TaskAnnouncement;
    is_plain =
      (
      offsetof(DataType, capability_requirements) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fleet_msgs
bool cdr_serialize_key_fleet_msgs__msg__TaskAnnouncement(
  const fleet_msgs__msg__TaskAnnouncement * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: task_id
  {
    const rosidl_runtime_c__String * str = &ros_message->task_id;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  // Field name: pickup
  {
    const rosidl_runtime_c__String * str = &ros_message->pickup;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  // Field name: dropoff
  {
    const rosidl_runtime_c__String * str = &ros_message->dropoff;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  // Field name: deadline
  {
    cdr << ros_message->deadline;
  }

  // Field name: priority
  {
    cdr << ros_message->priority;
  }

  // Field name: capability_requirements
  {
    size_t size = ros_message->capability_requirements.size;
    auto array_ptr = ros_message->capability_requirements.data;
    cdr << static_cast<uint32_t>(size);
    for (size_t i = 0; i < size; ++i) {
      const rosidl_runtime_c__String * str = &array_ptr[i];
      if (str->capacity == 0 || str->capacity <= str->size) {
        fprintf(stderr, "string capacity not greater than size\n");
        return false;
      }
      if (str->data[str->size] != '\0') {
        fprintf(stderr, "string not null-terminated\n");
        return false;
      }
      cdr << str->data;
    }
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fleet_msgs
size_t get_serialized_size_key_fleet_msgs__msg__TaskAnnouncement(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _TaskAnnouncement__ros_msg_type * ros_message = static_cast<const _TaskAnnouncement__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;

  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: task_id
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->task_id.size + 1);

  // Field name: pickup
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->pickup.size + 1);

  // Field name: dropoff
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->dropoff.size + 1);

  // Field name: deadline
  {
    size_t item_size = sizeof(ros_message->deadline);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: priority
  {
    size_t item_size = sizeof(ros_message->priority);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: capability_requirements
  {
    size_t array_size = ros_message->capability_requirements.size;
    auto array_ptr = ros_message->capability_requirements.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        (array_ptr[index].size + 1);
    }
  }

  return current_alignment - initial_alignment;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_fleet_msgs
size_t max_serialized_size_key_fleet_msgs__msg__TaskAnnouncement(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;
  // Field name: task_id
  {
    size_t array_size = 1;
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  // Field name: pickup
  {
    size_t array_size = 1;
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  // Field name: dropoff
  {
    size_t array_size = 1;
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  // Field name: deadline
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint64_t);
    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }

  // Field name: priority
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: capability_requirements
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = fleet_msgs__msg__TaskAnnouncement;
    is_plain =
      (
      offsetof(DataType, capability_requirements) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}


static bool _TaskAnnouncement__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const fleet_msgs__msg__TaskAnnouncement * ros_message = static_cast<const fleet_msgs__msg__TaskAnnouncement *>(untyped_ros_message);
  (void)ros_message;
  return cdr_serialize_fleet_msgs__msg__TaskAnnouncement(ros_message, cdr);
}

static bool _TaskAnnouncement__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  fleet_msgs__msg__TaskAnnouncement * ros_message = static_cast<fleet_msgs__msg__TaskAnnouncement *>(untyped_ros_message);
  (void)ros_message;
  return cdr_deserialize_fleet_msgs__msg__TaskAnnouncement(cdr, ros_message);
}

static uint32_t _TaskAnnouncement__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_fleet_msgs__msg__TaskAnnouncement(
      untyped_ros_message, 0));
}

static size_t _TaskAnnouncement__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_fleet_msgs__msg__TaskAnnouncement(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_TaskAnnouncement = {
  "fleet_msgs::msg",
  "TaskAnnouncement",
  _TaskAnnouncement__cdr_serialize,
  _TaskAnnouncement__cdr_deserialize,
  _TaskAnnouncement__get_serialized_size,
  _TaskAnnouncement__max_serialized_size,
  nullptr,
  false,
  nullptr,
  nullptr
};

static rosidl_message_type_support_t _TaskAnnouncement__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_TaskAnnouncement,
  get_message_typesupport_handle_function,
  &fleet_msgs__msg__TaskAnnouncement__get_type_hash,
  &fleet_msgs__msg__TaskAnnouncement__get_type_description,
  &fleet_msgs__msg__TaskAnnouncement__get_type_description_sources,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, fleet_msgs, msg, TaskAnnouncement)() {
  return &_TaskAnnouncement__type_support;
}

#if defined(__cplusplus)
}
#endif
