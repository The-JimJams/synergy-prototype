// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from fleet_msgs:msg/ResourceClaim.idl
// generated code does not contain a copyright notice
#include "fleet_msgs/msg/detail/resource_claim__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `robot_id`
// Member `resource`
// Member `claim_id`
// Member `status`
#include "rosidl_runtime_c/string_functions.h"

bool
fleet_msgs__msg__ResourceClaim__init(fleet_msgs__msg__ResourceClaim * msg)
{
  if (!msg) {
    return false;
  }
  // robot_id
  if (!rosidl_runtime_c__String__init(&msg->robot_id)) {
    fleet_msgs__msg__ResourceClaim__fini(msg);
    return false;
  }
  // resource
  if (!rosidl_runtime_c__String__init(&msg->resource)) {
    fleet_msgs__msg__ResourceClaim__fini(msg);
    return false;
  }
  // start_time
  // end_time
  // priority
  // claim_id
  if (!rosidl_runtime_c__String__init(&msg->claim_id)) {
    fleet_msgs__msg__ResourceClaim__fini(msg);
    return false;
  }
  // status
  if (!rosidl_runtime_c__String__init(&msg->status)) {
    fleet_msgs__msg__ResourceClaim__fini(msg);
    return false;
  }
  return true;
}

void
fleet_msgs__msg__ResourceClaim__fini(fleet_msgs__msg__ResourceClaim * msg)
{
  if (!msg) {
    return;
  }
  // robot_id
  rosidl_runtime_c__String__fini(&msg->robot_id);
  // resource
  rosidl_runtime_c__String__fini(&msg->resource);
  // start_time
  // end_time
  // priority
  // claim_id
  rosidl_runtime_c__String__fini(&msg->claim_id);
  // status
  rosidl_runtime_c__String__fini(&msg->status);
}

bool
fleet_msgs__msg__ResourceClaim__are_equal(const fleet_msgs__msg__ResourceClaim * lhs, const fleet_msgs__msg__ResourceClaim * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // robot_id
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->robot_id), &(rhs->robot_id)))
  {
    return false;
  }
  // resource
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->resource), &(rhs->resource)))
  {
    return false;
  }
  // start_time
  if (lhs->start_time != rhs->start_time) {
    return false;
  }
  // end_time
  if (lhs->end_time != rhs->end_time) {
    return false;
  }
  // priority
  if (lhs->priority != rhs->priority) {
    return false;
  }
  // claim_id
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->claim_id), &(rhs->claim_id)))
  {
    return false;
  }
  // status
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->status), &(rhs->status)))
  {
    return false;
  }
  return true;
}

bool
fleet_msgs__msg__ResourceClaim__copy(
  const fleet_msgs__msg__ResourceClaim * input,
  fleet_msgs__msg__ResourceClaim * output)
{
  if (!input || !output) {
    return false;
  }
  // robot_id
  if (!rosidl_runtime_c__String__copy(
      &(input->robot_id), &(output->robot_id)))
  {
    return false;
  }
  // resource
  if (!rosidl_runtime_c__String__copy(
      &(input->resource), &(output->resource)))
  {
    return false;
  }
  // start_time
  output->start_time = input->start_time;
  // end_time
  output->end_time = input->end_time;
  // priority
  output->priority = input->priority;
  // claim_id
  if (!rosidl_runtime_c__String__copy(
      &(input->claim_id), &(output->claim_id)))
  {
    return false;
  }
  // status
  if (!rosidl_runtime_c__String__copy(
      &(input->status), &(output->status)))
  {
    return false;
  }
  return true;
}

fleet_msgs__msg__ResourceClaim *
fleet_msgs__msg__ResourceClaim__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fleet_msgs__msg__ResourceClaim * msg = (fleet_msgs__msg__ResourceClaim *)allocator.allocate(sizeof(fleet_msgs__msg__ResourceClaim), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(fleet_msgs__msg__ResourceClaim));
  bool success = fleet_msgs__msg__ResourceClaim__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
fleet_msgs__msg__ResourceClaim__destroy(fleet_msgs__msg__ResourceClaim * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    fleet_msgs__msg__ResourceClaim__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
fleet_msgs__msg__ResourceClaim__Sequence__init(fleet_msgs__msg__ResourceClaim__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fleet_msgs__msg__ResourceClaim * data = NULL;

  if (size) {
    if (size > SIZE_MAX / sizeof(fleet_msgs__msg__ResourceClaim)) {
      return false;
    }
    data = (fleet_msgs__msg__ResourceClaim *)allocator.zero_allocate(size, sizeof(fleet_msgs__msg__ResourceClaim), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = fleet_msgs__msg__ResourceClaim__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        fleet_msgs__msg__ResourceClaim__fini(&data[i - 1]);
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
fleet_msgs__msg__ResourceClaim__Sequence__fini(fleet_msgs__msg__ResourceClaim__Sequence * array)
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
      fleet_msgs__msg__ResourceClaim__fini(&array->data[i]);
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

fleet_msgs__msg__ResourceClaim__Sequence *
fleet_msgs__msg__ResourceClaim__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fleet_msgs__msg__ResourceClaim__Sequence * array = (fleet_msgs__msg__ResourceClaim__Sequence *)allocator.allocate(sizeof(fleet_msgs__msg__ResourceClaim__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = fleet_msgs__msg__ResourceClaim__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
fleet_msgs__msg__ResourceClaim__Sequence__destroy(fleet_msgs__msg__ResourceClaim__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    fleet_msgs__msg__ResourceClaim__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
fleet_msgs__msg__ResourceClaim__Sequence__are_equal(const fleet_msgs__msg__ResourceClaim__Sequence * lhs, const fleet_msgs__msg__ResourceClaim__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!fleet_msgs__msg__ResourceClaim__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
fleet_msgs__msg__ResourceClaim__Sequence__copy(
  const fleet_msgs__msg__ResourceClaim__Sequence * input,
  fleet_msgs__msg__ResourceClaim__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    if (input->size > SIZE_MAX / sizeof(fleet_msgs__msg__ResourceClaim)) {
      return false;
    }
    const size_t allocation_size =
      input->size * sizeof(fleet_msgs__msg__ResourceClaim);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    fleet_msgs__msg__ResourceClaim * data =
      (fleet_msgs__msg__ResourceClaim *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!fleet_msgs__msg__ResourceClaim__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          fleet_msgs__msg__ResourceClaim__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!fleet_msgs__msg__ResourceClaim__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
