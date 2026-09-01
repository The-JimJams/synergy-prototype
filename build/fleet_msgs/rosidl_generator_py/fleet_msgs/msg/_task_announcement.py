# generated from rosidl_generator_py/resource/_idl.py.em
# with input from fleet_msgs:msg/TaskAnnouncement.idl
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


class Metaclass_TaskAnnouncement(rosidl_pycommon.interface_base_classes.MessageTypeSupportMeta):
    """Metaclass of message 'TaskAnnouncement'."""

    _CREATE_ROS_MESSAGE: typing.ClassVar[typing.Optional[PyCapsule]] = None
    _CONVERT_FROM_PY: typing.ClassVar[typing.Optional[PyCapsule]] = None
    _CONVERT_TO_PY: typing.ClassVar[typing.Optional[PyCapsule]] = None
    _DESTROY_ROS_MESSAGE: typing.ClassVar[typing.Optional[PyCapsule]] = None
    _TYPE_SUPPORT: typing.ClassVar[typing.Optional[PyCapsule]] = None

    class TaskAnnouncementConstants(typing.TypedDict):
        pass

    __constants: TaskAnnouncementConstants = {
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
                'fleet_msgs.msg.TaskAnnouncement')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__task_announcement
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__task_announcement
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__task_announcement
            cls._TYPE_SUPPORT = module.type_support_msg__msg__task_announcement
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__task_announcement

    @classmethod
    def __prepare__(metacls, name: str, bases: tuple[type[typing.Any], ...], /, **kwds: typing.Any) -> collections.abc.MutableMapping[str, object]:
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class TaskAnnouncement(rosidl_pycommon.interface_base_classes.BaseMessage, metaclass=Metaclass_TaskAnnouncement):
    """Message class 'TaskAnnouncement'."""

    __slots__ = [
        '_task_id',
        '_pickup',
        '_dropoff',
        '_deadline',
        '_priority',
        '_capability_requirements',
        '_check_fields',
    ]

    _fields_and_field_types: dict[str, str] = {
        'task_id': 'string',
        'pickup': 'string',
        'dropoff': 'string',
        'deadline': 'double',
        'priority': 'int32',
        'capability_requirements': 'sequence<string>',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES: tuple[rosidl_parser.definition.AbstractType, ...] = (
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('int32'),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.UnboundedString()),  # noqa: E501
    )

    def __init__(self, *,
                 task_id: typing.Optional[str] = None,  # noqa: E501
                 pickup: typing.Optional[str] = None,  # noqa: E501
                 dropoff: typing.Optional[str] = None,  # noqa: E501
                 deadline: typing.Optional[float] = None,  # noqa: E501
                 priority: typing.Optional[int] = None,  # noqa: E501
                 capability_requirements: typing.Optional[collections.abc.Sequence[str]] = None,  # noqa: E501
                 check_fields: typing.Optional[bool] = None) -> None:
        if check_fields is not None:
            self._check_fields = check_fields
        else:
            self._check_fields = ros_python_check_fields == '1'
        self.task_id = task_id if task_id is not None else str()
        self.pickup = pickup if pickup is not None else str()
        self.dropoff = dropoff if dropoff is not None else str()
        self.deadline = deadline if deadline is not None else float()
        self.priority = priority if priority is not None else int()
        self.capability_requirements = capability_requirements if capability_requirements is not None else []

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
        if not isinstance(other, TaskAnnouncement):
            return False
        if self.task_id != other.task_id:
            return False
        if self.pickup != other.pickup:
            return False
        if self.dropoff != other.dropoff:
            return False
        if self.deadline != other.deadline:
            return False
        if self.priority != other.priority:
            return False
        if self.capability_requirements != other.capability_requirements:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls) -> dict[str, str]:
        from copy import copy
        return copy(cls._fields_and_field_types)

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
    def pickup(self) -> str:
        """Message field 'pickup'."""
        return self._pickup

    @pickup.setter
    def pickup(self, value: str) -> None:

        if self._check_fields:
            if False:  # Done for templating alignment
                pass
            else:
                assert \
                    isinstance(value, str), \
                    "The 'pickup' field must be of type 'str'"

        self._pickup = value

    @builtins.property
    def dropoff(self) -> str:
        """Message field 'dropoff'."""
        return self._dropoff

    @dropoff.setter
    def dropoff(self, value: str) -> None:

        if self._check_fields:
            if False:  # Done for templating alignment
                pass
            else:
                assert \
                    isinstance(value, str), \
                    "The 'dropoff' field must be of type 'str'"

        self._dropoff = value

    @builtins.property
    def deadline(self) -> float:
        """Message field 'deadline'."""
        return self._deadline

    @deadline.setter
    def deadline(self, value: float) -> None:

        if self._check_fields:
            if False:  # Done for templating alignment
                pass
            else:
                assert \
                    isinstance(value, float), \
                    "The 'deadline' field must be of type 'float'"
                assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                    "The 'deadline' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"

        self._deadline = value

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
    def capability_requirements(self) -> typing.Annotated[typing.Any, list[str]]:   # typing.Annotated can be remove after mypy 1.16+ see mypy#3004
        """Message field 'capability_requirements'."""
        return self._capability_requirements

    @capability_requirements.setter
    def capability_requirements(self, value: collections.abc.Sequence[str]) -> None:
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
                    "The 'capability_requirements' field must be sequence and each value of type 'str'"

        if isinstance(value, list):
            self._capability_requirements = value
            return
        self._capability_requirements = list(value)
