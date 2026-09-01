// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from fleet_msgs:msg/ResourceClaim.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fleet_msgs/msg/resource_claim.hpp"


#ifndef FLEET_MSGS__MSG__DETAIL__RESOURCE_CLAIM__TRAITS_HPP_
#define FLEET_MSGS__MSG__DETAIL__RESOURCE_CLAIM__TRAITS_HPP_

#include <stdint.h>

#include <array>
#include <cstddef>
#include <sstream>
#include <string>
#include <string_view>
#include <tuple>
#include <type_traits>
#include <utility>

#include "fleet_msgs/msg/detail/resource_claim__struct.hpp"
#include "rosidl_runtime_cpp/buffer__traits.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace fleet_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const ResourceClaim & msg,
  std::ostream & out)
{
  out << "{";
  // member: robot_id
  {
    out << "robot_id: ";
    rosidl_generator_traits::value_to_yaml(msg.robot_id, out);
    out << ", ";
  }

  // member: resource
  {
    out << "resource: ";
    rosidl_generator_traits::value_to_yaml(msg.resource, out);
    out << ", ";
  }

  // member: start_time
  {
    out << "start_time: ";
    rosidl_generator_traits::value_to_yaml(msg.start_time, out);
    out << ", ";
  }

  // member: end_time
  {
    out << "end_time: ";
    rosidl_generator_traits::value_to_yaml(msg.end_time, out);
    out << ", ";
  }

  // member: priority
  {
    out << "priority: ";
    rosidl_generator_traits::value_to_yaml(msg.priority, out);
    out << ", ";
  }

  // member: claim_id
  {
    out << "claim_id: ";
    rosidl_generator_traits::value_to_yaml(msg.claim_id, out);
    out << ", ";
  }

  // member: status
  {
    out << "status: ";
    rosidl_generator_traits::value_to_yaml(msg.status, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ResourceClaim & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: robot_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "robot_id: ";
    rosidl_generator_traits::value_to_yaml(msg.robot_id, out);
    out << "\n";
  }

  // member: resource
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "resource: ";
    rosidl_generator_traits::value_to_yaml(msg.resource, out);
    out << "\n";
  }

  // member: start_time
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "start_time: ";
    rosidl_generator_traits::value_to_yaml(msg.start_time, out);
    out << "\n";
  }

  // member: end_time
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "end_time: ";
    rosidl_generator_traits::value_to_yaml(msg.end_time, out);
    out << "\n";
  }

  // member: priority
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "priority: ";
    rosidl_generator_traits::value_to_yaml(msg.priority, out);
    out << "\n";
  }

  // member: claim_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "claim_id: ";
    rosidl_generator_traits::value_to_yaml(msg.claim_id, out);
    out << "\n";
  }

  // member: status
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "status: ";
    rosidl_generator_traits::value_to_yaml(msg.status, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ResourceClaim & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

template<typename T, std::enable_if_t<std::is_same_v<std::decay_t<T>, fleet_msgs::msg::ResourceClaim>, int> = 0>
constexpr auto as_tuple_ref(T && msg)
{
  return std::forward_as_tuple(
    std::forward<T>(msg).robot_id,
    std::forward<T>(msg).resource,
    std::forward<T>(msg).start_time,
    std::forward<T>(msg).end_time,
    std::forward<T>(msg).priority,
    std::forward<T>(msg).claim_id,
    std::forward<T>(msg).status);
}

}  // namespace msg

}  // namespace fleet_msgs

namespace rosidl_generator_traits
{

template<>
constexpr const char * data_type<fleet_msgs::msg::ResourceClaim>()
{
  return "fleet_msgs::msg::ResourceClaim";
}

template<>
constexpr const char * name<fleet_msgs::msg::ResourceClaim>()
{
  return "fleet_msgs/msg/ResourceClaim";
}

template<>
struct has_fixed_size<fleet_msgs::msg::ResourceClaim>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<fleet_msgs::msg::ResourceClaim>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<fleet_msgs::msg::ResourceClaim>
  : std::true_type {};

template<>
struct MessageTraits<fleet_msgs::msg::ResourceClaim>
{
  static constexpr std::size_t member_count = 7;
  static constexpr std::array<std::string_view, member_count> member_names = {
    "robot_id",
    "resource",
    "start_time",
    "end_time",
    "priority",
    "claim_id",
    "status",
  };
};

}  // namespace rosidl_generator_traits

#endif  // FLEET_MSGS__MSG__DETAIL__RESOURCE_CLAIM__TRAITS_HPP_
