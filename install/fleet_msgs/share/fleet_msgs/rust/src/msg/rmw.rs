#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "fleet_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__fleet_msgs__msg__RobotState() -> *const std::ffi::c_void;
}

#[link(name = "fleet_msgs__rosidl_generator_c")]
extern "C" {
    fn fleet_msgs__msg__RobotState__init(msg: *mut RobotState) -> bool;
    fn fleet_msgs__msg__RobotState__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<RobotState>, size: usize) -> bool;
    fn fleet_msgs__msg__RobotState__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<RobotState>);
    fn fleet_msgs__msg__RobotState__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<RobotState>, out_seq: *mut rosidl_runtime_rs::Sequence<RobotState>) -> bool;
}

// Corresponds to fleet_msgs__msg__RobotState
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct RobotState {

    // This member is not documented.
    #[allow(missing_docs)]
    pub robot_id: rosidl_runtime_rs::String,


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
    pub current_task: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub status: rosidl_runtime_rs::String,

}



impl Default for RobotState {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !fleet_msgs__msg__RobotState__init(&mut msg as *mut _) {
        panic!("Call to fleet_msgs__msg__RobotState__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for RobotState {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fleet_msgs__msg__RobotState__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fleet_msgs__msg__RobotState__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fleet_msgs__msg__RobotState__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for RobotState {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for RobotState where Self: Sized {
  const TYPE_NAME: &'static str = "fleet_msgs/msg/RobotState";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__fleet_msgs__msg__RobotState() }
  }
}


#[link(name = "fleet_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__fleet_msgs__msg__RobotIntent() -> *const std::ffi::c_void;
}

#[link(name = "fleet_msgs__rosidl_generator_c")]
extern "C" {
    fn fleet_msgs__msg__RobotIntent__init(msg: *mut RobotIntent) -> bool;
    fn fleet_msgs__msg__RobotIntent__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<RobotIntent>, size: usize) -> bool;
    fn fleet_msgs__msg__RobotIntent__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<RobotIntent>);
    fn fleet_msgs__msg__RobotIntent__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<RobotIntent>, out_seq: *mut rosidl_runtime_rs::Sequence<RobotIntent>) -> bool;
}

// Corresponds to fleet_msgs__msg__RobotIntent
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct RobotIntent {

    // This member is not documented.
    #[allow(missing_docs)]
    pub robot_id: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub planned_path: rosidl_runtime_rs::Sequence<rosidl_runtime_rs::String>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub target_intersection: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub eta: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub priority: i32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub task_id: rosidl_runtime_rs::String,

}



impl Default for RobotIntent {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !fleet_msgs__msg__RobotIntent__init(&mut msg as *mut _) {
        panic!("Call to fleet_msgs__msg__RobotIntent__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for RobotIntent {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fleet_msgs__msg__RobotIntent__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fleet_msgs__msg__RobotIntent__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fleet_msgs__msg__RobotIntent__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for RobotIntent {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for RobotIntent where Self: Sized {
  const TYPE_NAME: &'static str = "fleet_msgs/msg/RobotIntent";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__fleet_msgs__msg__RobotIntent() }
  }
}


#[link(name = "fleet_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__fleet_msgs__msg__ResourceClaim() -> *const std::ffi::c_void;
}

#[link(name = "fleet_msgs__rosidl_generator_c")]
extern "C" {
    fn fleet_msgs__msg__ResourceClaim__init(msg: *mut ResourceClaim) -> bool;
    fn fleet_msgs__msg__ResourceClaim__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ResourceClaim>, size: usize) -> bool;
    fn fleet_msgs__msg__ResourceClaim__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ResourceClaim>);
    fn fleet_msgs__msg__ResourceClaim__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ResourceClaim>, out_seq: *mut rosidl_runtime_rs::Sequence<ResourceClaim>) -> bool;
}

// Corresponds to fleet_msgs__msg__ResourceClaim
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ResourceClaim {

    // This member is not documented.
    #[allow(missing_docs)]
    pub robot_id: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub resource: rosidl_runtime_rs::String,


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
    pub claim_id: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub status: rosidl_runtime_rs::String,

}



impl Default for ResourceClaim {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !fleet_msgs__msg__ResourceClaim__init(&mut msg as *mut _) {
        panic!("Call to fleet_msgs__msg__ResourceClaim__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ResourceClaim {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fleet_msgs__msg__ResourceClaim__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fleet_msgs__msg__ResourceClaim__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fleet_msgs__msg__ResourceClaim__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ResourceClaim {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ResourceClaim where Self: Sized {
  const TYPE_NAME: &'static str = "fleet_msgs/msg/ResourceClaim";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__fleet_msgs__msg__ResourceClaim() }
  }
}


#[link(name = "fleet_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__fleet_msgs__msg__TaskAnnouncement() -> *const std::ffi::c_void;
}

#[link(name = "fleet_msgs__rosidl_generator_c")]
extern "C" {
    fn fleet_msgs__msg__TaskAnnouncement__init(msg: *mut TaskAnnouncement) -> bool;
    fn fleet_msgs__msg__TaskAnnouncement__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<TaskAnnouncement>, size: usize) -> bool;
    fn fleet_msgs__msg__TaskAnnouncement__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<TaskAnnouncement>);
    fn fleet_msgs__msg__TaskAnnouncement__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<TaskAnnouncement>, out_seq: *mut rosidl_runtime_rs::Sequence<TaskAnnouncement>) -> bool;
}

// Corresponds to fleet_msgs__msg__TaskAnnouncement
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TaskAnnouncement {

    // This member is not documented.
    #[allow(missing_docs)]
    pub task_id: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub pickup: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub dropoff: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub deadline: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub priority: i32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub capability_requirements: rosidl_runtime_rs::Sequence<rosidl_runtime_rs::String>,

}



impl Default for TaskAnnouncement {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !fleet_msgs__msg__TaskAnnouncement__init(&mut msg as *mut _) {
        panic!("Call to fleet_msgs__msg__TaskAnnouncement__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for TaskAnnouncement {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fleet_msgs__msg__TaskAnnouncement__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fleet_msgs__msg__TaskAnnouncement__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fleet_msgs__msg__TaskAnnouncement__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for TaskAnnouncement {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for TaskAnnouncement where Self: Sized {
  const TYPE_NAME: &'static str = "fleet_msgs/msg/TaskAnnouncement";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__fleet_msgs__msg__TaskAnnouncement() }
  }
}


#[link(name = "fleet_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__fleet_msgs__msg__TaskBid() -> *const std::ffi::c_void;
}

#[link(name = "fleet_msgs__rosidl_generator_c")]
extern "C" {
    fn fleet_msgs__msg__TaskBid__init(msg: *mut TaskBid) -> bool;
    fn fleet_msgs__msg__TaskBid__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<TaskBid>, size: usize) -> bool;
    fn fleet_msgs__msg__TaskBid__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<TaskBid>);
    fn fleet_msgs__msg__TaskBid__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<TaskBid>, out_seq: *mut rosidl_runtime_rs::Sequence<TaskBid>) -> bool;
}

// Corresponds to fleet_msgs__msg__TaskBid
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TaskBid {

    // This member is not documented.
    #[allow(missing_docs)]
    pub robot_id: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub task_id: rosidl_runtime_rs::String,


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
    unsafe {
      let mut msg = std::mem::zeroed();
      if !fleet_msgs__msg__TaskBid__init(&mut msg as *mut _) {
        panic!("Call to fleet_msgs__msg__TaskBid__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for TaskBid {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fleet_msgs__msg__TaskBid__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fleet_msgs__msg__TaskBid__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fleet_msgs__msg__TaskBid__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for TaskBid {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for TaskBid where Self: Sized {
  const TYPE_NAME: &'static str = "fleet_msgs/msg/TaskBid";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__fleet_msgs__msg__TaskBid() }
  }
}


#[link(name = "fleet_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__fleet_msgs__msg__Heartbeat() -> *const std::ffi::c_void;
}

#[link(name = "fleet_msgs__rosidl_generator_c")]
extern "C" {
    fn fleet_msgs__msg__Heartbeat__init(msg: *mut Heartbeat) -> bool;
    fn fleet_msgs__msg__Heartbeat__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Heartbeat>, size: usize) -> bool;
    fn fleet_msgs__msg__Heartbeat__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Heartbeat>);
    fn fleet_msgs__msg__Heartbeat__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Heartbeat>, out_seq: *mut rosidl_runtime_rs::Sequence<Heartbeat>) -> bool;
}

// Corresponds to fleet_msgs__msg__Heartbeat
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Heartbeat {

    // This member is not documented.
    #[allow(missing_docs)]
    pub robot_id: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub timestamp: f64,

}



impl Default for Heartbeat {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !fleet_msgs__msg__Heartbeat__init(&mut msg as *mut _) {
        panic!("Call to fleet_msgs__msg__Heartbeat__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Heartbeat {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fleet_msgs__msg__Heartbeat__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fleet_msgs__msg__Heartbeat__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { fleet_msgs__msg__Heartbeat__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Heartbeat {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Heartbeat where Self: Sized {
  const TYPE_NAME: &'static str = "fleet_msgs/msg/Heartbeat";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__fleet_msgs__msg__Heartbeat() }
  }
}


