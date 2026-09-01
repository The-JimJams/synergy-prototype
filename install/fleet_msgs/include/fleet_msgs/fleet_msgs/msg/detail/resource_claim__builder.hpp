// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from fleet_msgs:msg/ResourceClaim.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fleet_msgs/msg/resource_claim.hpp"


#ifndef FLEET_MSGS__MSG__DETAIL__RESOURCE_CLAIM__BUILDER_HPP_
#define FLEET_MSGS__MSG__DETAIL__RESOURCE_CLAIM__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "fleet_msgs/msg/detail/resource_claim__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace fleet_msgs
{

namespace msg
{

namespace builder
{

class Init_ResourceClaim_status
{
public:
  explicit Init_ResourceClaim_status(::fleet_msgs::msg::ResourceClaim & msg)
  : msg_(msg)
  {}
  ::fleet_msgs::msg::ResourceClaim status(::fleet_msgs::msg::ResourceClaim::_status_type arg)
  {
    msg_.status = std::move(arg);
    return std::move(msg_);
  }

private:
  ::fleet_msgs::msg::ResourceClaim msg_;
};

class Init_ResourceClaim_claim_id
{
public:
  explicit Init_ResourceClaim_claim_id(::fleet_msgs::msg::ResourceClaim & msg)
  : msg_(msg)
  {}
  Init_ResourceClaim_status claim_id(::fleet_msgs::msg::ResourceClaim::_claim_id_type arg)
  {
    msg_.claim_id = std::move(arg);
    return Init_ResourceClaim_status(msg_);
  }

private:
  ::fleet_msgs::msg::ResourceClaim msg_;
};

class Init_ResourceClaim_priority
{
public:
  explicit Init_ResourceClaim_priority(::fleet_msgs::msg::ResourceClaim & msg)
  : msg_(msg)
  {}
  Init_ResourceClaim_claim_id priority(::fleet_msgs::msg::ResourceClaim::_priority_type arg)
  {
    msg_.priority = std::move(arg);
    return Init_ResourceClaim_claim_id(msg_);
  }

private:
  ::fleet_msgs::msg::ResourceClaim msg_;
};

class Init_ResourceClaim_end_time
{
public:
  explicit Init_ResourceClaim_end_time(::fleet_msgs::msg::ResourceClaim & msg)
  : msg_(msg)
  {}
  Init_ResourceClaim_priority end_time(::fleet_msgs::msg::ResourceClaim::_end_time_type arg)
  {
    msg_.end_time = std::move(arg);
    return Init_ResourceClaim_priority(msg_);
  }

private:
  ::fleet_msgs::msg::ResourceClaim msg_;
};

class Init_ResourceClaim_start_time
{
public:
  explicit Init_ResourceClaim_start_time(::fleet_msgs::msg::ResourceClaim & msg)
  : msg_(msg)
  {}
  Init_ResourceClaim_end_time start_time(::fleet_msgs::msg::ResourceClaim::_start_time_type arg)
  {
    msg_.start_time = std::move(arg);
    return Init_ResourceClaim_end_time(msg_);
  }

private:
  ::fleet_msgs::msg::ResourceClaim msg_;
};

class Init_ResourceClaim_resource
{
public:
  explicit Init_ResourceClaim_resource(::fleet_msgs::msg::ResourceClaim & msg)
  : msg_(msg)
  {}
  Init_ResourceClaim_start_time resource(::fleet_msgs::msg::ResourceClaim::_resource_type arg)
  {
    msg_.resource = std::move(arg);
    return Init_ResourceClaim_start_time(msg_);
  }

private:
  ::fleet_msgs::msg::ResourceClaim msg_;
};

class Init_ResourceClaim_robot_id
{
public:
  Init_ResourceClaim_robot_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ResourceClaim_resource robot_id(::fleet_msgs::msg::ResourceClaim::_robot_id_type arg)
  {
    msg_.robot_id = std::move(arg);
    return Init_ResourceClaim_resource(msg_);
  }

private:
  ::fleet_msgs::msg::ResourceClaim msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::fleet_msgs::msg::ResourceClaim>()
{
  return fleet_msgs::msg::builder::Init_ResourceClaim_robot_id();
}

}  // namespace fleet_msgs

#endif  // FLEET_MSGS__MSG__DETAIL__RESOURCE_CLAIM__BUILDER_HPP_
