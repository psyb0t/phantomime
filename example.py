import traceback
import logging
from phantomime import phantomime
from selenium.webdriver.remote.remote_connection import LOGGER as SELENIUM_LOGGER

_log_format = "[%(asctime)s] %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=_log_format)

SELENIUM_LOGGER.setLevel(logging.WARN)
logging.getLogger("requests").setLevel(logging.WARN)
logging.getLogger("urllib3").setLevel(logging.WARN)
logging.getLogger("docker").setLevel(logging.WARN)

phantomime.start(phantomime.DRIVER_TYPE_FIREFOX)
phantomime.set_page_load_timeout(30)
phantomime.set_window_size(1280, 720)

try:
    # get page
    phantomime.load_page("http://psyb0t.github.io/phantomime/test-page/")
    if not phantomime.is_page_ready():
        try:
            phantomime.wait_page_ready()
        except Exception as e:
            raise Exception(
                f"page did not become ready on time - Exception: {e}")

    page_html = phantomime.get_page_source()

    # check page title is the expected one
    expected_page_title = "phantomime test"
    actual_page_title = phantomime.get_page_title()
    if actual_page_title != expected_page_title:
        raise Exception(
            f"actual page title is {actual_page_title} but expected {expected_page_title}")

    phantomime.scroll_page()

    # check if known text is on page
    expected_text_on_page = "this text is expected"
    if not phantomime.is_text_on_page(expected_text_on_page):
        try:
            phantomime.wait_text_on_page(expected_text_on_page)
        except Exception as e:
            raise Exception(
                f"text {expected_text_on_page} did not appear on page - Exception: {e}")

    # select h1 element
    selector = "h1#page-title"
    el = phantomime.find_element(phantomime.SELECTOR_TYPE_CSS, selector)
    if el is None:
        raise Exception(f"element {selector} not found")

    # select h2 elements
    selector = '//h2[@class="page-subtitle"]'
    els = phantomime.find_elements(phantomime.SELECTOR_TYPE_XPATH, selector)
    if els is None or len(els) != 2:
        raise Exception(f"expected 2 {selector} elements. got {els}")

    # select paragraph visibility toggler button
    selector = "button#toggle-paragraph-visibility"
    toggle_btn = phantomime.find_element(
        phantomime.SELECTOR_TYPE_CSS, selector)
    if toggle_btn is None:
        raise Exception(f"{selector} not found")

    # select invisible paragraph
    selector = "p#invisible-paragraph"
    p_el = phantomime.find_element(phantomime.SELECTOR_TYPE_CSS, selector)
    if p_el is None:
        raise Exception(f"{selector} not found")

    if phantomime.is_element_visible(p_el):
        raise Exception(f"expected {selector} to not be visible")

    # this triggers some js code which sets a timeout of 10 seconds until the paragraph becomes visible and in the current viewport
    toggle_btn.click()

    try:
        phantomime.wait_element_is_visible(p_el, 15)
    except Exception as e:
        raise Exception(f"{selector} did not appear on page - Exception: {e}")

    # this triggers some js code which sets a timeout of 10 seconds until the paragraph becomes invisible
    toggle_btn.click()

    try:
        phantomime.wait_element_not_visible(p_el, 15)
    except Exception as e:
        raise Exception(
            "{selector} did not disappear from page - Exception: {e}")

    # select span creator button
    selector = "button#toggle-span-existence"
    toggle_btn = phantomime.find_element(
        phantomime.SELECTOR_TYPE_CSS, selector)
    if toggle_btn is None:
        raise Exception(f"{selector} not found")

    # check dynamic span does not exist
    span_selector = "span#dynamically-created"
    el = phantomime.find_element(phantomime.SELECTOR_TYPE_CSS, span_selector)
    if el is not None:
        raise Exception(f"expected {span_selector} to not exist")

    # this triggers some js code which sets a timeout of 10 seconds until the span gets added to the dom
    toggle_btn.click()
    try:
        phantomime.wait_element_exists(
            phantomime.SELECTOR_TYPE_CSS, span_selector, 15)
    except Exception as e:
        raise Exception(
            f"{span_selector} did not get created - Exception: {e}")

    # this triggers some js code which sets a timeout of 10 seconds until the span gets removed from the dom
    toggle_btn.click()
    try:
        phantomime.wait_element_not_exists(
            phantomime.SELECTOR_TYPE_CSS, span_selector, 15)
    except Exception as e:
        raise Exception(
            f"{span_selector} did not get removed - Exception: {e}")

    # switch to iframe1
    selector = "iframe#iframe1"
    phantomime.switch_to_iframe(phantomime.SELECTOR_TYPE_CSS, selector)

    # check h1 text
    selector = "h1"
    el = phantomime.find_element(phantomime.SELECTOR_TYPE_CSS, selector)
    expected_h1_text = "This is Iframe 1"
    actual_h1_text = el.text
    if actual_h1_text != expected_h1_text:
        raise Exception(
            f"iframe1 h1 text is {actual_h1_text} - expected {expected_h1_text}")

    # switch to iframe2
    selector = "iframe#iframe2"
    phantomime.switch_to_iframe(phantomime.SELECTOR_TYPE_CSS, selector)

    # check h1 text
    selector = "h1"
    el = phantomime.find_element(phantomime.SELECTOR_TYPE_CSS, selector)
    expected_h1_text = "This is Iframe 2"
    actual_h1_text = el.text
    if actual_h1_text != expected_h1_text:
        raise Exception(
            f"iframe1 h1 text is {actual_h1_text} - expected {expected_h1_text}")

    phantomime.switch_to_main()

    # this alerter button is present in the dom but is not in the current viewport
    selector = "button#alerter-out-of-view"
    alerter_btn = phantomime.find_element(
        phantomime.SELECTOR_TYPE_CSS, selector)
    if alerter_btn is None:
        raise Exception(f"{selector} not found")

    # check alerted_btn is in viewport
    if phantomime.is_element_in_viewport(alerter_btn):
        raise Exception(
            f"{selector} should not be visible in the current viewport")

    # scroll to the element so that it becomes visible in the current viewport
    phantomime.scroll_to_element(alerter_btn)
    try:
        phantomime.wait_element_in_viewport(alerter_btn, 10)
    except Exception as e:
        raise Exception(
            f"{selector} did not become visible in the current viewport")

    phantomime.hover_on_element(alerter_btn)
    # when hovering on the button it should become black
    if alerter_btn.get_attribute("class") != "isHovering":
        raise Exception(f"{selector} should have class isHovering")

    # click on button by js and it should show an alert
    phantomime.click_by_js(alerter_btn)

    # wait for alert
    alert = phantomime.wait_for_alert(10)
    alert.accept()

    # execute script that ahows an alert
    phantomime.execute_script("alert('hello')")
    alert = phantomime.wait_for_alert(10)
    alert.accept()

    # find a select element
    selector = "select"
    el = phantomime.find_select_element(phantomime.SELECTOR_TYPE_CSS, selector)
    if el is None:
        raise Exception(f"{selector} not found")

    # add cookie
    cookie_name = "my-cookie"
    cookie_value = "weird value"
    phantomime.add_cookie(cookie_name, cookie_value)
    cookies = phantomime.execute_script("return document.cookie")
    if not all(want in cookies for want in [cookie_name, cookie_value]):
        raise Exception(f"cookie {cookie_name} not correctly set")

    # delete cookie
    phantomime.delete_cookie(cookie_name)
    cookies = phantomime.execute_script("return document.cookie")
    if any(want in cookies for want in [cookie_name, cookie_value]):
        raise Exception(f"cookie {cookie_name} not correctly deleted")

    # get screenshot as base64
    print(phantomime.screenshot(phantomime.SCREENSHOT_OUTPUT_TYPE_BASE64))

    # get screenshot as screenshot.png file
    print(phantomime.screenshot(
        phantomime.SCREENSHOT_OUTPUT_TYPE_FILE, "screenshot"))
except Exception as e:
    print(traceback.format_exc())

phantomime.stop()
