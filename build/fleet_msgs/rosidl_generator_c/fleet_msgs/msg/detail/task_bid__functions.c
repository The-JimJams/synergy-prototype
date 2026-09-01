// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from fleet_msgs:msg/TaskBid.idl
// generated code does not contain a copyright notice
#include "fleet_msgs/msg/detail/task_bid__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `robot_id`
// Member `task_id`
#include "rosidl_runtime_c/string_functions.h"

bool
fleet_msgs__msg__TaskBid__init(fleet_msgs__msg__TaskBid * msg)
{
  if (!msg) {
    return false;
  }
  // robot_id
  if (!rosidl_runtime_c__String__init(&msg->robot_id)) {
    fleet_msgs__msg__TaskBid__fini(msg);
    return false;
  }
  // task_id
  if (!rosidl_runtime_c__String__init(&msg->task_id)) {
    fleet_msgs__msg__TaskBid__fini(msg);
    return false;
  }
  // estimated_time
  // distance
  // battery_cost
  // confidence
  return true;
}

void
fleet_msgs__msg__TaskBid__fini(fleet_msgs__msg__TaskBid * msg)
{
  if (!msg) {
    return;
  }
  // robot_id
  rosidl_runtime_c__String__fini(&msg->robot_id);
  // task_id
  rosidl_runtime_c__String__fini(&msg->task_id);
  // estimated_time
  // distance
  // battery_cost
  // confidence
}

bool
fleet_msgs__msg__TaskBid__are_equal(const fleet_msgs__msg__TaskBid * lhs, const fleet_msgs__msg__TaskBid * rhs)
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
  // task_id
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->task_id), &(rhs->task_id)))
  {
    return false;
  }
  // estimated_time
  if (lhs->estimated_time != rhs->estimated_time) {
    return false;
  }
  // distance
  if (lhs->distance != rhs->distance) {
    return false;
  }
  // battery_cost
  if (lhs->battery_cost != rhs->battery_cost) {
    return false;
  }
  // confidence
  if (lhs->confidence != rhs->confidence) {
    return false;
  }
  return true;
}

bool
fleet_msgs__msg__TaskBid__copy(
  const fleet_msgs__msg__TaskBid * input,
  fleet_msgs__msg__TaskBid * output)
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
  // task_id
  if (!rosidl_runtime_c__String__copy(
      &(input->task_id), &(output->task_id)))
  {
    return false;
  }
  // estimated_time
  output->estimated_time = input->estimated_time;
  // distance
  output->distance = input->distance;
  // battery_cost
  output->battery_cost = input->battery_cost;
  // confidence
  output->confidence = input->confidence;
  return true;
}

fleet_msgs__msg__TaskBid *
fleet_msgs__msg__TaskBid__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fleet_msgs__msg__TaskBid * msg = (fleet_msgs__msg__TaskBid *)allocator.allocate(sizeof(fleet_msgs__msg__TaskBid), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(fleet_msgs__msg__TaskBid));
  bool success = fleet_msgs__msg__TaskBid__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
fleet_msgs__msg__TaskBid__destroy(fleet_msgs__msg__TaskBid * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    fleet_msgs__msg__TaskBid__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
fleet_msgs__msg__TaskBid__Sequence__init(fleet_msgs__msg__TaskBid__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fleet_msgs__msg__TaskBid * data = NULL;

  if (size) {
    if (size > SIZE_MAX / sizeof(fleet_msgs__msg__TaskBid)) {
      return false;
    }
    data = (fleet_msgs__msg__TaskBid *)allocator.zero_allocate(size, sizeof(fleet_msgs__msg__TaskBid), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = fleet_msgs__msg__TaskBid__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        fleet_msgs__msg__TaskBid__fini(&data[i - 1]);
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
fleet_msgs__msg__TaskBid__Sequence__fini(fleet_msgs__msg__TaskBid__Sequence * array)
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
      fleet_msgs__msg__TaskBid__fini(&array->data[i]);
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

fleet_msgs__msg__TaskBid__Sequence *
fleet_msgs__msg__TaskBid__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fleet_msgs__msg__TaskBid__Sequence * array = (fleet_msgs__msg__TaskBid__Sequence *)allocator.allocate(sizeof(fleet_msgs__msg__TaskBid__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = fleet_msgs__msg__TaskBid__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
fleet_msgs__msg__TaskBid__Sequence__destroy(fleet_msgs__msg__TaskBid__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    fleet_msgs__msg__TaskBid__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
fleet_msgs__msg__TaskBid__Sequence__are_equal(const fleet_msgs__msg__TaskBid__Sequence * lhs, const fleet_msgs__msg__TaskBid__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!fleet_msgs__msg__TaskBid__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
fleet_msgs__msg__TaskBid__Sequence__copy(
  const fleet_msgs__msg__TaskBid__Sequence * input,
  fleet_msgs__msg__TaskBid__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    if (input->size > SIZE_MAX / sizeof(fleet_msgs__msg__TaskBid)) {
      return false;
    }
    const size_t allocation_size =
      input->size * sizeof(fleet_msgs__msg__TaskBid);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    fleet_msgs__msg__TaskBid * data =
      (fleet_msgs__msg__TaskBid *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!fleet_msgs__msg__TaskBid__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          fleet_msgs__msg__TaskBid__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!fleet_msgs__msg__TaskBid__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
