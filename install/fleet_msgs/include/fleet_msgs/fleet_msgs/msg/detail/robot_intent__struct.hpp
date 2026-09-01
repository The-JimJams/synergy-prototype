// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from fleet_msgs:msg/RobotIntent.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fleet_msgs/msg/robot_intent.hpp"


#ifndef FLEET_MSGS__MSG__DETAIL__ROBOT_INTENT__STRUCT_HPP_
#define FLEET_MSGS__MSG__DETAIL__ROBOT_INTENT__STRUCT_HPP_

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
# define DEPRECATED__fleet_msgs__msg__RobotIntent __attribute__((deprecated))
#else
# define DEPRECATED__fleet_msgs__msg__RobotIntent __declspec(deprecated)
#endif

namespace fleet_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct RobotIntent_
{
  using Type = RobotIntent_<ContainerAllocator>;

  explicit RobotIntent_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->robot_id = "";
      this->target_intersection = "";
      this->eta = 0.0;
      this->priority = 0l;
      this->task_id = "";
    }
  }

  explicit RobotIntent_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : robot_id(_alloc),
    target_intersection(_alloc),
    task_id(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->robot_id = "";
      this->target_intersection = "";
      this->eta = 0.0;
      this->priority = 0l;
      this->task_id = "";
    }
  }

  // field types and members
  using _robot_id_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _robot_id_type robot_id;
  using _planned_path_type =
    std::vector<std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>>>;
  _planned_path_type planned_path;
  using _target_intersection_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _target_intersection_type target_intersection;
  using _eta_type =
    double;
  _eta_type eta;
  using _priority_type =
    int32_t;
  _priority_type priority;
  using _task_id_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _task_id_type task_id;

  // setters for named parameter idiom
  Type & set__robot_id(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->robot_id = _arg;
    return *this;
  }
  Type & set__planned_path(
    const std::vector<std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>>> & _arg)
  {
    this->planned_path = _arg;
    return *this;
  }
  Type & set__target_intersection(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->target_intersection = _arg;
    return *this;
  }
  Type & set__eta(
    const double & _arg)
  {
    this->eta = _arg;
    return *this;
  }
  Type & set__priority(
    const int32_t & _arg)
  {
    this->priority = _arg;
    return *this;
  }
  Type & set__task_id(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->task_id = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    fleet_msgs::msg::RobotIntent_<ContainerAllocator> *;
  using ConstRawPtr =
    const fleet_msgs::msg::RobotIntent_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<fleet_msgs::msg::RobotIntent_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<fleet_msgs::msg::RobotIntent_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      fleet_msgs::msg::RobotIntent_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<fleet_msgs::msg::RobotIntent_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      fleet_msgs::msg::RobotIntent_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<fleet_msgs::msg::RobotIntent_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<fleet_msgs::msg::RobotIntent_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<fleet_msgs::msg::RobotIntent_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__fleet_msgs__msg__RobotIntent
    std::shared_ptr<fleet_msgs::msg::RobotIntent_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__fleet_msgs__msg__RobotIntent
    std::shared_ptr<fleet_msgs::msg::RobotIntent_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const RobotIntent_ & other) const
  {
    if (this->robot_id != other.robot_id) {
      return false;
    }
    if (this->planned_path != other.planned_path) {
      return false;
    }
    if (this->target_intersection != other.target_intersection) {
      return false;
    }
    if (this->eta != other.eta) {
      return false;
    }
    if (this->priority != other.priority) {
      return false;
    }
    if (this->task_id != other.task_id) {
      return false;
    }
    return true;
  }
  bool operator!=(const RobotIntent_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct RobotIntent_

// alias to use template instance with default allocator
using RobotIntent =
  fleet_msgs::msg::RobotIntent_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace fleet_msgs

#endif  // FLEET_MSGS__MSG__DETAIL__ROBOT_INTENT__STRUCT_HPP_
