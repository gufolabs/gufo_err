# ---------------------------------------------------------------------
# Gufo Err: Serialize/deserialize
# ---------------------------------------------------------------------
# Copyright (C) 2022, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
from typing import Dict, Any, Union, Tuple
import json
import uuid
import datetime

# Gufo Labs modules
from .types import ErrorInfo, FrameInfo, SourceInfo

CODEC_TYPE = "errorinfo"
CURRENT_VERSION = "1.0"


def to_dict(info: ErrorInfo) -> Dict[str, Any]:
    """
    Serialize ErrorInfo to a dict of primitive types.

    Args:
        info: ErrorInfo instance.

    Returns:
        Dict of primitive types (str, int, float).
    """

    def q_x_class(e: BaseException) -> str:
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

    def q_var(x: Any) -> Union[str, int, float]:
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

    def q_frame_info(fi: FrameInfo) -> Dict[str, Any]:
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
            "locals": {x: q_var(y) for x, y in fi.locals.items()},
        }
        if fi.source:
            r["source"] = q_source(fi.source)
        return r

    def q_source(si: SourceInfo) -> Dict[str, Any]:
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

    def q_exception(e: BaseException) -> Dict[str, Any]:
        """
        Convery exception into JSON-serializeable form.

        Args:
            e: BaseException instance

        Returns:
            Serialized dict
        """
        return {
            "class": q_x_class(e),
            "args": [q_var(x) for x in e.args],
        }

    r = {
        "$type": CODEC_TYPE,
        "$version": CURRENT_VERSION,
        "name": info.name,
        "version": info.version,
        "fingerprint": str(info.fingerprint),
        "exception": q_exception(info.exception),
        "stack": [q_frame_info(x) for x in info.stack],
    }
    if info.timestamp:
        r["timestamp"] = info.timestamp.isoformat()
    # @todo: stack
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
    """

    def get(d: Dict[str, Any], name: str) -> Any:
        """
        Get key from dict or raise ValueError if not found.

        Args:
            d: Data dictionary
            name: Key name

        Returns:
            Value
        """
        x = d.get(name, None)
        if x is None:
            raise ValueError(f"{name} is required")
        return x

    def get_fi(d: Dict[str, Any]) -> FrameInfo:
        if d.get("source"):
            source = get_si(d["source"])
        else:
            source = None
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
        raise ValueError("dict required")
    # Check data has proper type signature
    ci_type = get(data, "$type")
    if ci_type != CODEC_TYPE:
        raise ValueError("Invalid $type")
    # Check version
    ci_version = get(data, "$version")
    if ci_version != CURRENT_VERSION:
        raise ValueError("Unknown $version")
    # Process timestamp
    src_ts = data.get("timestamp")
    if src_ts:
        ts = datetime.datetime.fromisoformat(src_ts)
    else:
        ts = None
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
    )


def from_json(data: str) -> ErrorInfo:
    """
    Deserialize ErrorInfo from JSON string.

    Args:
        data: JSON string

    Returns:
        ErrorInfo instance
    """
    return from_dict(json.loads(data))


class ExceptionStub(Exception):
    """
    Stub to deserialized exceptions.

    Args:
        kls: Exception class name
        args: Exception arguments
    """

    def __init__(self, kls: str, args: Tuple[Any, ...]) -> None:
        self.kls = kls
        self.args = args
