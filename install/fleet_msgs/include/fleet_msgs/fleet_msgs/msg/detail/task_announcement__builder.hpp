// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from fleet_msgs:msg/TaskAnnouncement.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fleet_msgs/msg/task_announcement.hpp"


#ifndef FLEET_MSGS__MSG__DETAIL__TASK_ANNOUNCEMENT__BUILDER_HPP_
#define FLEET_MSGS__MSG__DETAIL__TASK_ANNOUNCEMENT__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "fleet_msgs/msg/detail/task_announcement__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace fleet_msgs
{

namespace msg
{

namespace builder
{

class Init_TaskAnnouncement_capability_requirements
{
public:
  explicit Init_TaskAnnouncement_capability_requirements(::fleet_msgs::msg::TaskAnnouncement & msg)
  : msg_(msg)
  {}
  ::fleet_msgs::msg::TaskAnnouncement capability_requirements(::fleet_msgs::msg::TaskAnnouncement::_capability_requirements_type arg)
  {
    msg_.capability_requirements = std::move(arg);
    return std::move(msg_);
  }

private:
  ::fleet_msgs::msg::TaskAnnouncement msg_;
};

class Init_TaskAnnouncement_priority
{
public:
  explicit Init_TaskAnnouncement_priority(::fleet_msgs::msg::TaskAnnouncement & msg)
  : msg_(msg)
  {}
  Init_TaskAnnouncement_capability_requirements priority(::fleet_msgs::msg::TaskAnnouncement::_priority_type arg)
  {
    msg_.priority = std::move(arg);
    return Init_TaskAnnouncement_capability_requirements(msg_);
  }

private:
  ::fleet_msgs::msg::TaskAnnouncement msg_;
};

class Init_TaskAnnouncement_deadline
{
public:
  explicit Init_TaskAnnouncement_deadline(::fleet_msgs::msg::TaskAnnouncement & msg)
  : msg_(msg)
  {}
  Init_TaskAnnouncement_priority deadline(::fleet_msgs::msg::TaskAnnouncement::_deadline_type arg)
  {
    msg_.deadline = std::move(arg);
    return Init_TaskAnnouncement_priority(msg_);
  }

private:
  ::fleet_msgs::msg::TaskAnnouncement msg_;
};

class Init_TaskAnnouncement_dropoff
{
public:
  explicit Init_TaskAnnouncement_dropoff(::fleet_msgs::msg::TaskAnnouncement & msg)
  : msg_(msg)
  {}
  Init_TaskAnnouncement_deadline dropoff(::fleet_msgs::msg::TaskAnnouncement::_dropoff_type arg)
  {
    msg_.dropoff = std::move(arg);
    return Init_TaskAnnouncement_deadline(msg_);
  }

private:
  ::fleet_msgs::msg::TaskAnnouncement msg_;
};

class Init_TaskAnnouncement_pickup
{
public:
  explicit Init_TaskAnnouncement_pickup(::fleet_msgs::msg::TaskAnnouncement & msg)
  : msg_(msg)
  {}
  Init_TaskAnnouncement_dropoff pickup(::fleet_msgs::msg::TaskAnnouncement::_pickup_type arg)
  {
    msg_.pickup = std::move(arg);
    return Init_TaskAnnouncement_dropoff(msg_);
  }

private:
  ::fleet_msgs::msg::TaskAnnouncement msg_;
};

class Init_TaskAnnouncement_task_id
{
public:
  Init_TaskAnnouncement_task_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_TaskAnnouncement_pickup task_id(::fleet_msgs::msg::TaskAnnouncement::_task_id_type arg)
  {
    msg_.task_id = std::move(arg);
    return Init_TaskAnnouncement_pickup(msg_);
  }

private:
  ::fleet_msgs::msg::TaskAnnouncement msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::fleet_msgs::msg::TaskAnnouncement>()
{
  return fleet_msgs::msg::builder::Init_TaskAnnouncement_task_id();
}

}  // namespace fleet_msgs

#endif  // FLEET_MSGS__MSG__DETAIL__TASK_ANNOUNCEMENT__BUILDER_HPP_
