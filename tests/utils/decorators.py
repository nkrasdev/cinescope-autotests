from collections.abc import Callable
from typing import ParamSpec, TypeVar

import allure

P = ParamSpec("P")
R = TypeVar("R")


def allure_test_details(
    story: str,
    title: str,
    description: str,
    severity: allure.severity_level,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Apply the standard Allure metadata without adding a wrapper frame."""

    def decorator(test_function: Callable[P, R]) -> Callable[P, R]:
        decorated = allure.severity(severity)(test_function)
        decorated = allure.description(description)(decorated)
        decorated = allure.title(title)(decorated)
        return allure.story(story)(decorated)

    return decorator
