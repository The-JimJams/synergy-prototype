# generated from rosidl_generator_py/resource/_idl.py.em
# with input from fleet_msgs:msg/RobotState.idl
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


if typing.TYPE_CHECKING:
    import numpy.typing  # noqa: E402, I100, I201, I300


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

# Member 'position'
import numpy  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_RobotState(rosidl_pycommon.interface_base_classes.MessageTypeSupportMeta):
    """Metaclass of message 'RobotState'."""

    _CREATE_ROS_MESSAGE: typing.ClassVar[typing.Optional[PyCapsule]] = None
    _CONVERT_FROM_PY: typing.ClassVar[typing.Optional[PyCapsule]] = None
    _CONVERT_TO_PY: typing.ClassVar[typing.Optional[PyCapsule]] = None
    _DESTROY_ROS_MESSAGE: typing.ClassVar[typing.Optional[PyCapsule]] = None
    _TYPE_SUPPORT: typing.ClassVar[typing.Optional[PyCapsule]] = None

    class RobotStateConstants(typing.TypedDict):
        pass

    __constants: RobotStateConstants = {
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
                'fleet_msgs.msg.RobotState')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__robot_state
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__robot_state
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__robot_state
            cls._TYPE_SUPPORT = module.type_support_msg__msg__robot_state
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__robot_state

    @classmethod
    def __prepare__(metacls, name: str, bases: tuple[type[typing.Any], ...], /, **kwds: typing.Any) -> collections.abc.MutableMapping[str, object]:
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class RobotState(rosidl_pycommon.interface_base_classes.BaseMessage, metaclass=Metaclass_RobotState):
    """Message class 'RobotState'."""

    __slots__ = [
        '_robot_id',
        '_timestamp',
        '_position',
        '_velocity',
        '_battery',
        '_current_task',
        '_status',
        '_check_fields',
    ]

    _fields_and_field_types: dict[str, str] = {
        'robot_id': 'string',
        'timestamp': 'double',
        'position': 'double[2]',
        'velocity': 'double',
        'battery': 'double',
        'current_task': 'string',
        'status': 'string',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES: tuple[rosidl_parser.definition.AbstractType, ...] = (
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.Array(rosidl_parser.definition.BasicType('double'), 2),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
    )

    def __init__(self, *,
                 robot_id: typing.Optional[str] = None,  # noqa: E501
                 timestamp: typing.Optional[float] = None,  # noqa: E501
                 position: typing.Optional[typing.Union[numpy.typing.NDArray[numpy.float64], collections.abc.Sequence[float]]] = None,  # noqa: E501
                 velocity: typing.Optional[float] = None,  # noqa: E501
                 battery: typing.Optional[float] = None,  # noqa: E501
                 current_task: typing.Optional[str] = None,  # noqa: E501
                 status: typing.Optional[str] = None,  # noqa: E501
                 check_fields: typing.Optional[bool] = None) -> None:
        if check_fields is not None:
            self._check_fields = check_fields
        else:
            self._check_fields = ros_python_check_fields == '1'
        self.robot_id = robot_id if robot_id is not None else str()
        self.timestamp = timestamp if timestamp is not None else float()
        if position is None:
            self.position = numpy.zeros(2, dtype=numpy.float64)
        else:
            self.position = position
        self.velocity = velocity if velocity is not None else float()
        self.battery = battery if battery is not None else float()
        self.current_task = current_task if current_task is not None else str()
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
        if not isinstance(other, RobotState):
            return False
        if self.robot_id != other.robot_id:
            return False
        if self.timestamp != other.timestamp:
            return False
        if any(self.position != other.position):
            return False
        if self.velocity != other.velocity:
            return False
        if self.battery != other.battery:
            return False
        if self.current_task != other.current_task:
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
    def timestamp(self) -> float:
        """Message field 'timestamp'."""
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: float) -> None:

        if self._check_fields:
            if False:  # Done for templating alignment
                pass
            else:
                assert \
                    isinstance(value, float), \
                    "The 'timestamp' field must be of type 'float'"
                assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                    "The 'timestamp' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"

        self._timestamp = value

    @builtins.property
    def position(self) -> typing.Annotated[typing.Any, numpy.typing.NDArray[numpy.float64]]:   # typing.Annotated can be remove after mypy 1.16+ see mypy#3004
        """Message field 'position'."""
        return self._position

    @position.setter
    def position(self, value: typing.Union[numpy.typing.NDArray[numpy.float64], collections.abc.Sequence[float]]) -> None:
        if isinstance(value, collections.abc.Set):
            import warnings
            warnings.warn(
                'Using set or subclass of set is deprecated,'
                ' please use a subclass of collections.abc.Sequence like list',
                DeprecationWarning)

        if self._check_fields:
            if isinstance(value, numpy.ndarray):
                assert value.dtype == numpy.float64, \
                    "The 'position' numpy.ndarray() must have the dtype of 'numpy.float64'"
                assert value.size == 2, \
                    "The 'position' numpy.ndarray() must have a size of 2"
            else:
                assert \
                    ((isinstance(value, collections.abc.Sequence) or
                     isinstance(value, collections.abc.Set)) and
                     not isinstance(value, str) and
                     not isinstance(value, collections.UserString) and
                     len(value) == 2 and
                     all(isinstance(v, float) for v in value) and
                     all(not (val < -1.7976931348623157e+308 or val > 1.7976931348623157e+308) or math.isinf(val) for val in value)), \
                    "The 'position' field must be sequence with length 2 and each value of type 'float' and each double in [-179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368.000000, 179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368.000000]"

        if isinstance(value, numpy.ndarray):
            self._position = value
            return
        self._position = numpy.array(value, dtype=numpy.float64)

    @builtins.property
    def velocity(self) -> float:
        """Message field 'velocity'."""
        return self._velocity

    @velocity.setter
    def velocity(self, value: float) -> None:

        if self._check_fields:
            if False:  # Done for templating alignment
                pass
            else:
                assert \
                    isinstance(value, float), \
                    "The 'velocity' field must be of type 'float'"
                assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                    "The 'velocity' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"

        self._velocity = value

    @builtins.property
    def battery(self) -> float:
        """Message field 'battery'."""
        return self._battery

    @battery.setter
    def battery(self, value: float) -> None:

        if self._check_fields:
            if False:  # Done for templating alignment
                pass
            else:
                assert \
                    isinstance(value, float), \
                    "The 'battery' field must be of type 'float'"
                assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                    "The 'battery' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"

        self._battery = value

    @builtins.property
    def current_task(self) -> str:
        """Message field 'current_task'."""
        return self._current_task

    @current_task.setter
    def current_task(self, value: str) -> None:

        if self._check_fields:
            if False:  # Done for templating alignment
                pass
            else:
                assert \
                    isinstance(value, str), \
                    "The 'current_task' field must be of type 'str'"

        self._current_task = value

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
