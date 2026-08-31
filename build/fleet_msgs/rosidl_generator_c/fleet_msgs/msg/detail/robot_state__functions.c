// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from fleet_msgs:msg/RobotState.idl
// generated code does not contain a copyright notice
#include "fleet_msgs/msg/detail/robot_state__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `robot_id`
// Member `current_task`
// Member `status`
#include "rosidl_runtime_c/string_functions.h"

bool
fleet_msgs__msg__RobotState__init(fleet_msgs__msg__RobotState * msg)
{
  if (!msg) {
    return false;
  }
  // robot_id
  if (!rosidl_runtime_c__String__init(&msg->robot_id)) {
    fleet_msgs__msg__RobotState__fini(msg);
    return false;
  }
  // timestamp
  // position
  // velocity
  // battery
  // current_task
  if (!rosidl_runtime_c__String__init(&msg->current_task)) {
    fleet_msgs__msg__RobotState__fini(msg);
    return false;
  }
  // status
  if (!rosidl_runtime_c__String__init(&msg->status)) {
    fleet_msgs__msg__RobotState__fini(msg);
    return false;
  }
  return true;
}

void
fleet_msgs__msg__RobotState__fini(fleet_msgs__msg__RobotState * msg)
{
  if (!msg) {
    return;
  }
  // robot_id
  rosidl_runtime_c__String__fini(&msg->robot_id);
  // timestamp
  // position
  // velocity
  // battery
  // current_task
  rosidl_runtime_c__String__fini(&msg->current_task);
  // status
  rosidl_runtime_c__String__fini(&msg->status);
}

bool
fleet_msgs__msg__RobotState__are_equal(const fleet_msgs__msg__RobotState * lhs, const fleet_msgs__msg__RobotState * rhs)
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
  // timestamp
  if (lhs->timestamp != rhs->timestamp) {
    return false;
  }
  // position
  for (size_t i = 0; i < 2; ++i) {
    if (lhs->position[i] != rhs->position[i]) {
      return false;
    }
  }
  // velocity
  if (lhs->velocity != rhs->velocity) {
    return false;
  }
  // battery
  if (lhs->battery != rhs->battery) {
    return false;
  }
  // current_task
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->current_task), &(rhs->current_task)))
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
fleet_msgs__msg__RobotState__copy(
  const fleet_msgs__msg__RobotState * input,
  fleet_msgs__msg__RobotState * output)
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
  // timestamp
  output->timestamp = input->timestamp;
  // position
  for (size_t i = 0; i < 2; ++i) {
    output->position[i] = input->position[i];
  }
  // velocity
  output->velocity = input->velocity;
  // battery
  output->battery = input->battery;
  // current_task
  if (!rosidl_runtime_c__String__copy(
      &(input->current_task), &(output->current_task)))
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

fleet_msgs__msg__RobotState *
fleet_msgs__msg__RobotState__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fleet_msgs__msg__RobotState * msg = (fleet_msgs__msg__RobotState *)allocator.allocate(sizeof(fleet_msgs__msg__RobotState), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(fleet_msgs__msg__RobotState));
  bool success = fleet_msgs__msg__RobotState__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
fleet_msgs__msg__RobotState__destroy(fleet_msgs__msg__RobotState * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    fleet_msgs__msg__RobotState__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
fleet_msgs__msg__RobotState__Sequence__init(fleet_msgs__msg__RobotState__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fleet_msgs__msg__RobotState * data = NULL;

  if (size) {
    if (size > SIZE_MAX / sizeof(fleet_msgs__msg__RobotState)) {
      return false;
    }
    data = (fleet_msgs__msg__RobotState *)allocator.zero_allocate(size, sizeof(fleet_msgs__msg__RobotState), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = fleet_msgs__msg__RobotState__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        fleet_msgs__msg__RobotState__fini(&data[i - 1]);
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
fleet_msgs__msg__RobotState__Sequence__fini(fleet_msgs__msg__RobotState__Sequence * array)
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
      fleet_msgs__msg__RobotState__fini(&array->data[i]);
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

fleet_msgs__msg__RobotState__Sequence *
fleet_msgs__msg__RobotState__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fleet_msgs__msg__RobotState__Sequence * array = (fleet_msgs__msg__RobotState__Sequence *)allocator.allocate(sizeof(fleet_msgs__msg__RobotState__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = fleet_msgs__msg__RobotState__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
fleet_msgs__msg__RobotState__Sequence__destroy(fleet_msgs__msg__RobotState__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    fleet_msgs__msg__RobotState__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
fleet_msgs__msg__RobotState__Sequence__are_equal(const fleet_msgs__msg__RobotState__Sequence * lhs, const fleet_msgs__msg__RobotState__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!fleet_msgs__msg__RobotState__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
fleet_msgs__msg__RobotState__Sequence__copy(
  const fleet_msgs__msg__RobotState__Sequence * input,
  fleet_msgs__msg__RobotState__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    if (input->size > SIZE_MAX / sizeof(fleet_msgs__msg__RobotState)) {
      return false;
    }
    const size_t allocation_size =
      input->size * sizeof(fleet_msgs__msg__RobotState);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    fleet_msgs__msg__RobotState * data =
      (fleet_msgs__msg__RobotState *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!fleet_msgs__msg__RobotState__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          fleet_msgs__msg__RobotState__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!fleet_msgs__msg__RobotState__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
