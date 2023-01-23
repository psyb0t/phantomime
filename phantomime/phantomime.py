import logging
import backoff
from . import docker
from . import decorators
from . import utils

from typing import Tuple, List, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver import Remote
from selenium.webdriver.common.options import ArgOptions
from selenium.webdriver.common.alert import Alert

_log = logging.getLogger(__package__)

DEFAULT_WINDOW_WITDH: int = 640
DEFAULT_WINDOW_HEIGHT: int = 480

DRIVER_TYPE_FIREFOX: str = "FIREFOX"
DRIVER_TYPE_CHROME: str = "CHROME"

SELECTOR_TYPE_XPATH: str = "XPATH"
SELECTOR_TYPE_CSS: str = "CSS_SELECTOR"

SELECT_OPTION_SELECTOR_TYPE_INDEX: str = "INDEX"
SELECT_OPTION_SELECTOR_TYPE_TEXT: str = "TEXT"
SELECT_OPTION_SELECTOR_TYPE_VALUE: str = "VALUE"

SCREENSHOT_OUTPUT_TYPE_BASE64: str = "BASE64"
SCREENSHOT_OUTPUT_TYPE_FILE: str = "FILE"

_driver_type_to_options: Dict = {
    DRIVER_TYPE_FIREFOX: webdriver.FirefoxOptions(),
    DRIVER_TYPE_CHROME: webdriver.ChromeOptions()
}

_driver: Remote = None


@decorators._must_have_supported_driver_type
@decorators._must_have_driver_uninitialized
@backoff.on_exception(backoff.expo, Exception, max_time=30, on_giveup=utils.backoff_raise_timeout_exception)
def _init_driver(driver_type: str, selenium_hub_url: str, driver_arguments: List[str]):
    global _driver
    options = _driver_type_to_options[driver_type]

    for driver_option in driver_arguments:
        options.add_argument(driver_option)

    _driver = webdriver.Remote(
        command_executor=selenium_hub_url,
        options=options
    )

    set_window_size(DEFAULT_WINDOW_WITDH, DEFAULT_WINDOW_HEIGHT)


@decorators._must_have_supported_driver_type
@decorators._must_have_driver_uninitialized
def start(driver_type: str = DRIVER_TYPE_FIREFOX, selenium_hub_url: str = None, driver_arguments: List[str] = []):
    """
    Start the session by initializing the driver and connecting to the given Selenium Hub URL.
    If the Selenium Hub URL is not provided, a docker container running the
    Selenium Hub will be started and the URL http://localhost:<random_ephemeral_port>/wd/hub will be used.
    """
    if selenium_hub_url is None:
        selenium_hub_port = docker._start_container(driver_type)
        selenium_hub_url = f"http://localhost:{selenium_hub_port}/wd/hub"

    _init_driver(driver_type, selenium_hub_url, driver_arguments)


@decorators._must_have_driver_initialized
def stop():
    """
    Stop the session by quitting the driver and stopping the Selenium hub container.
    """
    global _driver
    _driver.quit()
    _driver = None

    docker._stop_container()


@decorators._must_have_driver_initialized
def set_page_load_timeout(page_load_timeout: int):
    """
    Set the page load timeout for the session.
    """
    _driver.set_page_load_timeout(page_load_timeout)


@decorators._must_have_driver_initialized
def set_window_size(x: int, y: int):
    """
    Set the window size for the session.
    """
    _driver.set_window_size(x, y)


@decorators._must_have_driver_initialized
def load_page(url: str) -> str:
    """
    Navigate to the specified URL.
    """
    _log.debug(f"loading page {url}")
    _driver.get(url)


@decorators._must_have_driver_initialized
def get_page_source() -> str:
    """
    Get the HTML source of the current page.
    """
    return _driver.page_source


@decorators._must_have_driver_initialized
def is_page_ready() -> bool:
    """
    Check if the current page is fully loaded.
    """
    _log.debug("checking if page is ready")

    return execute_script(
        'return document.readyState == "complete";'
    )


@decorators._must_have_driver_initialized
def wait_page_ready(timeout: int = 30):
    """
    Wait for the current page to be fully loaded.
    """
    _log.debug(f"waiting max {timeout}sec for page to be ready")

    b = backoff.on_predicate(
        backoff.expo,
        lambda x: not x,
        on_giveup=utils.backoff_raise_timeout_exception,
        max_time=timeout
    )

    b(is_page_ready)()


@decorators._must_have_driver_initialized
def get_page_title() -> str:
    """
    Returns the title of the current page.
    """
    return _driver.title


@decorators._must_have_driver_initialized
def scroll_page():
    """
    Scrolls the page by its current height.
    """
    _log.debug("scrolling page")

    return execute_script('window.scrollTo(0, document.body.scrollHeight);')


@decorators._must_have_driver_initialized
def is_text_on_page(text: str) -> bool:
    """
    Check if the given text is present on the current page.
    """
    _log.debug(f"checking if page contains text: {text}")

    if find_elements(SELECTOR_TYPE_XPATH, f'//*[contains(text(), "{text}")]'):
        return True

    return False


@decorators._must_have_driver_initialized
def wait_text_on_page(text: str, timeout: int = 30):
    """
    Wait for the given text to appear on the current page.
    """
    _log.debug(f"waiting {timeout}sec for page to contain text: {text}")

    b = backoff.on_predicate(
        backoff.expo,
        lambda x: not x,
        on_giveup=utils.backoff_raise_timeout_exception,
        max_time=timeout
    )

    b(is_text_on_page)(text)


@decorators._must_have_supported_selector_type
@decorators._must_have_driver_initialized
def find_element(selector_type: str, selector: str) -> WebElement:
    """
    Find the first element matching the given selector and selector type.
    """
    _log.debug(
        f"finding element matching {selector} by selector type {selector_type}")

    try:
        return _driver.find_element(getattr(By, selector_type), selector)
    except:
        return None


@decorators._must_have_supported_selector_type
@decorators._must_have_driver_initialized
def find_select_element(selector_type: str, selector: str) -> Select:
    """
    Find the first element matching the given selector and selector type and return it as a Select wrapped WebElement.
    """
    _log.debug(
        f"finding element matching {selector} by selector type {selector_type} and returning it as a Select wrapped WebElement")

    return Select(find_element(selector_type, selector))


@decorators._must_have_supported_selector_type
@decorators._must_have_driver_initialized
def find_elements(selector_type: str, selector: str) -> List[WebElement]:
    """
    Find all elements matching the given selector and selector type.
    """
    _log.debug(
        f"finding elements matching {selector} by selector type {selector_type}")

    try:
        return _driver.find_elements(getattr(By, selector_type), selector)
    except:
        return None


@decorators._must_have_supported_selector_type
@decorators._must_have_driver_initialized
def wait_element_exists(selector_type: str, selector: str, timeout: int = 10) -> WebElement:
    """
    Waits for an element matching the given selector by selector_type to exist on the current page.
    """
    _log.debug(
        f"waiting for element matching {selector} by selector type {selector_type} to exist")

    b = backoff.on_predicate(
        backoff.expo,
        lambda el: el is None,
        on_giveup=utils.backoff_raise_timeout_exception,
        max_time=timeout
    )

    return b(find_element)(selector_type, selector)


@decorators._must_have_supported_selector_type
@decorators._must_have_driver_initialized
def wait_element_not_exists(selector_type: str, selector: str, timeout: int = 10):
    """
    Waits for an element matching the given selector by selector_type to not exist on the current page.
    """
    _log.debug(
        f"waiting for element matching {selector} by selector type {selector_type} to not exist")

    b = backoff.on_predicate(
        backoff.expo,
        lambda el: el is not None,
        on_giveup=utils.backoff_raise_timeout_exception,
        max_time=timeout
    )

    b(find_element)(selector_type, selector)


@decorators._must_have_driver_initialized
def is_element_visible(element: WebElement) -> bool:
    """
    Check if the given element is visible and in the current viewport.
    """
    return element.is_displayed()


@decorators._must_have_driver_initialized
def wait_element_is_visible(element: WebElement, timeout: int = 10):
    """
    Wait for the given element to be visible and in the current viewport.
    """
    _log.debug(
        f"waiting {timeout}sec for element to be visible and in the current viewport: {element}")

    b = backoff.on_predicate(
        backoff.expo,
        lambda x: not x,
        on_giveup=utils.backoff_raise_timeout_exception,
        max_time=timeout
    )

    b(is_element_visible)(element)


@decorators._must_have_driver_initialized
def wait_element_not_visible(element: WebElement, timeout: int = 10):
    """
    Wait for the given element to not be visible.
    """
    _log.debug(
        f"waiting {timeout}sec for element to not be visible: {element}")

    b = backoff.on_predicate(
        backoff.expo,
        lambda x: x,
        on_giveup=utils.backoff_raise_timeout_exception,
        max_time=timeout
    )

    b(is_element_visible)(element)


@decorators._must_have_driver_initialized
def is_element_in_viewport(element: WebElement) -> bool:
    """
    Check if an element is visible in the viewport
    """
    _log.debug(f"checking if element {element} is in viewport")

    bounding_rect = execute_script("""
        var rect = arguments[0].getBoundingClientRect();
        return {
            x: rect.x,
            y: rect.y,
            width: rect.width,
            height: rect.height,
            top: rect.top,
            right: rect.right,
            bottom: rect.bottom,
            left: rect.left
        };
    """, element)

    viewport_size = execute_script("""
        return {
            width: document.documentElement.clientWidth,
            height: document.documentElement.clientHeight
        };
    """)

    if bounding_rect["right"] < 0 or bounding_rect["bottom"] < 0:
        return False
    if bounding_rect["left"] > viewport_size["width"] or bounding_rect["top"] > viewport_size["height"]:
        return False
    return True


@decorators._must_have_driver_initialized
def wait_element_in_viewport(element: WebElement, timeout: int = 10):
    """
    Wait for an element to be visible in viewport
    """
    _log.debug(f"waiting {timeout}sec for element {element} to be viewport")

    b = backoff.on_predicate(
        backoff.expo,
        lambda x: not x,
        on_giveup=utils.backoff_raise_timeout_exception,
        max_time=timeout
    )

    b(is_element_in_viewport)(element)


@decorators._must_have_driver_initialized
def scroll_to_element(element: WebElement):
    """
    Scrolls the page so that the given element is visible.
    """
    _log.debug(f"scrolling to element {element}")
    execute_script('return arguments[0].scrollIntoView(true);', element)


@decorators._must_have_supported_selector_type
@decorators._must_have_driver_initialized
def switch_to_iframe(selector_type: str, selector: str):
    """
    Move to an iframe
    """
    _log.debug(f"switching to iframe {selector} by {selector_type}")
    el = find_element(selector_type, selector)
    if el is None:
        raise Exception(f"could not find iframe {selector} by {selector_type}")

    _driver.switch_to.frame(el)


@decorators._must_have_driver_initialized
def switch_to_main():
    _log.debug(f"switching to main")
    _driver.switch_to.default_content()


@decorators._must_have_driver_initialized
def hover_on_element(element: WebElement):
    """
    Hovers the mouse pointer over the given element.
    """
    _log.debug(f"hovering to element {element}")

    actions = ActionChains(_driver)
    actions.move_to_element(element)
    actions.perform()


@decorators._must_have_driver_initialized
def click_by_js(element: WebElement):
    """
    Clicks the given element using JavaScript.
    """
    _log.debug(f"clicking on element {element} by JS")
    execute_script('arguments[0].click();', element)


@decorators._must_have_driver_initialized
def execute_script(script: str, *args) -> Any:
    """
    Execute a JavaScript script.
    """
    _log.debug(f"executing script {script}")

    return _driver.execute_script(script, *args)


@decorators._must_have_driver_initialized
def wait_for_alert(timeout: int = 3) -> Alert:
    """
    Wait for an alert to be present.
    """
    _log.debug(f"waiting {timeout}sec for an alert")

    return WebDriverWait(_driver, timeout).until(EC.alert_is_present())


@decorators._must_have_driver_initialized
def add_cookie(name: str, value: str):
    """
    Add a cookie to the page
    """
    _log.debug(f"adding cookie {name} = {value}")

    cookie = {
        "name": name,
        "value": value,
    }

    _driver.add_cookie(cookie)


@decorators._must_have_driver_initialized
def get_cookie(name: str) -> Any:
    """
    Get a cookie by name
    """
    _log.debug(f"getting cookie {name}")

    return _driver.get_cookie(name)


@decorators._must_have_driver_initialized
def delete_cookie(name: str):
    """
    Delete a cookie by name
    """
    _log.debug(f"deleting cookie {name}")

    return _driver.delete_cookie(name)


@decorators._must_have_driver_initialized
def clear_cookies():
    """
    Clear all cookies.
    """
    _driver.delete_all_cookies()


@decorators._must_have_supported_screenshot_output_type
@decorators._must_have_driver_initialized
def screenshot(output_type: str, filename=None) -> str:
    """
    Take a screenshot.
    """
    filename_log_part = f" and filename {filename}"
    _log.debug(
        f"taking a screenshot having output type {output_type}{filename_log_part}")

    if output_type is SCREENSHOT_OUTPUT_TYPE_BASE64:
        return _driver.get_screenshot_as_base64()

    png_filename = f"{filename}.png"
    if not _driver.get_screenshot_as_file(png_filename):
        raise Exception("could not get screenshot as file")

    return png_filename
