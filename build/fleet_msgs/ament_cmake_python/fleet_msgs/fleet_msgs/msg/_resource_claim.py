# generated from rosidl_generator_py/resource/_idl.py.em
# with input from fleet_msgs:msg/ResourceClaim.idl
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


class Metaclass_ResourceClaim(rosidl_pycommon.interface_base_classes.MessageTypeSupportMeta):
    """Metaclass of message 'ResourceClaim'."""

    _CREATE_ROS_MESSAGE: typing.ClassVar[typing.Optional[PyCapsule]] = None
    _CONVERT_FROM_PY: typing.ClassVar[typing.Optional[PyCapsule]] = None
    _CONVERT_TO_PY: typing.ClassVar[typing.Optional[PyCapsule]] = None
    _DESTROY_ROS_MESSAGE: typing.ClassVar[typing.Optional[PyCapsule]] = None
    _TYPE_SUPPORT: typing.ClassVar[typing.Optional[PyCapsule]] = None

    class ResourceClaimConstants(typing.TypedDict):
        pass

    __constants: ResourceClaimConstants = {
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
                'fleet_msgs.msg.ResourceClaim')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__resource_claim
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__resource_claim
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__resource_claim
            cls._TYPE_SUPPORT = module.type_support_msg__msg__resource_claim
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__resource_claim

    @classmethod
    def __prepare__(metacls, name: str, bases: tuple[type[typing.Any], ...], /, **kwds: typing.Any) -> collections.abc.MutableMapping[str, object]:
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class ResourceClaim(rosidl_pycommon.interface_base_classes.BaseMessage, metaclass=Metaclass_ResourceClaim):
    """Message class 'ResourceClaim'."""

    __slots__ = [
        '_robot_id',
        '_resource',
        '_start_time',
        '_end_time',
        '_priority',
        '_claim_id',
        '_status',
        '_check_fields',
    ]

    _fields_and_field_types: dict[str, str] = {
        'robot_id': 'string',
        'resource': 'string',
        'start_time': 'double',
        'end_time': 'double',
        'priority': 'int32',
        'claim_id': 'string',
        'status': 'string',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES: tuple[rosidl_parser.definition.AbstractType, ...] = (
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('int32'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
    )

    def __init__(self, *,
                 robot_id: typing.Optional[str] = None,  # noqa: E501
                 resource: typing.Optional[str] = None,  # noqa: E501
                 start_time: typing.Optional[float] = None,  # noqa: E501
                 end_time: typing.Optional[float] = None,  # noqa: E501
                 priority: typing.Optional[int] = None,  # noqa: E501
                 claim_id: typing.Optional[str] = None,  # noqa: E501
                 status: typing.Optional[str] = None,  # noqa: E501
                 check_fields: typing.Optional[bool] = None) -> None:
        if check_fields is not None:
            self._check_fields = check_fields
        else:
            self._check_fields = ros_python_check_fields == '1'
        self.robot_id = robot_id if robot_id is not None else str()
        self.resource = resource if resource is not None else str()
        self.start_time = start_time if start_time is not None else float()
        self.end_time = end_time if end_time is not None else float()
        self.priority = priority if priority is not None else int()
        self.claim_id = claim_id if claim_id is not None else str()
        self.status = status if status is not None else str()

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
        if not isinstance(other, ResourceClaim):
            return False
        if self.robot_id != other.robot_id:
            return False
        if self.resource != other.resource:
            return False
        if self.start_time != other.start_time:
            return False
        if self.end_time != other.end_time:
            return False
        if self.priority != other.priority:
            return False
        if self.claim_id != other.claim_id:
            return False
        if self.status != other.status:
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
    def resource(self) -> str:
        """Message field 'resource'."""
        return self._resource

    @resource.setter
    def resource(self, value: str) -> None:

        if self._check_fields:
            if False:  # Done for templating alignment
                pass
            else:
                assert \
                    isinstance(value, str), \
                    "The 'resource' field must be of type 'str'"

        self._resource = value

    @builtins.property
    def start_time(self) -> float:
        """Message field 'start_time'."""
        return self._start_time

    @start_time.setter
    def start_time(self, value: float) -> None:

        if self._check_fields:
            if False:  # Done for templating alignment
                pass
            else:
                assert \
                    isinstance(value, float), \
                    "The 'start_time' field must be of type 'float'"
                assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                    "The 'start_time' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"

        self._start_time = value

    @builtins.property
    def end_time(self) -> float:
        """Message field 'end_time'."""
        return self._end_time

    @end_time.setter
    def end_time(self, value: float) -> None:

        if self._check_fields:
            if False:  # Done for templating alignment
                pass
            else:
                assert \
                    isinstance(value, float), \
                    "The 'end_time' field must be of type 'float'"
                assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                    "The 'end_time' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"

        self._end_time = value

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
    def claim_id(self) -> str:
        """Message field 'claim_id'."""
        return self._claim_id

    @claim_id.setter
    def claim_id(self, value: str) -> None:

        if self._check_fields:
            if False:  # Done for templating alignment
                pass
            else:
                assert \
                    isinstance(value, str), \
                    "The 'claim_id' field must be of type 'str'"

        self._claim_id = value

    @builtins.property
    def status(self) -> str:
        """Message field 'status'."""
        return self._status

    @status.setter
    def status(self, value: str) -> None:

        if self._check_fields:
            if False:  # Done for templating alignment
                pass
            else:
                assert \
                    isinstance(value, str), \
                    "The 'status' field must be of type 'str'"

        self._status = value
