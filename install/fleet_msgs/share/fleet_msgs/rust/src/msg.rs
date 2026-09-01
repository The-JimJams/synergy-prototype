#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to fleet_msgs__msg__RobotState

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct RobotState {

    // This member is not documented.
    #[allow(missing_docs)]
    pub robot_id: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub timestamp: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub position: [f64; 2],


    // This member is not documented.
    #[allow(missing_docs)]
    pub velocity: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub battery: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub current_task: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub status: std::string::String,

}



impl Default for RobotState {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::RobotState::default())
  }
}

impl rosidl_runtime_rs::Message for RobotState {
  type RmwMsg = super::msg::rmw::RobotState;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        robot_id: msg.robot_id.as_str().into(),
        timestamp: msg.timestamp,
        position: msg.position,
        velocity: msg.velocity,
        battery: msg.battery,
        current_task: msg.current_task.as_str().into(),
        status: msg.status.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        robot_id: msg.robot_id.as_str().into(),
      timestamp: msg.timestamp,
        position: msg.position,
      velocity: msg.velocity,
      battery: msg.battery,
        current_task: msg.current_task.as_str().into(),
        status: msg.status.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      robot_id: msg.robot_id.to_string(),
      timestamp: msg.timestamp,
      position: msg.position,
      velocity: msg.velocity,
      battery: msg.battery,
      current_task: msg.current_task.to_string(),
      status: msg.status.to_string(),
    }
  }
}


// Corresponds to fleet_msgs__msg__RobotIntent

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct RobotIntent {

    // This member is not documented.
    #[allow(missing_docs)]
    pub robot_id: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub planned_path: Vec<std::string::String>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub target_intersection: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub eta: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub priority: i32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub task_id: std::string::String,

}



impl Default for RobotIntent {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::RobotIntent::default())
  }
}

impl rosidl_runtime_rs::Message for RobotIntent {
  type RmwMsg = super::msg::rmw::RobotIntent;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        robot_id: msg.robot_id.as_str().into(),
        planned_path: msg.planned_path
          .into_iter()
          .map(|elem| elem.as_str().into())
          .collect(),
        target_intersection: msg.target_intersection.as_str().into(),
        eta: msg.eta,
        priority: msg.priority,
        task_id: msg.task_id.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        robot_id: msg.robot_id.as_str().into(),
        planned_path: msg.planned_path
          .iter()
          .map(|elem| elem.as_str().into())
          .collect(),
        target_intersection: msg.target_intersection.as_str().into(),
      eta: msg.eta,
      priority: msg.priority,
        task_id: msg.task_id.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      robot_id: msg.robot_id.to_string(),
      planned_path: msg.planned_path
          .into_iter()
          .map(|elem| elem.to_string())
          .collect(),
      target_intersection: msg.target_intersection.to_string(),
      eta: msg.eta,
      priority: msg.priority,
      task_id: msg.task_id.to_string(),
    }
  }
}


// Corresponds to fleet_msgs__msg__ResourceClaim

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ResourceClaim {

    // This member is not documented.
    #[allow(missing_docs)]
    pub robot_id: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub resource: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub start_time: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub end_time: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub priority: i32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub claim_id: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub status: std::string::String,

}



impl Default for ResourceClaim {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::ResourceClaim::default())
  }
}

impl rosidl_runtime_rs::Message for ResourceClaim {
  type RmwMsg = super::msg::rmw::ResourceClaim;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        robot_id: msg.robot_id.as_str().into(),
        resource: msg.resource.as_str().into(),
        start_time: msg.start_time,
        end_time: msg.end_time,
        priority: msg.priority,
        claim_id: msg.claim_id.as_str().into(),
        status: msg.status.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        robot_id: msg.robot_id.as_str().into(),
        resource: msg.resource.as_str().into(),
      start_time: msg.start_time,
      end_time: msg.end_time,
      priority: msg.priority,
        claim_id: msg.claim_id.as_str().into(),
        status: msg.status.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      robot_id: msg.robot_id.to_string(),
      resource: msg.resource.to_string(),
      start_time: msg.start_time,
      end_time: msg.end_time,
      priority: msg.priority,
      claim_id: msg.claim_id.to_string(),
      status: msg.status.to_string(),
    }
  }
}


// Corresponds to fleet_msgs__msg__TaskAnnouncement

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TaskAnnouncement {

    // This member is not documented.
    #[allow(missing_docs)]
    pub task_id: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub pickup: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub dropoff: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub deadline: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub priority: i32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub capability_requirements: Vec<std::string::String>,

}



impl Default for TaskAnnouncement {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::TaskAnnouncement::default())
  }
}

impl rosidl_runtime_rs::Message for TaskAnnouncement {
  type RmwMsg = super::msg::rmw::TaskAnnouncement;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        task_id: msg.task_id.as_str().into(),
        pickup: msg.pickup.as_str().into(),
        dropoff: msg.dropoff.as_str().into(),
        deadline: msg.deadline,
        priority: msg.priority,
        capability_requirements: msg.capability_requirements
          .into_iter()
          .map(|elem| elem.as_str().into())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        task_id: msg.task_id.as_str().into(),
        pickup: msg.pickup.as_str().into(),
        dropoff: msg.dropoff.as_str().into(),
      deadline: msg.deadline,
      priority: msg.priority,
        capability_requirements: msg.capability_requirements
          .iter()
          .map(|elem| elem.as_str().into())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      task_id: msg.task_id.to_string(),
      pickup: msg.pickup.to_string(),
      dropoff: msg.dropoff.to_string(),
      deadline: msg.deadline,
      priority: msg.priority,
      capability_requirements: msg.capability_requirements
          .into_iter()
          .map(|elem| elem.to_string())
          .collect(),
    }
  }
}


// Corresponds to fleet_msgs__msg__TaskBid

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TaskBid {

    // This member is not documented.
    #[allow(missing_docs)]
    pub robot_id: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub task_id: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub estimated_time: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub distance: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub battery_cost: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub confidence: f64,

}



impl Default for TaskBid {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::TaskBid::default())
  }
}

impl rosidl_runtime_rs::Message for TaskBid {
  type RmwMsg = super::msg::rmw::TaskBid;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        robot_id: msg.robot_id.as_str().into(),
        task_id: msg.task_id.as_str().into(),
        estimated_time: msg.estimated_time,
        distance: msg.distance,
        battery_cost: msg.battery_cost,
        confidence: msg.confidence,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        robot_id: msg.robot_id.as_str().into(),
        task_id: msg.task_id.as_str().into(),
      estimated_time: msg.estimated_time,
      distance: msg.distance,
      battery_cost: msg.battery_cost,
      confidence: msg.confidence,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      robot_id: msg.robot_id.to_string(),
      task_id: msg.task_id.to_string(),
      estimated_time: msg.estimated_time,
      distance: msg.distance,
      battery_cost: msg.battery_cost,
      confidence: msg.confidence,
    }
  }
}


// Corresponds to fleet_msgs__msg__Heartbeat

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Heartbeat {

    // This member is not documented.
    #[allow(missing_docs)]
    pub robot_id: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub timestamp: f64,

}



impl Default for Heartbeat {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Heartbeat::default())
  }
}

impl rosidl_runtime_rs::Message for Heartbeat {
  type RmwMsg = super::msg::rmw::Heartbeat;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        robot_id: msg.robot_id.as_str().into(),
        timestamp: msg.timestamp,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        robot_id: msg.robot_id.as_str().into(),
      timestamp: msg.timestamp,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      robot_id: msg.robot_id.to_string(),
      timestamp: msg.timestamp,
    }
  }
}


