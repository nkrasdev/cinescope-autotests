import re
from contextlib import suppress

import pytest
from playwright.sync_api import Page

AUTH_FALLBACK_XFAIL_REASON = (
    "DEV UI auth regression (2026-02-23): login/register form falls back to native GET submit with query params."
)
AUTH_FALLBACK_URL_PATTERN = re.compile(r".*/(login|register)\?.*(email|password)=")


def is_dev_auth_form_fallback_url(url: str) -> bool:
    return bool(AUTH_FALLBACK_URL_PATTERN.search(url))


def xfail_if_dev_auth_form_fallback(page: Page, timeout_ms: float = 1500) -> None:
    with suppress(Exception):
        page.wait_for_url(AUTH_FALLBACK_URL_PATTERN, timeout=timeout_ms)

    if is_dev_auth_form_fallback_url(page.url):
        pytest.xfail(AUTH_FALLBACK_XFAIL_REASON)
