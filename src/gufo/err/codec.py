# ---------------------------------------------------------------------
# Gufo Err: Serialize/deserialize
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# ---------------------------------------------------------------------
"""ErrInfo serialization/deserialization primitives."""
# Python modules
import datetime
import json
import uuid
from typing import Any, Dict, Union

# Gufo Labs modules
from .types import ErrorInfo, ExceptionStub, FrameInfo, SourceInfo

CODEC_TYPE = "errorinfo"
CURRENT_VERSION = "1.0"


def __q_x_class(e: BaseException) -> str:
    """
    Get exception class.

    Args:
        e: Exception instance

    Returns:
        Serialized exception class name
    """
    mod = e.__class__.__module__
    ncls = e.__class__.__name__
    if mod == "builtins":
        return ncls
    return f"{mod}.{ncls}"


def __q_var(x: Any) -> Union[str, int, float]:  # noqa: ANN401
    """
    Convert variable to the JSON-encodable form.

    Args:
        x: Exception argument

    Returns:
        JSON-serializeable form of argument
    """
    if isinstance(x, (int, float, str)):
        return x
    return str(x)


def __q_frame_info(fi: FrameInfo) -> Dict[str, Any]:
    """
    Convert FrameInfo into JSON-serializeable form.

    Args:
        fi: FrameInfo instance

    Returns:
        Serialized dict
    """
    r = {
        "name": fi.name,
        "module": fi.module,
        "locals": {x: __q_var(y) for x, y in fi.locals.items()},
    }
    if fi.source:
        r["source"] = __q_source(fi.source)
    return r


def __q_source(si: SourceInfo) -> Dict[str, Any]:
    """
    Convert SourceInfo into JSON-serializeable form.

    Args:
        si: SourceInfo instance

    Returns:
        Serialized dict
    """
    return {
        "file_name": si.file_name,
        "first_line": si.first_line,
        "current_line": si.current_line,
        "lines": si.lines,
    }


def __q_exception(e: BaseException) -> Dict[str, Any]:
    """
    Convery exception into JSON-serializeable form.

    Args:
        e: BaseException instance

    Returns:
        Serialized dict
    """
    return {
        "class": __q_x_class(e),
        "args": [__q_var(x) for x in e.args],
    }


def to_dict(info: ErrorInfo) -> Dict[str, Any]:
    """
    Serialize ErrorInfo to a dict of primitive types.

    Args:
        info: ErrorInfo instance.

    Returns:
        Dict of primitive types (str, int, float).
    """
    r = {
        "$type": CODEC_TYPE,
        "$version": CURRENT_VERSION,
        "name": info.name,
        "version": info.version,
        "fingerprint": str(info.fingerprint),
        "exception": __q_exception(info.exception),
        "stack": [__q_frame_info(x) for x in info.stack],
    }
    if info.timestamp:
        r["timestamp"] = info.timestamp.isoformat()
    if info.root_module:
        r["root_module"] = info.root_module
    return r


def to_json(info: ErrorInfo) -> str:
    """
    Serialize ErrorInfo to JSON string.

    Args:
        info: ErrorInfo instance.

    Returns:
        json-encoded string.
    """
    return json.dumps(to_dict(info))


def from_dict(data: Dict[str, Any]) -> ErrorInfo:
    """
    Deserealize Dict to ErrorInfo.

    Args:
        data: Result of to_dict

    Returns:
        ErrorInfo instance

    Raises:
        ValueError: if required key is missed.
    """

    def get(d: Dict[str, Any], name: str) -> Any:  # noqa: ANN401
        """
        Get the key's value from the dictionary.

        Args:
            d: Data dictionary
            name: Key name.

        Returns:
            Value

        Raises:
            ValueError if key is missed.
        """
        x = d.get(name, None)
        if x is None:
            msg = f"{name} is required"
            raise ValueError(msg)
        return x

    def get_fi(d: Dict[str, Any]) -> FrameInfo:
        source = get_si(d["source"]) if d.get("source") else None
        return FrameInfo(
            name=get(d, "name"),
            module=get(d, "module"),
            locals=get(d, "locals"),
            source=source,
        )

    def get_si(d: Dict[str, Any]) -> SourceInfo:
        return SourceInfo(
            file_name=get(d, "file_name"),
            first_line=get(d, "first_line"),
            current_line=get(d, "current_line"),
            lines=get(d, "lines"),
        )

    # Check incoming data is dict
    if not isinstance(data, dict):
        msg = "dict required"
        raise ValueError(msg)
    # Check data has proper type signature
    ci_type = get(data, "$type")
    if ci_type != CODEC_TYPE:
        msg = "Invalid $type"
        raise ValueError(msg)
    # Check version
    ci_version = get(data, "$version")
    if ci_version != CURRENT_VERSION:
        msg = "Unknown $version"
        raise ValueError(msg)
    # Process timestamp
    src_ts = data.get("timestamp")
    ts = datetime.datetime.fromisoformat(src_ts) if src_ts else None
    # Exception
    exc = get(data, "exception")
    # Stack
    stack = [get_fi(x) for x in get(data, "stack")]
    # Set exception stub
    return ErrorInfo(
        name=get(data, "name"),
        version=get(data, "version"),
        fingerprint=uuid.UUID(get(data, "fingerprint")),
        timestamp=ts,
        stack=stack,
        exception=ExceptionStub(kls=exc["class"], args=exc["args"]),
        root_module=data.get("root_module"),
    )


def from_json(data: str) -> ErrorInfo:
    """
    Deserialize ErrorInfo from JSON string.

    Args:
        data: JSON string

    Returns:
        ErrorInfo instance

    Raises:
        ValueError: if required key is missed.
    """
    return from_dict(json.loads(data))
