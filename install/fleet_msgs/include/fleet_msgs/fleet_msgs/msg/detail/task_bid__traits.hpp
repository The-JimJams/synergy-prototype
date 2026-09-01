// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from fleet_msgs:msg/TaskBid.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fleet_msgs/msg/task_bid.hpp"


#ifndef FLEET_MSGS__MSG__DETAIL__TASK_BID__TRAITS_HPP_
#define FLEET_MSGS__MSG__DETAIL__TASK_BID__TRAITS_HPP_

#include <stdint.h>

#include <array>
#include <cstddef>
#include <sstream>
#include <string>
#include <string_view>
#include <tuple>
#include <type_traits>
#include <utility>

#include "fleet_msgs/msg/detail/task_bid__struct.hpp"
#include "rosidl_runtime_cpp/buffer__traits.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace fleet_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const TaskBid & msg,
  std::ostream & out)
{
  out << "{";
  // member: robot_id
  {
    out << "robot_id: ";
    rosidl_generator_traits::value_to_yaml(msg.robot_id, out);
    out << ", ";
  }

  // member: task_id
  {
    out << "task_id: ";
    rosidl_generator_traits::value_to_yaml(msg.task_id, out);
    out << ", ";
  }

  // member: estimated_time
  {
    out << "estimated_time: ";
    rosidl_generator_traits::value_to_yaml(msg.estimated_time, out);
    out << ", ";
  }

  // member: distance
  {
    out << "distance: ";
    rosidl_generator_traits::value_to_yaml(msg.distance, out);
    out << ", ";
  }

  // member: battery_cost
  {
    out << "battery_cost: ";
    rosidl_generator_traits::value_to_yaml(msg.battery_cost, out);
    out << ", ";
  }

  // member: confidence
  {
    out << "confidence: ";
    rosidl_generator_traits::value_to_yaml(msg.confidence, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const TaskBid & msg,
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

  // member: task_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "task_id: ";
    rosidl_generator_traits::value_to_yaml(msg.task_id, out);
    out << "\n";
  }

  // member: estimated_time
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "estimated_time: ";
    rosidl_generator_traits::value_to_yaml(msg.estimated_time, out);
    out << "\n";
  }

  // member: distance
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "distance: ";
    rosidl_generator_traits::value_to_yaml(msg.distance, out);
    out << "\n";
  }

  // member: battery_cost
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "battery_cost: ";
    rosidl_generator_traits::value_to_yaml(msg.battery_cost, out);
    out << "\n";
  }

  // member: confidence
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "confidence: ";
    rosidl_generator_traits::value_to_yaml(msg.confidence, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const TaskBid & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

template<typename T, std::enable_if_t<std::is_same_v<std::decay_t<T>, fleet_msgs::msg::TaskBid>, int> = 0>
constexpr auto as_tuple_ref(T && msg)
{
  return std::forward_as_tuple(
    std::forward<T>(msg).robot_id,
    std::forward<T>(msg).task_id,
    std::forward<T>(msg).estimated_time,
    std::forward<T>(msg).distance,
    std::forward<T>(msg).battery_cost,
    std::forward<T>(msg).confidence);
}

}  // namespace msg

}  // namespace fleet_msgs

namespace rosidl_generator_traits
{

template<>
constexpr const char * data_type<fleet_msgs::msg::TaskBid>()
{
  return "fleet_msgs::msg::TaskBid";
}

template<>
constexpr const char * name<fleet_msgs::msg::TaskBid>()
{
  return "fleet_msgs/msg/TaskBid";
}

template<>
struct has_fixed_size<fleet_msgs::msg::TaskBid>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<fleet_msgs::msg::TaskBid>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<fleet_msgs::msg::TaskBid>
  : std::true_type {};

template<>
struct MessageTraits<fleet_msgs::msg::TaskBid>
{
  static constexpr std::size_t member_count = 6;
  static constexpr std::array<std::string_view, member_count> member_names = {
    "robot_id",
    "task_id",
    "estimated_time",
    "distance",
    "battery_cost",
    "confidence",
  };
};

}  // namespace rosidl_generator_traits

#endif  // FLEET_MSGS__MSG__DETAIL__TASK_BID__TRAITS_HPP_
