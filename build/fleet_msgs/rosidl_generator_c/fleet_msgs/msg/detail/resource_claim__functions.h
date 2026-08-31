// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from fleet_msgs:msg/ResourceClaim.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fleet_msgs/msg/resource_claim.h"


#ifndef FLEET_MSGS__MSG__DETAIL__RESOURCE_CLAIM__FUNCTIONS_H_
#define FLEET_MSGS__MSG__DETAIL__RESOURCE_CLAIM__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/action_type_support_struct.h"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_runtime_c/service_type_support_struct.h"
#include "rosidl_runtime_c/type_description/type_description__struct.h"
#include "rosidl_runtime_c/type_description/type_source__struct.h"
#include "rosidl_runtime_c/type_hash.h"
#include "rosidl_runtime_c/visibility_control.h"
#include "fleet_msgs/msg/rosidl_generator_c__visibility_control.h"

#include "fleet_msgs/msg/detail/resource_claim__struct.h"

/// Initialize msg/ResourceClaim message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * fleet_msgs__msg__ResourceClaim
 * )) before or use
 * fleet_msgs__msg__ResourceClaim__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_fleet_msgs
bool
fleet_msgs__msg__ResourceClaim__init(fleet_msgs__msg__ResourceClaim * msg);

/// Finalize msg/ResourceClaim message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_fleet_msgs
void
fleet_msgs__msg__ResourceClaim__fini(fleet_msgs__msg__ResourceClaim * msg);

/// Create msg/ResourceClaim message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * fleet_msgs__msg__ResourceClaim__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_fleet_msgs
fleet_msgs__msg__ResourceClaim *
fleet_msgs__msg__ResourceClaim__create(void);

/// Destroy msg/ResourceClaim message.
/**
 * It calls
 * fleet_msgs__msg__ResourceClaim__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_fleet_msgs
void
fleet_msgs__msg__ResourceClaim__destroy(fleet_msgs__msg__ResourceClaim * msg);

/// Check for msg/ResourceClaim message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_fleet_msgs
bool
fleet_msgs__msg__ResourceClaim__are_equal(const fleet_msgs__msg__ResourceClaim * lhs, const fleet_msgs__msg__ResourceClaim * rhs);

/// Copy a msg/ResourceClaim message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_fleet_msgs
bool
fleet_msgs__msg__ResourceClaim__copy(
  const fleet_msgs__msg__ResourceClaim * input,
  fleet_msgs__msg__ResourceClaim * output);

/// Retrieve pointer to the hash of the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_fleet_msgs
const rosidl_type_hash_t *
fleet_msgs__msg__ResourceClaim__get_type_hash(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_fleet_msgs
const rosidl_runtime_c__type_description__TypeDescription *
fleet_msgs__msg__ResourceClaim__get_type_description(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the single raw source text that defined this type.
ROSIDL_GENERATOR_C_PUBLIC_fleet_msgs
const rosidl_runtime_c__type_description__TypeSource *
fleet_msgs__msg__ResourceClaim__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the recursive raw sources that defined the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_fleet_msgs
const rosidl_runtime_c__type_description__TypeSource__Sequence *
fleet_msgs__msg__ResourceClaim__get_type_description_sources(
  const rosidl_message_type_support_t * type_support);

/// Initialize array of msg/ResourceClaim messages.
/**
 * It allocates the memory for the number of elements and calls
 * fleet_msgs__msg__ResourceClaim__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_fleet_msgs
bool
fleet_msgs__msg__ResourceClaim__Sequence__init(fleet_msgs__msg__ResourceClaim__Sequence * array, size_t size);

/// Finalize array of msg/ResourceClaim messages.
/**
 * It calls
 * fleet_msgs__msg__ResourceClaim__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_fleet_msgs
void
fleet_msgs__msg__ResourceClaim__Sequence__fini(fleet_msgs__msg__ResourceClaim__Sequence * array);

/// Create array of msg/ResourceClaim messages.
/**
 * It allocates the memory for the array and calls
 * fleet_msgs__msg__ResourceClaim__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_fleet_msgs
fleet_msgs__msg__ResourceClaim__Sequence *
fleet_msgs__msg__ResourceClaim__Sequence__create(size_t size);

/// Destroy array of msg/ResourceClaim messages.
/**
 * It calls
 * fleet_msgs__msg__ResourceClaim__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_fleet_msgs
void
fleet_msgs__msg__ResourceClaim__Sequence__destroy(fleet_msgs__msg__ResourceClaim__Sequence * array);

/// Check for msg/ResourceClaim message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_fleet_msgs
bool
fleet_msgs__msg__ResourceClaim__Sequence__are_equal(const fleet_msgs__msg__ResourceClaim__Sequence * lhs, const fleet_msgs__msg__ResourceClaim__Sequence * rhs);

/// Copy an array of msg/ResourceClaim messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_fleet_msgs
bool
fleet_msgs__msg__ResourceClaim__Sequence__copy(
  const fleet_msgs__msg__ResourceClaim__Sequence * input,
  fleet_msgs__msg__ResourceClaim__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // FLEET_MSGS__MSG__DETAIL__RESOURCE_CLAIM__FUNCTIONS_H_
