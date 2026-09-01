// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from fleet_msgs:msg/TaskAnnouncement.idl
// generated code does not contain a copyright notice
#include "fleet_msgs/msg/detail/task_announcement__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `task_id`
// Member `pickup`
// Member `dropoff`
// Member `capability_requirements`
#include "rosidl_runtime_c/string_functions.h"

bool
fleet_msgs__msg__TaskAnnouncement__init(fleet_msgs__msg__TaskAnnouncement * msg)
{
  if (!msg) {
    return false;
  }
  // task_id
  if (!rosidl_runtime_c__String__init(&msg->task_id)) {
    fleet_msgs__msg__TaskAnnouncement__fini(msg);
    return false;
  }
  // pickup
  if (!rosidl_runtime_c__String__init(&msg->pickup)) {
    fleet_msgs__msg__TaskAnnouncement__fini(msg);
    return false;
  }
  // dropoff
  if (!rosidl_runtime_c__String__init(&msg->dropoff)) {
    fleet_msgs__msg__TaskAnnouncement__fini(msg);
    return false;
  }
  // deadline
  // priority
  // capability_requirements
  if (!rosidl_runtime_c__String__Sequence__init(&msg->capability_requirements, 0)) {
    fleet_msgs__msg__TaskAnnouncement__fini(msg);
    return false;
  }
  return true;
}

void
fleet_msgs__msg__TaskAnnouncement__fini(fleet_msgs__msg__TaskAnnouncement * msg)
{
  if (!msg) {
    return;
  }
  // task_id
  rosidl_runtime_c__String__fini(&msg->task_id);
  // pickup
  rosidl_runtime_c__String__fini(&msg->pickup);
  // dropoff
  rosidl_runtime_c__String__fini(&msg->dropoff);
  // deadline
  // priority
  // capability_requirements
  rosidl_runtime_c__String__Sequence__fini(&msg->capability_requirements);
}

bool
fleet_msgs__msg__TaskAnnouncement__are_equal(const fleet_msgs__msg__TaskAnnouncement * lhs, const fleet_msgs__msg__TaskAnnouncement * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // task_id
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->task_id), &(rhs->task_id)))
  {
    return false;
  }
  // pickup
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->pickup), &(rhs->pickup)))
  {
    return false;
  }
  // dropoff
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->dropoff), &(rhs->dropoff)))
  {
    return false;
  }
  // deadline
  if (lhs->deadline != rhs->deadline) {
    return false;
  }
  // priority
  if (lhs->priority != rhs->priority) {
    return false;
  }
  // capability_requirements
  if (!rosidl_runtime_c__String__Sequence__are_equal(
      &(lhs->capability_requirements), &(rhs->capability_requirements)))
  {
    return false;
  }
  return true;
}

bool
fleet_msgs__msg__TaskAnnouncement__copy(
  const fleet_msgs__msg__TaskAnnouncement * input,
  fleet_msgs__msg__TaskAnnouncement * output)
{
  if (!input || !output) {
    return false;
  }
  // task_id
  if (!rosidl_runtime_c__String__copy(
      &(input->task_id), &(output->task_id)))
  {
    return false;
  }
  // pickup
  if (!rosidl_runtime_c__String__copy(
      &(input->pickup), &(output->pickup)))
  {
    return false;
  }
  // dropoff
  if (!rosidl_runtime_c__String__copy(
      &(input->dropoff), &(output->dropoff)))
  {
    return false;
  }
  // deadline
  output->deadline = input->deadline;
  // priority
  output->priority = input->priority;
  // capability_requirements
  if (!rosidl_runtime_c__String__Sequence__copy(
      &(input->capability_requirements), &(output->capability_requirements)))
  {
    return false;
  }
  return true;
}

fleet_msgs__msg__TaskAnnouncement *
fleet_msgs__msg__TaskAnnouncement__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fleet_msgs__msg__TaskAnnouncement * msg = (fleet_msgs__msg__TaskAnnouncement *)allocator.allocate(sizeof(fleet_msgs__msg__TaskAnnouncement), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(fleet_msgs__msg__TaskAnnouncement));
  bool success = fleet_msgs__msg__TaskAnnouncement__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
fleet_msgs__msg__TaskAnnouncement__destroy(fleet_msgs__msg__TaskAnnouncement * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    fleet_msgs__msg__TaskAnnouncement__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
fleet_msgs__msg__TaskAnnouncement__Sequence__init(fleet_msgs__msg__TaskAnnouncement__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fleet_msgs__msg__TaskAnnouncement * data = NULL;

  if (size) {
    if (size > SIZE_MAX / sizeof(fleet_msgs__msg__TaskAnnouncement)) {
      return false;
    }
    data = (fleet_msgs__msg__TaskAnnouncement *)allocator.zero_allocate(size, sizeof(fleet_msgs__msg__TaskAnnouncement), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = fleet_msgs__msg__TaskAnnouncement__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        fleet_msgs__msg__TaskAnnouncement__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
fleet_msgs__msg__TaskAnnouncement__Sequence__fini(fleet_msgs__msg__TaskAnnouncement__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      fleet_msgs__msg__TaskAnnouncement__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

fleet_msgs__msg__TaskAnnouncement__Sequence *
fleet_msgs__msg__TaskAnnouncement__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fleet_msgs__msg__TaskAnnouncement__Sequence * array = (fleet_msgs__msg__TaskAnnouncement__Sequence *)allocator.allocate(sizeof(fleet_msgs__msg__TaskAnnouncement__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = fleet_msgs__msg__TaskAnnouncement__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
fleet_msgs__msg__TaskAnnouncement__Sequence__destroy(fleet_msgs__msg__TaskAnnouncement__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    fleet_msgs__msg__TaskAnnouncement__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
fleet_msgs__msg__TaskAnnouncement__Sequence__are_equal(const fleet_msgs__msg__TaskAnnouncement__Sequence * lhs, const fleet_msgs__msg__TaskAnnouncement__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!fleet_msgs__msg__TaskAnnouncement__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
fleet_msgs__msg__TaskAnnouncement__Sequence__copy(
  const fleet_msgs__msg__TaskAnnouncement__Sequence * input,
  fleet_msgs__msg__TaskAnnouncement__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    if (input->size > SIZE_MAX / sizeof(fleet_msgs__msg__TaskAnnouncement)) {
      return false;
    }
    const size_t allocation_size =
      input->size * sizeof(fleet_msgs__msg__TaskAnnouncement);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    fleet_msgs__msg__TaskAnnouncement * data =
      (fleet_msgs__msg__TaskAnnouncement *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!fleet_msgs__msg__TaskAnnouncement__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          fleet_msgs__msg__TaskAnnouncement__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!fleet_msgs__msg__TaskAnnouncement__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
