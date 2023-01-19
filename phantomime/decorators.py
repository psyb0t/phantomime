from functools import wraps
from typing import Callable
from . import phantomime


def _must_have_driver_initialized(fn: Callable) -> any:
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if _driver is None:
            raise Exception("_driver is not initialized")

        return fn(*args, **kwargs)

    return wrapper


def _must_have_driver_uninitialized(fn: Callable) -> any:
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if phantomime._driver is not None:
            raise Exception("_driver is initialized")

        return fn(*args, **kwargs)

    return wrapper


def _must_have_supported_selector_type(fn: Callable) -> any:
    @wraps(fn)
    def wrapper(*args, **kwargs):
        selector_type = args[0].upper()

        supported_selector_types = [
            phantomime.SELECTOR_TYPE_XPATH,
            phantomime.SELECTOR_TYPE_CSS
        ]

        if selector_type not in supported_selector_types:
            raise Exception(
                f"invalid selector type. supported: {', '.join(supported_selector_types)}"
            )

        return fn(*args, **kwargs)

    return wrapper
