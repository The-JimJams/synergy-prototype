// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from fleet_msgs:msg/TaskAnnouncement.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "fleet_msgs/msg/task_announcement.hpp"


#ifndef FLEET_MSGS__MSG__DETAIL__TASK_ANNOUNCEMENT__TRAITS_HPP_
#define FLEET_MSGS__MSG__DETAIL__TASK_ANNOUNCEMENT__TRAITS_HPP_

#include <stdint.h>

#include <array>
#include <cstddef>
#include <sstream>
#include <string>
#include <string_view>
#include <tuple>
#include <type_traits>
#include <utility>

#include "fleet_msgs/msg/detail/task_announcement__struct.hpp"
#include "rosidl_runtime_cpp/buffer__traits.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace fleet_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const TaskAnnouncement & msg,
  std::ostream & out)
{
  out << "{";
  // member: task_id
  {
    out << "task_id: ";
    rosidl_generator_traits::value_to_yaml(msg.task_id, out);
    out << ", ";
  }

  // member: pickup
  {
    out << "pickup: ";
    rosidl_generator_traits::value_to_yaml(msg.pickup, out);
    out << ", ";
  }

  // member: dropoff
  {
    out << "dropoff: ";
    rosidl_generator_traits::value_to_yaml(msg.dropoff, out);
    out << ", ";
  }

  // member: deadline
  {
    out << "deadline: ";
    rosidl_generator_traits::value_to_yaml(msg.deadline, out);
    out << ", ";
  }

  // member: priority
  {
    out << "priority: ";
    rosidl_generator_traits::value_to_yaml(msg.priority, out);
    out << ", ";
  }

  // member: capability_requirements
  {
    if (msg.capability_requirements.size() == 0) {
      out << "capability_requirements: []";
    } else {
      out << "capability_requirements: [";
      size_t pending_items = msg.capability_requirements.size();
      for (auto item : msg.capability_requirements) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const TaskAnnouncement & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: task_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "task_id: ";
    rosidl_generator_traits::value_to_yaml(msg.task_id, out);
    out << "\n";
  }

  // member: pickup
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "pickup: ";
    rosidl_generator_traits::value_to_yaml(msg.pickup, out);
    out << "\n";
  }

  // member: dropoff
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "dropoff: ";
    rosidl_generator_traits::value_to_yaml(msg.dropoff, out);
    out << "\n";
  }

  // member: deadline
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "deadline: ";
    rosidl_generator_traits::value_to_yaml(msg.deadline, out);
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

  // member: capability_requirements
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.capability_requirements.size() == 0) {
      out << "capability_requirements: []\n";
    } else {
      out << "capability_requirements:\n";
      for (auto item : msg.capability_requirements) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const TaskAnnouncement & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

template<typename T, std::enable_if_t<std::is_same_v<std::decay_t<T>, fleet_msgs::msg::TaskAnnouncement>, int> = 0>
constexpr auto as_tuple_ref(T && msg)
{
  return std::forward_as_tuple(
    std::forward<T>(msg).task_id,
    std::forward<T>(msg).pickup,
    std::forward<T>(msg).dropoff,
    std::forward<T>(msg).deadline,
    std::forward<T>(msg).priority,
    std::forward<T>(msg).capability_requirements);
}

}  // namespace msg

}  // namespace fleet_msgs

namespace rosidl_generator_traits
{

template<>
constexpr const char * data_type<fleet_msgs::msg::TaskAnnouncement>()
{
  return "fleet_msgs::msg::TaskAnnouncement";
}

template<>
constexpr const char * name<fleet_msgs::msg::TaskAnnouncement>()
{
  return "fleet_msgs/msg/TaskAnnouncement";
}

template<>
struct has_fixed_size<fleet_msgs::msg::TaskAnnouncement>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<fleet_msgs::msg::TaskAnnouncement>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<fleet_msgs::msg::TaskAnnouncement>
  : std::true_type {};

template<>
struct MessageTraits<fleet_msgs::msg::TaskAnnouncement>
{
  static constexpr std::size_t member_count = 6;
  static constexpr std::array<std::string_view, member_count> member_names = {
    "task_id",
    "pickup",
    "dropoff",
    "deadline",
    "priority",
    "capability_requirements",
  };
};

}  // namespace rosidl_generator_traits

#endif  // FLEET_MSGS__MSG__DETAIL__TASK_ANNOUNCEMENT__TRAITS_HPP_
