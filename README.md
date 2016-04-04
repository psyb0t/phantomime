# Phantomime

A Docker and Selenium powered headless web browser for Python

## Requirements

* [Docker Engine](https://docs.docker.com/engine/installation/)
* [Python bindings for Selenium](http://selenium-python.readthedocs.org/installation.html)

## Initial Steps

```bash
git clone https://github.com/psyb0t/Phantomime.git phantomime
cd phantomime
./update-requirements
```

## Basic Usage

Import Phantomime

```python
from phantomime import Phantomime
```

Set pre-init variables and initialize

```python
Phantomime.verbose = True
Phantomime.window_size = (2560, 1600)
Phantomime.set_driver('firefox')
Phantomime.init()
```

Load a page

```python
page_source = Phantomime.load_page('http://9gag.com/')
```

Wait for page to be ready

```python
if not Phantomime.wait_page_ready(10):
  sys.exit('Page failed to be ready in 10 seconds!')
```

Get page title

```python
page_title = Phantomime.page_title()
```

Perform a scroll-down

```python
Phantomime.scroll_page()
```

Take a screenshot and save it as screenshot_file.png

```python
Phantomime.screenshot('file', 'screenshot_file')
```

## Phantomime module explained

```python
Phantomime.verbose
"""Print general status strings or not

Value:
True of False
"""

Phantomime.window_size
"""The window size

Value:
Two integer value tuple (width, height)
"""

Phantomime.ppy_jQuery
"""The jQuery function name to use when injecting

Value:
Unique function name string
"""

Phantomime.Browser
"""The Selenium Driver element

Available after init()
"""

Phantomime.set_driver(d)
"""Set the Selenium driver to use

Arguments:
d -- driver string (firefox | chrome)
"""

Phantomime.init()
"""Initiate the browser by finding
an unused port for the Selenium server and
an unused container name, then starting the
Selenium server docker machine and connecting
to it
"""

Phantomime.load_page(url)
"""Loads a URL in the browser window

Arguments:
url -- the URL string to be loaded

Returns:
The current page source or False
"""

Phantomime.page_ready()
"""Check if the page has finished loading

Returns:
True or False
"""

Phantomime.wait_page_ready(t=10)
"""Waits for a page to finish loading

Arguments:
t -- the timeout in seconds (default = 10)

Returns:
True or False
"""

Phantomime.page_title()
"""Return the current page title
"""

Phantomime.scroll_page()
"""Scroll the current page down to the
maximum scroll height
"""

Phantomime.page_contains_text(text)
"""Check if the page contains the specified text string

Arguments:
text -- the text string to search for

Returns:
True of False
"""

Phantomime.wait_page_contains_text(text, t=5)
"""Wait for the page to contain the specified text strng

Arguments:
text -- the text string to search for
t -- the timeout in seconds (default = 5)

Returns:
True or False
"""

Phantomime.wait_element_visible(by, sel, t=2)
"""Wait for the specified element to become visible

Arguments:
by -- the type of query used to select the element (XPATH | CSS)
sel -- the selector
t -- the timeout in seconds (default = 2)

Returns:
The first visible Selenium WebDriver Element or False
"""

Phantomime.wait_element_not_visible(by, sel, t=2)
"""Wait for the specified element to become invisible

Arguments:
by -- the type of query used to select the element (XPATH | CSS)
sel -- the selector
t -- the timeout in seconds (default = 2)

Returns:
True or False
"""

Phantomime.wait_element_exists(by, sel, t=2)
"""Wait for the specified element to exist

Arguments:
by -- the type of query used to select the element (XPATH | CSS)
sel -- the selector
t -- the timeout in seconds (default = 2)

Returns:
The first existing Selenium WebDriver Element or False
"""

Phantomime.wait_element_not_exists(by, sel, t=2)
"""Wait for the specified element to not exist

Arguments:
by -- the type of query used to select the element (XPATH | CSS)
sel -- the selector
t -- the timeout in seconds (default = 2)

Returns:
True or False
"""

Phantomime.find_elements(by, sel)
"""Find all elements on page based on selector

Arguments:
by -- the type of query used to select the element (XPATH | CSS)
sel -- the selector

Returns:
List of Selenium WebDriver Elements or False
"""

Phantomime.scroll_to_element(element)
"""Scroll the page to the specified element

Arguments:
element -- the Selenium WebDriver Element to scroll to
"""

Phantomime.hover_on_element(element)
"""Hover over an element

Arguments:
element -- the Selenium WebDriver Element to hover on

Returns:
True of False
"""

Phantomime.click_by_js(element)
"""Clicks on element by triggering .click() using JavaScript

Arguments:
element -- the Selenium WebDriver Element to click

Returns:
True or False
"""

Phantomime.select_option(select_el, by, val)
"""Select an option from a select dropdown

Arguments:
select_el -- the Selenium WebDriver Element select dropdown
by -- the type of the value used (index | text | value)
val -- the value of the option to select
"""

Phantomime.inject_ppy_jquery()
"""Inject jQuery in the page using the Phantomime.ppy_jQuery
variable value as the function name (default = __ppy__jQuery())
"""

Phantomime.runjs(js)
"""Run JavaScript code on the page

Arguments:
js -- the JavaScript code

Returns:
The result of the JavaScript code
"""

Phantomime.wait_for_alert(t=3)
"""Wait for an alert box to be present

Arguments:
t -- the timeout in seconds (default = 3)

Returns:
The alert Selenium object or False
"""

Phantomime.clear_cookies()
"""Clear all cookies set for the current domain
"""

Phantomime.wait(t=10)
"""Wait for a specified amount of seconds

Arguments:
t -- the timeout in seconds (default = 10)
"""

Phantomime.screenshot(t='base64', fname=None)
"""Take a screenshot of the current browser window

Arguments:
t -- the type of the screenshot (default=base64 | raw | file)
fname -- the file name of the .png file (used when t = file; default=None)
"""
```