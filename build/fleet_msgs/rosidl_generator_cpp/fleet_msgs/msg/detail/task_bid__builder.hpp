// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from fleet_msgs:msg/TaskBid.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fleet_msgs/msg/task_bid.hpp"


#ifndef FLEET_MSGS__MSG__DETAIL__TASK_BID__BUILDER_HPP_
#define FLEET_MSGS__MSG__DETAIL__TASK_BID__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "fleet_msgs/msg/detail/task_bid__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace fleet_msgs
{

namespace msg
{

namespace builder
{

class Init_TaskBid_confidence
{
public:
  explicit Init_TaskBid_confidence(::fleet_msgs::msg::TaskBid & msg)
  : msg_(msg)
  {}
  ::fleet_msgs::msg::TaskBid confidence(::fleet_msgs::msg::TaskBid::_confidence_type arg)
  {
    msg_.confidence = std::move(arg);
    return std::move(msg_);
  }

private:
  ::fleet_msgs::msg::TaskBid msg_;
};

class Init_TaskBid_battery_cost
{
public:
  explicit Init_TaskBid_battery_cost(::fleet_msgs::msg::TaskBid & msg)
  : msg_(msg)
  {}
  Init_TaskBid_confidence battery_cost(::fleet_msgs::msg::TaskBid::_battery_cost_type arg)
  {
    msg_.battery_cost = std::move(arg);
    return Init_TaskBid_confidence(msg_);
  }

private:
  ::fleet_msgs::msg::TaskBid msg_;
};

class Init_TaskBid_distance
{
public:
  explicit Init_TaskBid_distance(::fleet_msgs::msg::TaskBid & msg)
  : msg_(msg)
  {}
  Init_TaskBid_battery_cost distance(::fleet_msgs::msg::TaskBid::_distance_type arg)
  {
    msg_.distance = std::move(arg);
    return Init_TaskBid_battery_cost(msg_);
  }

private:
  ::fleet_msgs::msg::TaskBid msg_;
};

class Init_TaskBid_estimated_time
{
public:
  explicit Init_TaskBid_estimated_time(::fleet_msgs::msg::TaskBid & msg)
  : msg_(msg)
  {}
  Init_TaskBid_distance estimated_time(::fleet_msgs::msg::TaskBid::_estimated_time_type arg)
  {
    msg_.estimated_time = std::move(arg);
    return Init_TaskBid_distance(msg_);
  }

private:
  ::fleet_msgs::msg::TaskBid msg_;
};

class Init_TaskBid_task_id
{
public:
  explicit Init_TaskBid_task_id(::fleet_msgs::msg::TaskBid & msg)
  : msg_(msg)
  {}
  Init_TaskBid_estimated_time task_id(::fleet_msgs::msg::TaskBid::_task_id_type arg)
  {
    msg_.task_id = std::move(arg);
    return Init_TaskBid_estimated_time(msg_);
  }

private:
  ::fleet_msgs::msg::TaskBid msg_;
};

class Init_TaskBid_robot_id
{
public:
  Init_TaskBid_robot_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_TaskBid_task_id robot_id(::fleet_msgs::msg::TaskBid::_robot_id_type arg)
  {
    msg_.robot_id = std::move(arg);
    return Init_TaskBid_task_id(msg_);
  }

private:
  ::fleet_msgs::msg::TaskBid msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::fleet_msgs::msg::TaskBid>()
{
  return fleet_msgs::msg::builder::Init_TaskBid_robot_id();
}

}  // namespace fleet_msgs

#endif  // FLEET_MSGS__MSG__DETAIL__TASK_BID__BUILDER_HPP_
