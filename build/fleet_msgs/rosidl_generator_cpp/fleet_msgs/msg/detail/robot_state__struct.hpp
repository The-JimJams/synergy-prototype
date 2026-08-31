// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from fleet_msgs:msg/RobotState.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fleet_msgs/msg/robot_state.hpp"


#ifndef FLEET_MSGS__MSG__DETAIL__ROBOT_STATE__STRUCT_HPP_
#define FLEET_MSGS__MSG__DETAIL__ROBOT_STATE__STRUCT_HPP_

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
# define DEPRECATED__fleet_msgs__msg__RobotState __attribute__((deprecated))
#else
# define DEPRECATED__fleet_msgs__msg__RobotState __declspec(deprecated)
#endif

namespace fleet_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct RobotState_
{
  using Type = RobotState_<ContainerAllocator>;

  explicit RobotState_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->robot_id = "";
      this->timestamp = 0.0;
      std::fill(this->position.begin(), this->position.end(), 0.0);
      this->velocity = 0.0;
      this->battery = 0.0;
      this->current_task = "";
      this->status = "";
    }
  }

  explicit RobotState_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : robot_id(_alloc),
    position(_alloc),
    current_task(_alloc),
    status(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->robot_id = "";
      this->timestamp = 0.0;
      std::fill(this->position.begin(), this->position.end(), 0.0);
      this->velocity = 0.0;
      this->battery = 0.0;
      this->current_task = "";
      this->status = "";
    }
  }

  // field types and members
  using _robot_id_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _robot_id_type robot_id;
  using _timestamp_type =
    double;
  _timestamp_type timestamp;
  using _position_type =
    std::array<double, 2>;
  _position_type position;
  using _velocity_type =
    double;
  _velocity_type velocity;
  using _battery_type =
    double;
  _battery_type battery;
  using _current_task_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _current_task_type current_task;
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
  Type & set__timestamp(
    const double & _arg)
  {
    this->timestamp = _arg;
    return *this;
  }
  Type & set__position(
    const std::array<double, 2> & _arg)
  {
    this->position = _arg;
    return *this;
  }
  Type & set__velocity(
    const double & _arg)
  {
    this->velocity = _arg;
    return *this;
  }
  Type & set__battery(
    const double & _arg)
  {
    this->battery = _arg;
    return *this;
  }
  Type & set__current_task(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->current_task = _arg;
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
    fleet_msgs::msg::RobotState_<ContainerAllocator> *;
  using ConstRawPtr =
    const fleet_msgs::msg::RobotState_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<fleet_msgs::msg::RobotState_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<fleet_msgs::msg::RobotState_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      fleet_msgs::msg::RobotState_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<fleet_msgs::msg::RobotState_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      fleet_msgs::msg::RobotState_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<fleet_msgs::msg::RobotState_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<fleet_msgs::msg::RobotState_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<fleet_msgs::msg::RobotState_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__fleet_msgs__msg__RobotState
    std::shared_ptr<fleet_msgs::msg::RobotState_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__fleet_msgs__msg__RobotState
    std::shared_ptr<fleet_msgs::msg::RobotState_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const RobotState_ & other) const
  {
    if (this->robot_id != other.robot_id) {
      return false;
    }
    if (this->timestamp != other.timestamp) {
      return false;
    }
    if (this->position != other.position) {
      return false;
    }
    if (this->velocity != other.velocity) {
      return false;
    }
    if (this->battery != other.battery) {
      return false;
    }
    if (this->current_task != other.current_task) {
      return false;
    }
    if (this->status != other.status) {
      return false;
    }
    return true;
  }
  bool operator!=(const RobotState_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct RobotState_

// alias to use template instance with default allocator
using RobotState =
  fleet_msgs::msg::RobotState_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace fleet_msgs

#endif  // FLEET_MSGS__MSG__DETAIL__ROBOT_STATE__STRUCT_HPP_
