from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from tests.utils.sensitive_data import REDACTED_VALUE, is_sensitive_key, redact_data

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _is_project_record(record: logging.LogRecord) -> bool:
    pathname = getattr(record, "pathname", "")
    if pathname:
        try:
            return Path(pathname).resolve().is_relative_to(_PROJECT_ROOT)
        except OSError:
            return False

    return record.name.startswith("tests")


def _serialize_value(key: str, value: Any) -> str:
    if is_sensitive_key(key):
        return REDACTED_VALUE

    safe_value = redact_data(value)

    if isinstance(safe_value, str):
        return json.dumps(safe_value, ensure_ascii=False)

    if isinstance(safe_value, bool | int | float):
        return str(safe_value)

    if isinstance(safe_value, Mapping | list | tuple | set):
        try:
            return json.dumps(safe_value, ensure_ascii=False, sort_keys=True, default=str)
        except TypeError:
            return str(safe_value)

    return str(safe_value)


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
        if _is_project_record(record):
            record.msg = standardize_legacy_message(record.getMessage())
            record.args = ()
        return True
