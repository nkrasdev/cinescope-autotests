from __future__ import annotations

import logging
from uuid import uuid4

from tests.utils.logging_utils import LegacyMessageFilter, build_log_message, format_context, log_event


def test_format_context_sorts_keys_and_skips_none() -> None:
    context = format_context(zeta=1, alpha="ok", empty=None)

    assert context == 'alpha="ok" zeta=1'


def test_format_context_redacts_sensitive_values() -> None:
    password_value = uuid4().hex
    access_token_value = uuid4().hex
    authorization_value = f"Bearer {uuid4().hex}"
    context = format_context(
        password=password_value,
        access_token=access_token_value,
        authorization=authorization_value,
    )

    assert context == "access_token=<redacted> authorization=<redacted> password=<redacted>"


def test_build_log_message_uses_standardized_prefix_and_context() -> None:
    message = build_log_message("test", "start", nodeid="tests/api/test_auth.py::test_login")

    assert message == '[TEST][START] nodeid="tests/api/test_auth.py::test_login"'


def test_log_event_writes_structured_message(caplog) -> None:
    logger = logging.getLogger("tests.logging")

    with caplog.at_level(logging.INFO):
        log_event(logger, "fixture", "cleanup", fixture="created_movie", movie_id=42)

    assert caplog.records
    assert caplog.records[-1].message == '[FIXTURE][CLEANUP] fixture="created_movie" movie_id=42'


def test_legacy_message_filter_prefixes_non_structured_logs(caplog) -> None:
    logger = logging.getLogger("tests.legacy")
    logger.addFilter(LegacyMessageFilter())

    with caplog.at_level(logging.INFO):
        logger.info("Старое сообщение без шаблона")

    assert caplog.records[-1].message == '[LEGACY][MESSAGE] text="Старое сообщение без шаблона"'


def test_legacy_message_filter_keeps_structured_logs_unchanged(caplog) -> None:
    logger = logging.getLogger("tests.structured")
    logger.addFilter(LegacyMessageFilter())

    with caplog.at_level(logging.INFO):
        logger.info('[TEST][START] nodeid="tests/api/test_auth.py::test_login"')

    assert caplog.records[-1].message == '[TEST][START] nodeid="tests/api/test_auth.py::test_login"'


def test_legacy_message_filter_does_not_rewrite_external_record() -> None:
    record = logging.LogRecord(
        name="urllib3.connectionpool",
        level=logging.INFO,
        pathname="/usr/lib/python3.13/site-packages/urllib3/connectionpool.py",
        lineno=100,
        msg="external message",
        args=(),
        exc_info=None,
    )

    processed = LegacyMessageFilter().filter(record)

    assert processed is True
    assert record.msg == "external message"
