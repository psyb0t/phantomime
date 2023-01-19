import logging
import backoff
from . import docker
from . import decorators

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

DEFAULT_WINDOW_SIZE: Tuple[int, int] = (640, 480)
DRIVER_TYPE_FIREFOX: str = "FIREFOX"
DRIVER_TYPE_CHROME: str = "CHROME"

SELECTOR_TYPE_XPATH: str = "XPATH"
SELECTOR_TYPE_CSS: str = "CSS_SELECTOR"

SELECT_OPTION_SELECTOR_TYPE_INDEX: str = "INDEX"
SELECT_OPTION_SELECTOR_TYPE_TEXT: str = "TEXT"
SELECT_OPTION_SELECTOR_TYPE_VALUE: str = "VALUE"

SCREENSHOT_OUTPUT_TYPE_BASE64: str = "BASE64"
SCREENSHOT_OUTPUT_TYPE_FILE: str = "FILE"

_driver_type: str = DRIVER_TYPE_FIREFOX
_driver_type_to_options: Dict[str: ArgOptions] = {
    DRIVER_TYPE_FIREFOX: webdriver.FirefoxOptions(),
    DRIVER_TYPE_CHROME: webdriver.ChromeOptions()
}

_driver: Remote = None


@decorators._must_have_supported_driver_type
def set_driver_type():
    driver_type = driver_type.lower()
    supported_driver_types = [DRIVER_TYPE_FIREFOX, DRIVER_TYPE_CHROME]
    if driver_type not in supported_driver_types:
        raise Exception(
            'invalid driver. supported: %s' % ', '.join(supported_driver_types)
        )

    global _driver_type
    _driver_type = driver_type


@decorators._must_have_driver_uninitialized
@backoff.on_exception(backoff.expo, Exception, max_time=30)
def _init_driver(driver_type: str, selenium_hub_url: str):
    global _driver
    _driver = webdriver.Remote(
        command_executor=selenium_hub_url,
        options=_driver_type_to_options[driver_type]
    )

    set_window_size(DEFAULT_WINDOW_SIZE)


def start():
    selenium_hub_port = docker.start_container()
    selenium_hub_url = f"http://localhost:{selenium_hub_port}/wd/hub"
    _init_driver(selenium_hub_url)


def stop():
    _driver.quit()
    docker.stop_container()


@decorators._must_have_driver_initialized
def set_page_load_timeout(page_load_timeout: int):
    _driver.set_page_load_timeout(page_load_timeout)


@decorators._must_have_driver_initialized
def set_window_size(window_size: Tuple[int, int]):
    _driver.set_window_size(window_size[0], window_size[1])


@decorators._must_have_driver_initialized
def load_page(url: str) -> str:
    _log.debug(f"loading page {url}")
    _driver.get(url)


@decorators._must_have_driver_initialized
def get_page_source() -> str:
    return _driver.page_source


@decorators._must_have_driver_initialized
def is_page_ready() -> bool:
    _log.debug("checking if page is ready")

    return execute_script(
        'return document.readyState == "complete";'
    )


@decorators._must_have_driver_initialized
def wait_page_ready(timeout: int = 30):
    _log(f"waiting max {timeout}sec for page to be ready")

    f = backoff.on_predicate(backoff.expo, lambda x: x,
                             max_time=timeout)(is_page_ready)

    f()


@decorators._must_have_driver_initialized
def page_title():
    return _driver.title


@decorators._must_have_driver_initialized
def scroll_page():
    _log.debug("scrolling page")

    return execute_script('window.scrollTo(0, document.body.scrollHeight);')


@decorators._must_have_driver_initialized
def is_text_on_page(text: str) -> bool:
    _log.debug(f"checking if page contains text: {text}")

    if find_elements(SELECTOR_TYPE_XPATH, f'//*[contains(text(), "{text}")]'):
        return True

    return False


@decorators._must_have_driver_initialized
def wait_text_on_page(text: str, timeout: int = 30):
    _log(f"waiting {timeout}sec for page to contain text: {text}")

    f = backoff.on_predicate(backoff.expo, lambda x: x,
                             max_time=timeout)(is_text_on_page)

    f(text)


def find_element(selector_type: str, selector: str) -> WebElement:
    _log.debug(
        f"finding element matching {selector} by selector type {selector_type}")

    try:
        return _driver.find_element(getattr(By, selector_type), selector)
    except:
        return None


@decorators._must_have_supported_selector_type
@decorators._must_have_driver_initialized
def find_elements(selector_type: str, selector: str) -> List[WebElement]:
    _log.debug(
        f"finding elements matching {selector} by selector type {selector_type}")

    try:
        return _driver.find_elements(getattr(By, selector_type), selector)
    except:
        return None


@decorators._must_have_supported_selector_type
@decorators._must_have_driver_initialized
def is_element_visible(element: WebElement) -> bool:
    return element.is_displayed()


@decorators._must_have_supported_selector_type
@decorators._must_have_driver_initialized
def wait_element_visible(element: WebElement, timeout: int = 10):
    _log(f"waiting {timeout}sec for element to be visible: {element}")

    f = backoff.on_predicate(backoff.expo, lambda x: x,
                             max_time=timeout)(is_element_visible)

    f(element)


@decorators._must_have_supported_selector_type
@decorators._must_have_driver_initialized
def wait_element_not_visible(element: WebElement, timeout: int = 10):
    _log(f"waiting {timeout}sec for element to not be visible: {element}")

    f = backoff.on_predicate(backoff.expo, lambda x: not x,
                             max_time=timeout)(is_element_visible)

    f(element)


@decorators._must_have_supported_selector_type
@decorators._must_have_driver_initialized
def wait_element_exists(selector_type: str, selector: str, timeout: int = 10) -> WebElement:
    _log.debug(
        f"waiting for element matching {selector} by selector type {selector_type} to exist")

    f = backoff.on_predicate(backoff.expo, lambda el: el is not None,
                             max_time=timeout)(find_element)

    return f(selector_type, selector)


@decorators._must_have_supported_selector_type
@decorators._must_have_driver_initialized
def wait_element_not_exists(selector_type: str, selector: str, timeout: int = 10):
    _log.debug(
        f"waiting for element matching {selector} by selector type {selector_type} to not exist")

    f = backoff.on_predicate(backoff.expo, lambda el: el is None,
                             max_time=timeout)(find_element)

    f(selector_type, selector)


@decorators._must_have_driver_initialized
def scroll_to_element(element: WebElement):
    _log.debug(f"scrolling to element {element}")
    execute_script('return arguments[0].scrollIntoView(true);', element)


@decorators._must_have_driver_initialized
def hover_on_element(element: WebElement):
    _log.debug(f"hovering to element {element}")

    actions = ActionChains(_driver)
    actions.move_to_element(element)
    actions.perform()


@decorators._must_have_driver_initialized
def click_by_js(element: WebElement):
    _log.debug(f"clicking on element {element} by JS")
    execute_script('arguments[0].click();', element)


@decorators._must_have_supported_select_option_selector_type
@decorators._must_have_driver_initialized
def select_option(element: WebElement, selector_type: str, value: Any):
    _log.debug(f"selecting option {value} by {selector_type} on {element}")

    select = Select(element)
    if selector_type is SELECT_OPTION_SELECTOR_TYPE_INDEX:
        return select.select_by_index(value)
    elif selector_type is SELECT_OPTION_SELECTOR_TYPE_TEXT:
        select.select_by_visible_text(value)
    elif selector_type is SELECT_OPTION_SELECTOR_TYPE_VALUE:
        select.select_by_value(value)


@decorators._must_have_driver_initialized
def execute_script(script: str) -> Any:
    _log.debug(f"executing script {script}")

    return _driver.execute_script(script)


@decorators._must_have_driver_initialized
def wait_for_alert(timeout: int = 3) -> Alert:
    _log.debug(f"waiting {timeout}sec for an alert")

    return WebDriverWait(_driver, timeout).until(EC.alert_is_present())


@decorators._must_have_driver_initialized
def clear_cookies():
    _driver.delete_all_cookies()


@decorators._must_have_driver_initialized
def screenshot(output_type: str, filename=None) -> str:
    filename_log_part = f" and filename {filename}"
    _log.debug(
        f"taking a screenshot having output type {output_type}{filename_log_part}")

    if output_type is SCREENSHOT_OUTPUT_TYPE_BASE64:
        return _driver.get_screenshot_as_base64()

    png_filename = f"{filename}.png"
    if not _driver.get_screenshot_as_file(png_filename):
        raise Exception("could not get screenshot as file")

    return png_filename
