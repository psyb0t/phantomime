from functools import wraps
from typing import Callable, Any
from . import phantomime


def _must_have_driver_initialized(fn: Callable) -> Any:
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if phantomime._driver is None:
            raise Exception("_driver is not initialized")

        return fn(*args, **kwargs)

    return wrapper


def _must_have_driver_uninitialized(fn: Callable) -> Any:
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if phantomime._driver is not None:
            raise Exception("_driver is initialized")

        return fn(*args, **kwargs)

    return wrapper


def _must_have_supported_selector_type(fn: Callable) -> Any:
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


def _must_have_supported_select_option_selector_type(fn: Callable) -> Any:
    @wraps(fn)
    def wrapper(*args, **kwargs):
        selector_type = args[0].upper()

        supported_selector_types = [
            phantomime.SELECT_OPTION_SELECTOR_TYPE_INDEX,
            phantomime.SELECT_OPTION_SELECTOR_TYPE_TEXT,
            phantomime.SELECT_OPTION_SELECTOR_TYPE_VALUE
        ]

        if selector_type not in supported_selector_types:
            raise Exception(
                f"invalid select option selector type. supported: {', '.join(supported_selector_types)}"
            )

        return fn(*args, **kwargs)

    return wrapper


def _must_have_supported_driver_type(fn: Callable) -> Any:
    @wraps(fn)
    def wrapper(*args, **kwargs):
        driver_type = args[1].upper()

        supported_driver_types = [
            phantomime.DRIVER_TYPE_FIREFOX,
            phantomime.DRIVER_TYPE_CHROME
        ]

        if driver_type not in supported_driver_types:
            raise Exception(
                f"invalid driver type. supported: {', '.join(supported_driver_types)}"
            )

        return fn(*args, **kwargs)

    return wrapper


def _must_have_supported_screenshot_output_type(fn: Callable) -> Any:
    @wraps(fn)
    def wrapper(*args, **kwargs):
        output_type = args[0].upper()

        supported_output_types = [
            phantomime.SCREENSHOT_OUTPUT_TYPE_BASE64,
            phantomime.SCREENSHOT_OUTPUT_TYPE_FILE
        ]

        if output_type not in supported_output_types:
            raise Exception(
                f"invalid screenshot output type. supported: {', '.join(supported_output_types)}"
            )

        return fn(*args, **kwargs)

    return wrapper
