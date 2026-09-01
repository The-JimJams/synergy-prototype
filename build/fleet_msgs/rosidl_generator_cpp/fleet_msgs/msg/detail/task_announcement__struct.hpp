// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from fleet_msgs:msg/TaskAnnouncement.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fleet_msgs/msg/task_announcement.hpp"


#ifndef FLEET_MSGS__MSG__DETAIL__TASK_ANNOUNCEMENT__STRUCT_HPP_
#define FLEET_MSGS__MSG__DETAIL__TASK_ANNOUNCEMENT__STRUCT_HPP_

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
# define DEPRECATED__fleet_msgs__msg__TaskAnnouncement __attribute__((deprecated))
#else
# define DEPRECATED__fleet_msgs__msg__TaskAnnouncement __declspec(deprecated)
#endif

namespace fleet_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct TaskAnnouncement_
{
  using Type = TaskAnnouncement_<ContainerAllocator>;

  explicit TaskAnnouncement_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->task_id = "";
      this->pickup = "";
      this->dropoff = "";
      this->deadline = 0.0;
      this->priority = 0l;
    }
  }

  explicit TaskAnnouncement_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : task_id(_alloc),
    pickup(_alloc),
    dropoff(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->task_id = "";
      this->pickup = "";
      this->dropoff = "";
      this->deadline = 0.0;
      this->priority = 0l;
    }
  }

  // field types and members
  using _task_id_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _task_id_type task_id;
  using _pickup_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _pickup_type pickup;
  using _dropoff_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _dropoff_type dropoff;
  using _deadline_type =
    double;
  _deadline_type deadline;
  using _priority_type =
    int32_t;
  _priority_type priority;
  using _capability_requirements_type =
    std::vector<std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>>>;
  _capability_requirements_type capability_requirements;

  // setters for named parameter idiom
  Type & set__task_id(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->task_id = _arg;
    return *this;
  }
  Type & set__pickup(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->pickup = _arg;
    return *this;
  }
  Type & set__dropoff(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->dropoff = _arg;
    return *this;
  }
  Type & set__deadline(
    const double & _arg)
  {
    this->deadline = _arg;
    return *this;
  }
  Type & set__priority(
    const int32_t & _arg)
  {
    this->priority = _arg;
    return *this;
  }
  Type & set__capability_requirements(
    const std::vector<std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>>> & _arg)
  {
    this->capability_requirements = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    fleet_msgs::msg::TaskAnnouncement_<ContainerAllocator> *;
  using ConstRawPtr =
    const fleet_msgs::msg::TaskAnnouncement_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<fleet_msgs::msg::TaskAnnouncement_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<fleet_msgs::msg::TaskAnnouncement_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      fleet_msgs::msg::TaskAnnouncement_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<fleet_msgs::msg::TaskAnnouncement_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      fleet_msgs::msg::TaskAnnouncement_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<fleet_msgs::msg::TaskAnnouncement_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<fleet_msgs::msg::TaskAnnouncement_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<fleet_msgs::msg::TaskAnnouncement_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__fleet_msgs__msg__TaskAnnouncement
    std::shared_ptr<fleet_msgs::msg::TaskAnnouncement_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__fleet_msgs__msg__TaskAnnouncement
    std::shared_ptr<fleet_msgs::msg::TaskAnnouncement_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const TaskAnnouncement_ & other) const
  {
    if (this->task_id != other.task_id) {
      return false;
    }
    if (this->pickup != other.pickup) {
      return false;
    }
    if (this->dropoff != other.dropoff) {
      return false;
    }
    if (this->deadline != other.deadline) {
      return false;
    }
    if (this->priority != other.priority) {
      return false;
    }
    if (this->capability_requirements != other.capability_requirements) {
      return false;
    }
    return true;
  }
  bool operator!=(const TaskAnnouncement_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct TaskAnnouncement_

// alias to use template instance with default allocator
using TaskAnnouncement =
  fleet_msgs::msg::TaskAnnouncement_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace fleet_msgs

#endif  // FLEET_MSGS__MSG__DETAIL__TASK_ANNOUNCEMENT__STRUCT_HPP_
