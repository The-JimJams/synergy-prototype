// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from fleet_msgs:msg/RobotIntent.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fleet_msgs/msg/robot_intent.hpp"


#ifndef FLEET_MSGS__MSG__DETAIL__ROBOT_INTENT__TRAITS_HPP_
#define FLEET_MSGS__MSG__DETAIL__ROBOT_INTENT__TRAITS_HPP_

#include <stdint.h>

#include <array>
#include <cstddef>
#include <sstream>
#include <string>
#include <string_view>
#include <tuple>
#include <type_traits>
#include <utility>

#include "fleet_msgs/msg/detail/robot_intent__struct.hpp"
#include "rosidl_runtime_cpp/buffer__traits.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace fleet_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const RobotIntent & msg,
  std::ostream & out)
{
  out << "{";
  // member: robot_id
  {
    out << "robot_id: ";
    rosidl_generator_traits::value_to_yaml(msg.robot_id, out);
    out << ", ";
  }

  // member: planned_path
  {
    if (msg.planned_path.size() == 0) {
      out << "planned_path: []";
    } else {
      out << "planned_path: [";
      size_t pending_items = msg.planned_path.size();
      for (auto item : msg.planned_path) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: target_intersection
  {
    out << "target_intersection: ";
    rosidl_generator_traits::value_to_yaml(msg.target_intersection, out);
    out << ", ";
  }

  // member: eta
  {
    out << "eta: ";
    rosidl_generator_traits::value_to_yaml(msg.eta, out);
    out << ", ";
  }

  // member: priority
  {
    out << "priority: ";
    rosidl_generator_traits::value_to_yaml(msg.priority, out);
    out << ", ";
  }

  // member: task_id
  {
    out << "task_id: ";
    rosidl_generator_traits::value_to_yaml(msg.task_id, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const RobotIntent & msg,
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

  // member: planned_path
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.planned_path.size() == 0) {
      out << "planned_path: []\n";
    } else {
      out << "planned_path:\n";
      for (auto item : msg.planned_path) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: target_intersection
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "target_intersection: ";
    rosidl_generator_traits::value_to_yaml(msg.target_intersection, out);
    out << "\n";
  }

  // member: eta
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "eta: ";
    rosidl_generator_traits::value_to_yaml(msg.eta, out);
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

  // member: task_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "task_id: ";
    rosidl_generator_traits::value_to_yaml(msg.task_id, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const RobotIntent & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

template<typename T, std::enable_if_t<std::is_same_v<std::decay_t<T>, fleet_msgs::msg::RobotIntent>, int> = 0>
constexpr auto as_tuple_ref(T && msg)
{
  return std::forward_as_tuple(
    std::forward<T>(msg).robot_id,
    std::forward<T>(msg).planned_path,
    std::forward<T>(msg).target_intersection,
    std::forward<T>(msg).eta,
    std::forward<T>(msg).priority,
    std::forward<T>(msg).task_id);
}

}  // namespace msg

}  // namespace fleet_msgs

namespace rosidl_generator_traits
{

template<>
constexpr const char * data_type<fleet_msgs::msg::RobotIntent>()
{
  return "fleet_msgs::msg::RobotIntent";
}

template<>
constexpr const char * name<fleet_msgs::msg::RobotIntent>()
{
  return "fleet_msgs/msg/RobotIntent";
}

template<>
struct has_fixed_size<fleet_msgs::msg::RobotIntent>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<fleet_msgs::msg::RobotIntent>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<fleet_msgs::msg::RobotIntent>
  : std::true_type {};

template<>
struct MessageTraits<fleet_msgs::msg::RobotIntent>
{
  static constexpr std::size_t member_count = 6;
  static constexpr std::array<std::string_view, member_count> member_names = {
    "robot_id",
    "planned_path",
    "target_intersection",
    "eta",
    "priority",
    "task_id",
  };
};

}  // namespace rosidl_generator_traits

#endif  // FLEET_MSGS__MSG__DETAIL__ROBOT_INTENT__TRAITS_HPP_
