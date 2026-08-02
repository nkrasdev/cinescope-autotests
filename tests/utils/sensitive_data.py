import json
import re
from collections.abc import Mapping
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

REDACTED_VALUE = "<redacted>"

_SENSITIVE_KEY_FRAGMENTS = frozenset(
    {
        "apikey",
        "authorization",
        "cardnumber",
        "cvc",
        "cvv",
        "email",
        "password",
        "passwordrepeat",
        "refreshtoken",
        "securitycode",
        "secret",
        "token",
    }
)


def _normalize_key(key: str) -> str:
    return re.sub(r"[^a-z0-9]", "", key.casefold())


def is_sensitive_key(key: str) -> bool:
    normalized_key = _normalize_key(key)
    return any(fragment in normalized_key for fragment in _SENSITIVE_KEY_FRAGMENTS)


def redact_data(value: Any) -> Any:
    """Recursively replace sensitive mapping values with a stable marker."""
    if isinstance(value, Mapping):
        return {key: REDACTED_VALUE if is_sensitive_key(str(key)) else redact_data(item) for key, item in value.items()}
    if isinstance(value, list | tuple | set | frozenset):
        return [redact_data(item) for item in value]
    return value


def sanitize_body(body: str) -> str:
    """Redact JSON or form-encoded bodies while leaving plain text untouched."""
    stripped_body = body.strip()
    if not stripped_body:
        return body

    try:
        payload = json.loads(stripped_body)
    except json.JSONDecodeError:
        payload = None
    else:
        return json.dumps(redact_data(payload), ensure_ascii=False)

    if "=" not in stripped_body:
        return body

    form_fields = parse_qsl(stripped_body, keep_blank_values=True)
    if not form_fields:
        return body

    if not any(is_sensitive_key(key) for key, _ in form_fields):
        return body

    redacted_fields = [(key, REDACTED_VALUE if is_sensitive_key(key) else value) for key, value in form_fields]
    return urlencode(redacted_fields, doseq=True)


def sanitize_url(url: str, *, redact_path: bool = False) -> str:
    """Redact sensitive query values and, optionally, the entire URL path."""
    parsed_url = urlsplit(url)
    safe_path = "/<redacted>" if redact_path and parsed_url.path else parsed_url.path
    query_fields = parse_qsl(parsed_url.query, keep_blank_values=True)
    safe_query = urlencode(
        [(key, REDACTED_VALUE if is_sensitive_key(key) else value) for key, value in query_fields],
        doseq=True,
    )
    return urlunsplit((parsed_url.scheme, parsed_url.netloc, safe_path, safe_query, parsed_url.fragment))
