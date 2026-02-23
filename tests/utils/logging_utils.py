from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from typing import Any

_SENSITIVE_KEYS = {
    "authorization",
    "password",
    "token",
    "access_token",
    "refresh_token",
    "api_key",
    "secret",
}


def _is_sensitive_key(key: str) -> bool:
    normalized = key.lower()
    return any(fragment in normalized for fragment in _SENSITIVE_KEYS)


def _serialize_value(key: str, value: Any) -> str:
    if _is_sensitive_key(key):
        return "<redacted>"

    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)

    if isinstance(value, bool | int | float):
        return str(value)

    if isinstance(value, Mapping | list | tuple | set):
        try:
            return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
        except TypeError:
            return str(value)

    return str(value)


def format_context(**context: Any) -> str:
    """Build deterministic key=value context string for logs."""
    parts: list[str] = []
    for key in sorted(context):
        value = context[key]
        if value is None:
            continue
        parts.append(f"{key}={_serialize_value(key, value)}")
    return " ".join(parts)


def build_log_message(domain: str, action: str, **context: Any) -> str:
    prefix = f"[{domain.upper()}][{action.upper()}]"
    context_str = format_context(**context)
    if not context_str:
        return prefix
    return f"{prefix} {context_str}"


def log_event(
    logger: logging.Logger,
    domain: str,
    action: str,
    *,
    level: int = logging.INFO,
    **context: Any,
) -> None:
    logger.log(level, build_log_message(domain, action, **context))


def standardize_legacy_message(message: str) -> str:
    if message.startswith("["):
        return message
    return build_log_message("legacy", "message", text=message)


class LegacyMessageFilter(logging.Filter):
    """Converts free-form logs to the standardized [DOMAIN][ACTION] format."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = standardize_legacy_message(record.getMessage())
        record.args = ()
        return True
