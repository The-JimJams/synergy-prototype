// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from fleet_msgs:msg/ResourceClaim.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fleet_msgs/msg/resource_claim.hpp"


#ifndef FLEET_MSGS__MSG__DETAIL__RESOURCE_CLAIM__STRUCT_HPP_
#define FLEET_MSGS__MSG__DETAIL__RESOURCE_CLAIM__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_buffer/buffer.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__fleet_msgs__msg__ResourceClaim __attribute__((deprecated))
#else
# define DEPRECATED__fleet_msgs__msg__ResourceClaim __declspec(deprecated)
#endif

namespace fleet_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct ResourceClaim_
{
  using Type = ResourceClaim_<ContainerAllocator>;

  explicit ResourceClaim_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->robot_id = "";
      this->resource = "";
      this->start_time = 0.0;
      this->end_time = 0.0;
      this->priority = 0l;
      this->claim_id = "";
      this->status = "";
    }
  }

  explicit ResourceClaim_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : robot_id(_alloc),
    resource(_alloc),
    claim_id(_alloc),
    status(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->robot_id = "";
      this->resource = "";
      this->start_time = 0.0;
      this->end_time = 0.0;
      this->priority = 0l;
      this->claim_id = "";
      this->status = "";
    }
  }

  // field types and members
  using _robot_id_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _robot_id_type robot_id;
  using _resource_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _resource_type resource;
  using _start_time_type =
    double;
  _start_time_type start_time;
  using _end_time_type =
    double;
  _end_time_type end_time;
  using _priority_type =
    int32_t;
  _priority_type priority;
  using _claim_id_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _claim_id_type claim_id;
  using _status_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _status_type status;

  // setters for named parameter idiom
  Type & set__robot_id(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->robot_id = _arg;
    return *this;
  }
  Type & set__resource(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->resource = _arg;
    return *this;
  }
  Type & set__start_time(
    const double & _arg)
  {
    this->start_time = _arg;
    return *this;
  }
  Type & set__end_time(
    const double & _arg)
  {
    this->end_time = _arg;
    return *this;
  }
  Type & set__priority(
    const int32_t & _arg)
  {
    this->priority = _arg;
    return *this;
  }
  Type & set__claim_id(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->claim_id = _arg;
    return *this;
  }
  Type & set__status(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->status = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    fleet_msgs::msg::ResourceClaim_<ContainerAllocator> *;
  using ConstRawPtr =
    const fleet_msgs::msg::ResourceClaim_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<fleet_msgs::msg::ResourceClaim_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<fleet_msgs::msg::ResourceClaim_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      fleet_msgs::msg::ResourceClaim_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<fleet_msgs::msg::ResourceClaim_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      fleet_msgs::msg::ResourceClaim_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<fleet_msgs::msg::ResourceClaim_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<fleet_msgs::msg::ResourceClaim_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<fleet_msgs::msg::ResourceClaim_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__fleet_msgs__msg__ResourceClaim
    std::shared_ptr<fleet_msgs::msg::ResourceClaim_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__fleet_msgs__msg__ResourceClaim
    std::shared_ptr<fleet_msgs::msg::ResourceClaim_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ResourceClaim_ & other) const
  {
    if (this->robot_id != other.robot_id) {
      return false;
    }
    if (this->resource != other.resource) {
      return false;
    }
    if (this->start_time != other.start_time) {
      return false;
    }
    if (this->end_time != other.end_time) {
      return false;
    }
    if (this->priority != other.priority) {
      return false;
    }
    if (this->claim_id != other.claim_id) {
      return false;
    }
    if (this->status != other.status) {
      return false;
    }
    return true;
  }
  bool operator!=(const ResourceClaim_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ResourceClaim_

// alias to use template instance with default allocator
using ResourceClaim =
  fleet_msgs::msg::ResourceClaim_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace fleet_msgs

#endif  // FLEET_MSGS__MSG__DETAIL__RESOURCE_CLAIM__STRUCT_HPP_
