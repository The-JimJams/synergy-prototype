// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from fleet_msgs:msg/Heartbeat.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fleet_msgs/msg/heartbeat.hpp"


#ifndef FLEET_MSGS__MSG__DETAIL__HEARTBEAT__BUILDER_HPP_
#define FLEET_MSGS__MSG__DETAIL__HEARTBEAT__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "fleet_msgs/msg/detail/heartbeat__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace fleet_msgs
{

namespace msg
{

namespace builder
{

class Init_Heartbeat_timestamp
{
public:
  explicit Init_Heartbeat_timestamp(::fleet_msgs::msg::Heartbeat & msg)
  : msg_(msg)
  {}
  ::fleet_msgs::msg::Heartbeat timestamp(::fleet_msgs::msg::Heartbeat::_timestamp_type arg)
  {
    msg_.timestamp = std::move(arg);
    return std::move(msg_);
  }

private:
  ::fleet_msgs::msg::Heartbeat msg_;
};

class Init_Heartbeat_robot_id
{
public:
  Init_Heartbeat_robot_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Heartbeat_timestamp robot_id(::fleet_msgs::msg::Heartbeat::_robot_id_type arg)
  {
    msg_.robot_id = std::move(arg);
    return Init_Heartbeat_timestamp(msg_);
  }

private:
  ::fleet_msgs::msg::Heartbeat msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::fleet_msgs::msg::Heartbeat>()
{
  return fleet_msgs::msg::builder::Init_Heartbeat_robot_id();
}

}  // namespace fleet_msgs

#endif  // FLEET_MSGS__MSG__DETAIL__HEARTBEAT__BUILDER_HPP_
