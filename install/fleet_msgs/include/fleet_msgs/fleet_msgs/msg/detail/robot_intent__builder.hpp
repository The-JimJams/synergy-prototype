// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from fleet_msgs:msg/RobotIntent.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fleet_msgs/msg/robot_intent.hpp"


#ifndef FLEET_MSGS__MSG__DETAIL__ROBOT_INTENT__BUILDER_HPP_
#define FLEET_MSGS__MSG__DETAIL__ROBOT_INTENT__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "fleet_msgs/msg/detail/robot_intent__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace fleet_msgs
{

namespace msg
{

namespace builder
{

class Init_RobotIntent_task_id
{
public:
  explicit Init_RobotIntent_task_id(::fleet_msgs::msg::RobotIntent & msg)
  : msg_(msg)
  {}
  ::fleet_msgs::msg::RobotIntent task_id(::fleet_msgs::msg::RobotIntent::_task_id_type arg)
  {
    msg_.task_id = std::move(arg);
    return std::move(msg_);
  }

private:
  ::fleet_msgs::msg::RobotIntent msg_;
};

class Init_RobotIntent_priority
{
public:
  explicit Init_RobotIntent_priority(::fleet_msgs::msg::RobotIntent & msg)
  : msg_(msg)
  {}
  Init_RobotIntent_task_id priority(::fleet_msgs::msg::RobotIntent::_priority_type arg)
  {
    msg_.priority = std::move(arg);
    return Init_RobotIntent_task_id(msg_);
  }

private:
  ::fleet_msgs::msg::RobotIntent msg_;
};

class Init_RobotIntent_eta
{
public:
  explicit Init_RobotIntent_eta(::fleet_msgs::msg::RobotIntent & msg)
  : msg_(msg)
  {}
  Init_RobotIntent_priority eta(::fleet_msgs::msg::RobotIntent::_eta_type arg)
  {
    msg_.eta = std::move(arg);
    return Init_RobotIntent_priority(msg_);
  }

private:
  ::fleet_msgs::msg::RobotIntent msg_;
};

class Init_RobotIntent_target_intersection
{
public:
  explicit Init_RobotIntent_target_intersection(::fleet_msgs::msg::RobotIntent & msg)
  : msg_(msg)
  {}
  Init_RobotIntent_eta target_intersection(::fleet_msgs::msg::RobotIntent::_target_intersection_type arg)
  {
    msg_.target_intersection = std::move(arg);
    return Init_RobotIntent_eta(msg_);
  }

private:
  ::fleet_msgs::msg::RobotIntent msg_;
};

class Init_RobotIntent_planned_path
{
public:
  explicit Init_RobotIntent_planned_path(::fleet_msgs::msg::RobotIntent & msg)
  : msg_(msg)
  {}
  Init_RobotIntent_target_intersection planned_path(::fleet_msgs::msg::RobotIntent::_planned_path_type arg)
  {
    msg_.planned_path = std::move(arg);
    return Init_RobotIntent_target_intersection(msg_);
  }

private:
  ::fleet_msgs::msg::RobotIntent msg_;
};

class Init_RobotIntent_robot_id
{
public:
  Init_RobotIntent_robot_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_RobotIntent_planned_path robot_id(::fleet_msgs::msg::RobotIntent::_robot_id_type arg)
  {
    msg_.robot_id = std::move(arg);
    return Init_RobotIntent_planned_path(msg_);
  }

private:
  ::fleet_msgs::msg::RobotIntent msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::fleet_msgs::msg::RobotIntent>()
{
  return fleet_msgs::msg::builder::Init_RobotIntent_robot_id();
}

}  // namespace fleet_msgs

#endif  // FLEET_MSGS__MSG__DETAIL__ROBOT_INTENT__BUILDER_HPP_
