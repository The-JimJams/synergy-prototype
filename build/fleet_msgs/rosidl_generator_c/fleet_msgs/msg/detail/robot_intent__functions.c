// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from fleet_msgs:msg/RobotIntent.idl
// generated code does not contain a copyright notice
#include "fleet_msgs/msg/detail/robot_intent__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `robot_id`
// Member `planned_path`
// Member `target_intersection`
// Member `task_id`
#include "rosidl_runtime_c/string_functions.h"

bool
fleet_msgs__msg__RobotIntent__init(fleet_msgs__msg__RobotIntent * msg)
{
  if (!msg) {
    return false;
  }
  // robot_id
  if (!rosidl_runtime_c__String__init(&msg->robot_id)) {
    fleet_msgs__msg__RobotIntent__fini(msg);
    return false;
  }
  // planned_path
  if (!rosidl_runtime_c__String__Sequence__init(&msg->planned_path, 0)) {
    fleet_msgs__msg__RobotIntent__fini(msg);
    return false;
  }
  // target_intersection
  if (!rosidl_runtime_c__String__init(&msg->target_intersection)) {
    fleet_msgs__msg__RobotIntent__fini(msg);
    return false;
  }
  // eta
  // priority
  // task_id
  if (!rosidl_runtime_c__String__init(&msg->task_id)) {
    fleet_msgs__msg__RobotIntent__fini(msg);
    return false;
  }
  return true;
}

void
fleet_msgs__msg__RobotIntent__fini(fleet_msgs__msg__RobotIntent * msg)
{
  if (!msg) {
    return;
  }
  // robot_id
  rosidl_runtime_c__String__fini(&msg->robot_id);
  // planned_path
  rosidl_runtime_c__String__Sequence__fini(&msg->planned_path);
  // target_intersection
  rosidl_runtime_c__String__fini(&msg->target_intersection);
  // eta
  // priority
  // task_id
  rosidl_runtime_c__String__fini(&msg->task_id);
}

bool
fleet_msgs__msg__RobotIntent__are_equal(const fleet_msgs__msg__RobotIntent * lhs, const fleet_msgs__msg__RobotIntent * rhs)
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
  // planned_path
  if (!rosidl_runtime_c__String__Sequence__are_equal(
      &(lhs->planned_path), &(rhs->planned_path)))
  {
    return false;
  }
  // target_intersection
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->target_intersection), &(rhs->target_intersection)))
  {
    return false;
  }
  // eta
  if (lhs->eta != rhs->eta) {
    return false;
  }
  // priority
  if (lhs->priority != rhs->priority) {
    return false;
  }
  // task_id
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->task_id), &(rhs->task_id)))
  {
    return false;
  }
  return true;
}

bool
fleet_msgs__msg__RobotIntent__copy(
  const fleet_msgs__msg__RobotIntent * input,
  fleet_msgs__msg__RobotIntent * output)
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
  // planned_path
  if (!rosidl_runtime_c__String__Sequence__copy(
      &(input->planned_path), &(output->planned_path)))
  {
    return false;
  }
  // target_intersection
  if (!rosidl_runtime_c__String__copy(
      &(input->target_intersection), &(output->target_intersection)))
  {
    return false;
  }
  // eta
  output->eta = input->eta;
  // priority
  output->priority = input->priority;
  // task_id
  if (!rosidl_runtime_c__String__copy(
      &(input->task_id), &(output->task_id)))
  {
    return false;
  }
  return true;
}

fleet_msgs__msg__RobotIntent *
fleet_msgs__msg__RobotIntent__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fleet_msgs__msg__RobotIntent * msg = (fleet_msgs__msg__RobotIntent *)allocator.allocate(sizeof(fleet_msgs__msg__RobotIntent), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(fleet_msgs__msg__RobotIntent));
  bool success = fleet_msgs__msg__RobotIntent__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
fleet_msgs__msg__RobotIntent__destroy(fleet_msgs__msg__RobotIntent * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    fleet_msgs__msg__RobotIntent__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
fleet_msgs__msg__RobotIntent__Sequence__init(fleet_msgs__msg__RobotIntent__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fleet_msgs__msg__RobotIntent * data = NULL;

  if (size) {
    if (size > SIZE_MAX / sizeof(fleet_msgs__msg__RobotIntent)) {
      return false;
    }
    data = (fleet_msgs__msg__RobotIntent *)allocator.zero_allocate(size, sizeof(fleet_msgs__msg__RobotIntent), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = fleet_msgs__msg__RobotIntent__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        fleet_msgs__msg__RobotIntent__fini(&data[i - 1]);
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
fleet_msgs__msg__RobotIntent__Sequence__fini(fleet_msgs__msg__RobotIntent__Sequence * array)
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
      fleet_msgs__msg__RobotIntent__fini(&array->data[i]);
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

fleet_msgs__msg__RobotIntent__Sequence *
fleet_msgs__msg__RobotIntent__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  fleet_msgs__msg__RobotIntent__Sequence * array = (fleet_msgs__msg__RobotIntent__Sequence *)allocator.allocate(sizeof(fleet_msgs__msg__RobotIntent__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = fleet_msgs__msg__RobotIntent__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
fleet_msgs__msg__RobotIntent__Sequence__destroy(fleet_msgs__msg__RobotIntent__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    fleet_msgs__msg__RobotIntent__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
fleet_msgs__msg__RobotIntent__Sequence__are_equal(const fleet_msgs__msg__RobotIntent__Sequence * lhs, const fleet_msgs__msg__RobotIntent__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!fleet_msgs__msg__RobotIntent__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
fleet_msgs__msg__RobotIntent__Sequence__copy(
  const fleet_msgs__msg__RobotIntent__Sequence * input,
  fleet_msgs__msg__RobotIntent__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    if (input->size > SIZE_MAX / sizeof(fleet_msgs__msg__RobotIntent)) {
      return false;
    }
    const size_t allocation_size =
      input->size * sizeof(fleet_msgs__msg__RobotIntent);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    fleet_msgs__msg__RobotIntent * data =
      (fleet_msgs__msg__RobotIntent *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!fleet_msgs__msg__RobotIntent__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          fleet_msgs__msg__RobotIntent__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!fleet_msgs__msg__RobotIntent__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
