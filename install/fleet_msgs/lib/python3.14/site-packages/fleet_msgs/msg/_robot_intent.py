# generated from rosidl_generator_py/resource/_idl.py.em
# with input from fleet_msgs:msg/RobotIntent.idl
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


class Metaclass_RobotIntent(rosidl_pycommon.interface_base_classes.MessageTypeSupportMeta):
    """Metaclass of message 'RobotIntent'."""

    _CREATE_ROS_MESSAGE: typing.ClassVar[typing.Optional[PyCapsule]] = None
    _CONVERT_FROM_PY: typing.ClassVar[typing.Optional[PyCapsule]] = None
    _CONVERT_TO_PY: typing.ClassVar[typing.Optional[PyCapsule]] = None
    _DESTROY_ROS_MESSAGE: typing.ClassVar[typing.Optional[PyCapsule]] = None
    _TYPE_SUPPORT: typing.ClassVar[typing.Optional[PyCapsule]] = None

    class RobotIntentConstants(typing.TypedDict):
        pass

    __constants: RobotIntentConstants = {
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
                'fleet_msgs.msg.RobotIntent')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__robot_intent
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__robot_intent
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__robot_intent
            cls._TYPE_SUPPORT = module.type_support_msg__msg__robot_intent
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__robot_intent

    @classmethod
    def __prepare__(metacls, name: str, bases: tuple[type[typing.Any], ...], /, **kwds: typing.Any) -> collections.abc.MutableMapping[str, object]:
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class RobotIntent(rosidl_pycommon.interface_base_classes.BaseMessage, metaclass=Metaclass_RobotIntent):
    """Message class 'RobotIntent'."""

    __slots__ = [
        '_robot_id',
        '_planned_path',
        '_target_intersection',
        '_eta',
        '_priority',
        '_task_id',
        '_check_fields',
    ]

    _fields_and_field_types: dict[str, str] = {
        'robot_id': 'string',
        'planned_path': 'sequence<string>',
        'target_intersection': 'string',
        'eta': 'double',
        'priority': 'int32',
        'task_id': 'string',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES: tuple[rosidl_parser.definition.AbstractType, ...] = (
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.UnboundedString()),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('int32'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
    )

    def __init__(self, *,
                 robot_id: typing.Optional[str] = None,  # noqa: E501
                 planned_path: typing.Optional[collections.abc.Sequence[str]] = None,  # noqa: E501
                 target_intersection: typing.Optional[str] = None,  # noqa: E501
                 eta: typing.Optional[float] = None,  # noqa: E501
                 priority: typing.Optional[int] = None,  # noqa: E501
                 task_id: typing.Optional[str] = None,  # noqa: E501
                 check_fields: typing.Optional[bool] = None) -> None:
        if check_fields is not None:
            self._check_fields = check_fields
        else:
            self._check_fields = ros_python_check_fields == '1'
        self.robot_id = robot_id if robot_id is not None else str()
        self.planned_path = planned_path if planned_path is not None else []
        self.target_intersection = target_intersection if target_intersection is not None else str()
        self.eta = eta if eta is not None else float()
        self.priority = priority if priority is not None else int()
        self.task_id = task_id if task_id is not None else str()

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
        if not isinstance(other, RobotIntent):
            return False
        if self.robot_id != other.robot_id:
            return False
        if self.planned_path != other.planned_path:
            return False
        if self.target_intersection != other.target_intersection:
            return False
        if self.eta != other.eta:
            return False
        if self.priority != other.priority:
            return False
        if self.task_id != other.task_id:
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
    def planned_path(self) -> typing.Annotated[typing.Any, list[str]]:   # typing.Annotated can be remove after mypy 1.16+ see mypy#3004
        """Message field 'planned_path'."""
        return self._planned_path

    @planned_path.setter
    def planned_path(self, value: collections.abc.Sequence[str]) -> None:
        if isinstance(value, collections.abc.Set):
            import warnings
            warnings.warn(
                'Using set or subclass of set is deprecated,'
                ' please use a subclass of collections.abc.Sequence like list',
                DeprecationWarning)

        if self._check_fields:
            if False:  # Done for templating alignment
                pass
            else:
                assert \
                    ((isinstance(value, collections.abc.Sequence) or
                     isinstance(value, collections.abc.Set)) and
                     not isinstance(value, str) and
                     not isinstance(value, collections.UserString) and
                     all(isinstance(v, str) for v in value) and
                     True), \
                    "The 'planned_path' field must be sequence and each value of type 'str'"

        if isinstance(value, list):
            self._planned_path = value
            return
        self._planned_path = list(value)

    @builtins.property
    def target_intersection(self) -> str:
        """Message field 'target_intersection'."""
        return self._target_intersection

    @target_intersection.setter
    def target_intersection(self, value: str) -> None:

        if self._check_fields:
            if False:  # Done for templating alignment
                pass
            else:
                assert \
                    isinstance(value, str), \
                    "The 'target_intersection' field must be of type 'str'"

        self._target_intersection = value

    @builtins.property
    def eta(self) -> float:
        """Message field 'eta'."""
        return self._eta

    @eta.setter
    def eta(self, value: float) -> None:

        if self._check_fields:
            if False:  # Done for templating alignment
                pass
            else:
                assert \
                    isinstance(value, float), \
                    "The 'eta' field must be of type 'float'"
                assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                    "The 'eta' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"

        self._eta = value

    @builtins.property
    def priority(self) -> int:
        """Message field 'priority'."""
        return self._priority

    @priority.setter
    def priority(self, value: int) -> None:

        if self._check_fields:
            if False:  # Done for templating alignment
                pass
            else:
                assert \
                    isinstance(value, int), \
                    "The 'priority' field must be of type 'int'"
                assert value >= -2147483648 and value < 2147483648, \
                    "The 'priority' field must be an integer in [-2147483648, 2147483647]"

        self._priority = value

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
