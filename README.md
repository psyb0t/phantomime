# phantomime

Phantomime is an embeddable headless browser package for Python that provides a simplified interface for interacting with web pages using Selenium and Selenium Hub.

## Requirements

- [Docker Engine](https://docs.docker.com/engine/installation/)

## Features

- Support for Firefox and Chrome as the headless browser
- Support for several selector types (CSS, XPath)
- Support for waiting for elements to exist, be visible, not visible
- Support for scrolling to elements
- Support for hovering on elements
- Support for clicking on elements using JavaScript
- Support for scrolling the entire page
- Support for checking if text exists on a page
- Support for taking screenshots of a web page
- Support for waiting for alerts
- Support for loading a page
- Support for getting the page source
- Support for checking if the page is ready
- Support for setting the page load timeout
- Support for setting the window size
- Support for selecting options in select elements
- Support for executing javascript on the page
- Support for clearing cookies

## Installation

`pip install git+https://github.com/psyb0t/phantomime.git#egg=phantomime`

## Usage

```python
import phantomime

# set driver type
phantomime.set_driver_type(phantomime.DRIVER_TYPE_CHROME)

# start the selenium hub container and connect the selenium WebDriver to it
phantomime.start()

# load a page
phantomime.load_page("https://www.example.com")

# check if page is ready
phantomime.is_page_ready()

# get page title
print(phantomime.page_title())

# stop the container
phantomime.stop()
```
