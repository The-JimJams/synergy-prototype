// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from fleet_msgs:msg/RobotState.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fleet_msgs/msg/robot_state.hpp"


#ifndef FLEET_MSGS__MSG__DETAIL__ROBOT_STATE__BUILDER_HPP_
#define FLEET_MSGS__MSG__DETAIL__ROBOT_STATE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "fleet_msgs/msg/detail/robot_state__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace fleet_msgs
{

namespace msg
{

namespace builder
{

class Init_RobotState_status
{
public:
  explicit Init_RobotState_status(::fleet_msgs::msg::RobotState & msg)
  : msg_(msg)
  {}
  ::fleet_msgs::msg::RobotState status(::fleet_msgs::msg::RobotState::_status_type arg)
  {
    msg_.status = std::move(arg);
    return std::move(msg_);
  }

private:
  ::fleet_msgs::msg::RobotState msg_;
};

class Init_RobotState_current_task
{
public:
  explicit Init_RobotState_current_task(::fleet_msgs::msg::RobotState & msg)
  : msg_(msg)
  {}
  Init_RobotState_status current_task(::fleet_msgs::msg::RobotState::_current_task_type arg)
  {
    msg_.current_task = std::move(arg);
    return Init_RobotState_status(msg_);
  }

private:
  ::fleet_msgs::msg::RobotState msg_;
};

class Init_RobotState_battery
{
public:
  explicit Init_RobotState_battery(::fleet_msgs::msg::RobotState & msg)
  : msg_(msg)
  {}
  Init_RobotState_current_task battery(::fleet_msgs::msg::RobotState::_battery_type arg)
  {
    msg_.battery = std::move(arg);
    return Init_RobotState_current_task(msg_);
  }

private:
  ::fleet_msgs::msg::RobotState msg_;
};

class Init_RobotState_velocity
{
public:
  explicit Init_RobotState_velocity(::fleet_msgs::msg::RobotState & msg)
  : msg_(msg)
  {}
  Init_RobotState_battery velocity(::fleet_msgs::msg::RobotState::_velocity_type arg)
  {
    msg_.velocity = std::move(arg);
    return Init_RobotState_battery(msg_);
  }

private:
  ::fleet_msgs::msg::RobotState msg_;
};

class Init_RobotState_position
{
public:
  explicit Init_RobotState_position(::fleet_msgs::msg::RobotState & msg)
  : msg_(msg)
  {}
  Init_RobotState_velocity position(::fleet_msgs::msg::RobotState::_position_type arg)
  {
    msg_.position = std::move(arg);
    return Init_RobotState_velocity(msg_);
  }

private:
  ::fleet_msgs::msg::RobotState msg_;
};

class Init_RobotState_timestamp
{
public:
  explicit Init_RobotState_timestamp(::fleet_msgs::msg::RobotState & msg)
  : msg_(msg)
  {}
  Init_RobotState_position timestamp(::fleet_msgs::msg::RobotState::_timestamp_type arg)
  {
    msg_.timestamp = std::move(arg);
    return Init_RobotState_position(msg_);
  }

private:
  ::fleet_msgs::msg::RobotState msg_;
};

class Init_RobotState_robot_id
{
public:
  Init_RobotState_robot_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_RobotState_timestamp robot_id(::fleet_msgs::msg::RobotState::_robot_id_type arg)
  {
    msg_.robot_id = std::move(arg);
    return Init_RobotState_timestamp(msg_);
  }

private:
  ::fleet_msgs::msg::RobotState msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::fleet_msgs::msg::RobotState>()
{
  return fleet_msgs::msg::builder::Init_RobotState_robot_id();
}

}  // namespace fleet_msgs

#endif  // FLEET_MSGS__MSG__DETAIL__ROBOT_STATE__BUILDER_HPP_
