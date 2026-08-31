# generated from rosidl_generator_py/resource/_idl.py.em
# with input from fleet_msgs:msg/TaskBid.idl
# generated code does not contain a copyright notice

from __future__ import annotations

import collections.abc
import os
import typing

import rosidl_pycommon.interface_base_classes

if typing.TYPE_CHECKING:
    from ctypes import Structure

    class PyCapsule(Structure):
        pass  # don't need to define the full structure


# This is being done at the module level and not on the instance level to avoid looking
# for the same variable multiple times on each instance. This variable is not supposed to
# change during runtime so it makes sense to only look for it once.
ros_python_check_fields = os.getenv('ROS_PYTHON_CHECK_FIELDS', default='')


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_TaskBid(rosidl_pycommon.interface_base_classes.MessageTypeSupportMeta):
    """Metaclass of message 'TaskBid'."""

    _CREATE_ROS_MESSAGE: typing.ClassVar[typing.Optional[PyCapsule]] = None
    _CONVERT_FROM_PY: typing.ClassVar[typing.Optional[PyCapsule]] = None
    _CONVERT_TO_PY: typing.ClassVar[typing.Optional[PyCapsule]] = None
    _DESTROY_ROS_MESSAGE: typing.ClassVar[typing.Optional[PyCapsule]] = None
    _TYPE_SUPPORT: typing.ClassVar[typing.Optional[PyCapsule]] = None

    class TaskBidConstants(typing.TypedDict):
        pass

    __constants: TaskBidConstants = {
    }

    @classmethod
    def __import_type_support__(cls) -> None:
        try:
            from rosidl_generator_py import import_type_support  # type: ignore[attr-defined]
            module = import_type_support('fleet_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'fleet_msgs.msg.TaskBid')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__task_bid
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__task_bid
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__task_bid
            cls._TYPE_SUPPORT = module.type_support_msg__msg__task_bid
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__task_bid

    @classmethod
    def __prepare__(metacls, name: str, bases: tuple[type[typing.Any], ...], /, **kwds: typing.Any) -> collections.abc.MutableMapping[str, object]:
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class TaskBid(rosidl_pycommon.interface_base_classes.BaseMessage, metaclass=Metaclass_TaskBid):
    """Message class 'TaskBid'."""

    __slots__ = [
        '_robot_id',
        '_task_id',
        '_estimated_time',
        '_distance',
        '_battery_cost',
        '_confidence',
        '_check_fields',
    ]

    _fields_and_field_types: dict[str, str] = {
        'robot_id': 'string',
        'task_id': 'string',
        'estimated_time': 'double',
        'distance': 'double',
        'battery_cost': 'double',
        'confidence': 'double',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES: tuple[rosidl_parser.definition.AbstractType, ...] = (
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
    )

    def __init__(self, *,
                 robot_id: typing.Optional[str] = None,  # noqa: E501
                 task_id: typing.Optional[str] = None,  # noqa: E501
                 estimated_time: typing.Optional[float] = None,  # noqa: E501
                 distance: typing.Optional[float] = None,  # noqa: E501
                 battery_cost: typing.Optional[float] = None,  # noqa: E501
                 confidence: typing.Optional[float] = None,  # noqa: E501
                 check_fields: typing.Optional[bool] = None) -> None:
        if check_fields is not None:
            self._check_fields = check_fields
        else:
            self._check_fields = ros_python_check_fields == '1'
        self.robot_id = robot_id if robot_id is not None else str()
        self.task_id = task_id if task_id is not None else str()
        self.estimated_time = estimated_time if estimated_time is not None else float()
        self.distance = distance if distance is not None else float()
        self.battery_cost = battery_cost if battery_cost is not None else float()
        self.confidence = confidence if confidence is not None else float()

    def __repr__(self) -> str:
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args: list[str] = []
        for s, t in zip(self.get_fields_and_field_types().keys(), self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    from rosidl_buffer import Buffer as _RosidlBuffer
                    if not isinstance(field, _RosidlBuffer):
                        if self._check_fields:
                            assert fieldstr.startswith('array(')
                        prefix = "array('X', "
                        suffix = ')'
                        fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TaskBid):
            return False
        if self.robot_id != other.robot_id:
            return False
        if self.task_id != other.task_id:
            return False
        if self.estimated_time != other.estimated_time:
            return False
        if self.distance != other.distance:
            return False
        if self.battery_cost != other.battery_cost:
            return False
        if self.confidence != other.confidence:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls) -> dict[str, str]:
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def robot_id(self) -> str:
        """Message field 'robot_id'."""
        return self._robot_id

    @robot_id.setter
    def robot_id(self, value: str) -> None:

        if self._check_fields:
            if False:  # Done for templating alignment
                pass
            else:
                assert \
                    isinstance(value, str), \
                    "The 'robot_id' field must be of type 'str'"

        self._robot_id = value

    @builtins.property
    def task_id(self) -> str:
        """Message field 'task_id'."""
        return self._task_id

    @task_id.setter
    def task_id(self, value: str) -> None:

        if self._check_fields:
            if False:  # Done for templating alignment
                pass
            else:
                assert \
                    isinstance(value, str), \
                    "The 'task_id' field must be of type 'str'"

        self._task_id = value

    @builtins.property
    def estimated_time(self) -> float:
        """Message field 'estimated_time'."""
        return self._estimated_time

    @estimated_time.setter
    def estimated_time(self, value: float) -> None:

        if self._check_fields:
            if False:  # Done for templating alignment
                pass
            else:
                assert \
                    isinstance(value, float), \
                    "The 'estimated_time' field must be of type 'float'"
                assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                    "The 'estimated_time' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"

        self._estimated_time = value

    @builtins.property
    def distance(self) -> float:
        """Message field 'distance'."""
        return self._distance

    @distance.setter
    def distance(self, value: float) -> None:

        if self._check_fields:
            if False:  # Done for templating alignment
                pass
            else:
                assert \
                    isinstance(value, float), \
                    "The 'distance' field must be of type 'float'"
                assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                    "The 'distance' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"

        self._distance = value

    @builtins.property
    def battery_cost(self) -> float:
        """Message field 'battery_cost'."""
        return self._battery_cost

    @battery_cost.setter
    def battery_cost(self, value: float) -> None:

        if self._check_fields:
            if False:  # Done for templating alignment
                pass
            else:
                assert \
                    isinstance(value, float), \
                    "The 'battery_cost' field must be of type 'float'"
                assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                    "The 'battery_cost' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"

        self._battery_cost = value

    @builtins.property
    def confidence(self) -> float:
        """Message field 'confidence'."""
        return self._confidence

    @confidence.setter
    def confidence(self, value: float) -> None:

        if self._check_fields:
            if False:  # Done for templating alignment
                pass
            else:
                assert \
                    isinstance(value, float), \
                    "The 'confidence' field must be of type 'float'"
                assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                    "The 'confidence' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"

        self._confidence = value
