import base64
import logging
import backoff
from . import utils
from . import docker
from . import decorators

from typing import Tuple
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

_log = logging.getLogger(__package__)

DEFAULT_WINDOW_SIZE = (640, 480)
DRIVER_TYPE_FIREFOX = "firefox"
DRIVER_TYPE_CHROME = "chrome"

SELECTOR_TYPE_XPATH = "XPATH"
SELECTOR_TYPE_CSS = "CSS_SELECTOR"

_driver_type = DRIVER_TYPE_FIREFOX
_driver_type_to_options = {
    DRIVER_TYPE_FIREFOX: webdriver.FirefoxOptions(),
    DRIVER_TYPE_CHROME: webdriver.ChromeOptions()
}

_driver = None


def set_driver_type(driver_type: str):
    driver_type = driver_type.lower()
    supported_driver_types = [DRIVER_TYPE_FIREFOX, DRIVER_TYPE_CHROME]
    if driver_type not in supported_driver_types:
        raise Exception(
            'invalid driver. supported: %s' % ', '.join(supported_driver_types)
        )

    global _driver_type
    _driver_type = driver_type


@utils._must_have_driver_uninitialized
@backoff.on_exception(backoff.expo, Exception, max_time=30)
def _init_driver(selenium_hub_url: str):
    global _driver
    _driver = webdriver.Remote(
        command_executor=selenium_hub_url,
        options=_driver_type_to_options[_driver_type]
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


@decorators._must_have_supported_selector_type
@decorators._must_have_driver_initialized
def is_element_visible(selector_type: str, selector: str) -> bool:
    return False


@decorators._must_have_driver_initialized
def wait_element_visible(selector_type, selector, t=2):
    """
    _log.debug(
        f"finding elements matching {selector} by selector type {selector_type}")
    if verbose:
        print 'Waiting for %s:%s to be visible...' % (by, sel)

    if by not in ['XPATH', 'CSS', 'CSS_SELECTOR']:
        raise Exception('Invalid SELECT BY type')

    if by == 'CSS':
        by = 'CSS_SELECTOR'

    try:
        WebDriverWait(Browser, t).until(
            EC.visibility_of_element_located((getattr(By, by), sel))
        )

        return find_elements(by, sel)[0]
    except TimeoutException:
        return False
    """


@decorators._must_have_driver_initialized
def wait_element_not_visible(by, sel, t=2):
    """
    if verbose:
        print 'Waiting for %s:%s to not be visible...' % (by, sel)

    if by not in ['XPATH', 'CSS', 'CSS_SELECTOR']:
        raise Exception('Invalid SELECT BY type')

    if by == 'CSS':
        by = 'CSS_SELECTOR'

    try:
        WebDriverWait(Browser, t).until_not(
            EC.visibility_of_element_located((getattr(By, by), sel))
        )

        return True
    except TimeoutException:
        return False
    """


@decorators._must_have_driver_initialized
def wait_element_exists(by, sel, t=2):
    """
    if verbose:
        print 'Waiting for %s:%s to appear in DOM...' % (by, sel)

    if by not in ['XPATH', 'CSS', 'CSS_SELECTOR']:
        raise Exception('Invalid SELECT BY type')

    if by == 'CSS':
        by = 'CSS_SELECTOR'

    try:
        WebDriverWait(Browser, t).until(
            EC.presence_of_element_located((getattr(By, by), sel))
        )

        return find_elements(by, sel)[0]
    except TimeoutException:
        return False
    """


@decorators._must_have_driver_initialized
def wait_element_not_exists(by, sel, t=2):
    """
    if verbose:
        print 'Waiting for %s:%s to disappear in DOM...' % (by, sel)

    if by not in ['XPATH', 'CSS', 'CSS_SELECTOR']:
        raise Exception('Invalid SELECT BY type')

    if by == 'CSS':
        by = 'CSS_SELECTOR'

    try:
        WebDriverWait(Browser, t).until_not(
            EC.presence_of_element_located((getattr(By, by), sel))
        )

        return True
    except TimeoutException:
        return False
    """


@decorators._must_have_supported_selector_type
@decorators._must_have_driver_initialized
def find_elements(selector_type: str, selector: str) -> any:
    _log.debug(
        f"finding elements matching {selector} by selector type {selector_type}")

    try:
        return _driver.find_elements(getattr(By, selector_type), selector)
    except:
        return None


def find_element():
    pass


@decorators._must_have_driver_initialized
def scroll_to_element(element):
    """
    if verbose:
        print 'Scrolling to element...'

    return Browser.execute_script(
        'return arguments[0].scrollIntoView(true);', element
    )
    """


@decorators._must_have_driver_initialized
def hover_on_element(element):
    """
    if verbose:
        print 'Hovering on element...'

    try:
        actions = ActionChains(Browser)
        actions.move_to_element(element)
        actions.perform()

        return True
    except:
        return False
    """


@decorators._must_have_driver_initialized
def click_by_js(element):
    """
    if verbose:
        print 'Clicking on element by js...'

    try:
        Browser.execute_script('arguments[0].click();', element)
        return True
    except:
        return False
    """


@decorators._must_have_driver_initialized
def select_option(select_el, by, val):
    """
    select = Select(select_el)

    if by == 'index':
        return select.select_by_index(val)
    elif by == 'text':
        select.select_by_visible_text(val)
    elif by == 'value':
        select.select_by_value(val)
    else:
        raise Exception('Invalid SELECT BY type')

    return True
    """


@decorators._must_have_driver_initialized
def execute_script(script):
    """
    if verbose:
        print 'Running JavaScript code...'

    return Browser.execute_script(script)
    """


@decorators._must_have_driver_initialized
def wait_for_alert(t=3):
    """
    if verbose:
        print 'Waiting for alert to pop...'

    try:
        WebDriverWait(Browser, t).until(EC.alert_is_present())

        return Browser.switch_to_alert()
    except TimeoutException:
        return False
    """


@decorators._must_have_driver_initialized
def clear_cookies():
    _driver.delete_all_cookies()


@decorators._must_have_driver_initialized
def screenshot(t='base64', fname=None):
    """
    if verbose:
        print 'Taking a screenshot...'

    screenshot_types = ['base64', 'raw', 'file']
    if t not in screenshot_types:
        raise Exception(
            'Invalid screenshot type. Types: %s' % ', '.join(screenshot_types)
        )

    sshot = Browser.get_screenshot_as_base64()

    if t == 'base64':
        return sshot

    raw = base64.b64decode(sshot)
    if t == 'raw':
        return raw

    if t == 'file':
        if not fname:
            raise Exception('Screenshot filename not defined')

        with open('%s.png' % fname, 'w') as f:
            f.write(raw)

            return True
    """
