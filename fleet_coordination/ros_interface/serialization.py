"""
Serialization Module — Dataclass <-> JSON/Dict Conversion.
===========================================================

Provides deterministic, schema-safe serialization and deserialization for
domain data models (RobotState, RobotIntent, Pose2D, etc.) used across
the decentralized ROS 2 messaging boundary.

Zero ROS imports — pure Python standard library (json, dataclasses, enum).
"""

from __future__ import annotations

import json
from dataclasses import fields, is_dataclass
from enum import Enum
from typing import Any, TypeVar, get_args, get_origin, get_type_hints

from fleet_coordination.models.pose import Pose2D
from fleet_coordination.models.robot_intent import RobotIntent
from fleet_coordination.models.robot_state import RobotState, RobotStatus

T = TypeVar("T")


def to_dict(obj: Any) -> Any:
    """Convert a domain model, Enum, dataclass, or collection to a JSON-serializable structure.

    Args:
        obj: The domain object, dataclass, Enum, list, dict, or primitive to convert.

    Returns:
        A JSON-safe structure consisting of primitives, dicts, and lists.

    Raises:
        TypeError: If an unhandled or non-serializable object type is provided.
    """
    if obj is None:
        return None
    if isinstance(obj, Enum):
        return obj.name
    if isinstance(obj, (int, float, str, bool)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [to_dict(item) for item in obj]
    if isinstance(obj, dict):
        return {str(k): to_dict(v) for k, v in obj.items()}
    if is_dataclass(obj) and not isinstance(obj, type):
        result: dict[str, Any] = {}
        for f in fields(obj):
            val = getattr(obj, f.name)
            result[f.name] = to_dict(val)
        return result

    raise TypeError(f"Object of type {type(obj).__name__!r} is not serializable")


def _deserialize_value(value: Any, target_type: Any) -> Any:
    """Recursively deserialize a value into the specified target type."""
    if value is None:
        return None

    # Handle Union types (e.g. str | None, float | None)
    origin = get_origin(target_type)
    if origin is not None:
        args = get_args(target_type)
        # Union / Optional check
        if type(None) in args:
            non_none_args = [a for a in args if a is not type(None)]
            if len(non_none_args) == 1:
                return _deserialize_value(value, non_none_args[0])
        # Generic list (e.g. list[Pose2D])
        if origin is list or target_type is list:
            if not isinstance(value, list):
                raise TypeError(f"Expected list for {target_type}, got {type(value).__name__}")
            elem_type = args[0] if args else Any
            return [_deserialize_value(elem, elem_type) for elem in value]
        # Generic dict
        if origin is dict or target_type is dict:
            if not isinstance(value, dict):
                raise TypeError(f"Expected dict for {target_type}, got {type(value).__name__}")
            val_type = args[1] if len(args) > 1 else Any
            return {k: _deserialize_value(v, val_type) for k, v in value.items()}

    # Handle Enum classes
    if isinstance(target_type, type) and issubclass(target_type, Enum):
        if not isinstance(value, str):
            raise TypeError(
                f"Expected string for enum {target_type.__name__}, got {type(value).__name__}"
            )
        try:
            return target_type[value]
        except KeyError:
            valid_names = [e.name for e in target_type]
            raise ValueError(
                f"Invalid value {value!r} for enum {target_type.__name__}. Valid values: {valid_names}"
            ) from None

    # Handle Dataclass classes
    if isinstance(target_type, type) and is_dataclass(target_type):
        if not isinstance(value, dict):
            raise TypeError(
                f"Expected dict for dataclass {target_type.__name__}, got {type(value).__name__}"
            )
        return from_dict(value, target_type)

    # Handle primitive types
    if target_type in (int, float):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise TypeError(f"Expected numeric for {target_type.__name__}, got {type(value).__name__}")
        return target_type(value)
    if target_type is str:
        if not isinstance(value, str):
            raise TypeError(f"Expected string for str, got {type(value).__name__}")
        return value
    if target_type is bool:
        if not isinstance(value, bool):
            raise TypeError(f"Expected bool for bool, got {type(value).__name__}")
        return value

    return value


def from_dict(data: dict[str, Any], cls: type[T]) -> T:
    """Reconstruct a dataclass instance from a dictionary.

    Args:
        data: The dictionary containing serialized field values.
        cls: The target dataclass type to instantiate.

    Returns:
        An instance of cls populated with deserialized fields.

    Raises:
        TypeError: If data is not a dictionary or field types mismatch.
        ValueError: If required fields are missing or enum values are invalid.
    """
    if not isinstance(data, dict):
        raise TypeError(f"Expected dictionary for from_dict, got {type(data).__name__}")

    if not (isinstance(cls, type) and is_dataclass(cls)):
        raise TypeError(f"Target class {cls} is not a dataclass type")

    type_hints = get_type_hints(cls)
    cls_fields = fields(cls)
    kwargs: dict[str, Any] = {}

    for f in cls_fields:
        field_name = f.name
        field_type = type_hints.get(field_name, Any)

        if field_name in data:
            val = data[field_name]
            kwargs[field_name] = _deserialize_value(val, field_type)
        else:
            # Check if field has default or default_factory
            has_default = (
                f.default is not f.default.__class__()
                if hasattr(f, "default") and f.default is not None
                else False
            )
            # Standard dataclass check for missing required fields
            from dataclasses import _MISSING_TYPE  # type: ignore

            if isinstance(f.default, _MISSING_TYPE) and isinstance(f.default_factory, _MISSING_TYPE):
                raise ValueError(
                    f"Missing required field {field_name!r} for dataclass {cls.__name__}"
                )

    return cls(**kwargs)


def to_json(obj: Any, indent: int | None = None) -> str:
    """Serialize a domain model, dataclass, or collection to a deterministic JSON string.

    Args:
        obj: The domain model or structure to serialize.
        indent: Optional indentation level for pretty printing.

    Returns:
        Deterministic JSON string.
    """
    safe_dict = to_dict(obj)
    return json.dumps(safe_dict, sort_keys=True, indent=indent)


def from_json(json_string: str, cls: type[T]) -> T:
    """Deserialize a JSON string into an instance of the target dataclass.

    Args:
        json_string: Valid JSON string.
        cls: Target dataclass type to reconstruct.

    Returns:
        Reconstructed dataclass instance.

    Raises:
        ValueError: If JSON is malformed, required fields are missing, or values are invalid.
        TypeError: If data types do not match the expected model schema.
    """
    if not isinstance(json_string, str):
        raise TypeError(f"Expected str for json_string, got {type(json_string).__name__}")

    try:
        data = json.loads(json_string)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ValueError(f"Invalid JSON string: {e}") from e

    return from_dict(data, cls)
