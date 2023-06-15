# Phantomime

![phantomime](./assets/phantomime.png)

Phantomime is a Python package that provides a simplified, high-level API for interacting with web pages. It leverages the power of Selenium and Selenium Hub and provides functionality for headless browsing, making it an excellent tool for web scraping, testing, and automation.

## Prerequisites

- [Docker Engine](https://docs.docker.com/engine/installation/)

## Installation

You can install Phantomime directly from its GitHub repository using pip:

```bash
pip install git+https://github.com/psyb0t/phantomime.git#egg=phantomime
```

## Usage

Phantomime provides a variety of functionalities for interacting with web pages. Here is an example of a typical usage scenario:

```python
from phantomime import phantomime

# Start Phantomime with Firefox as the driver
phantomime.start(phantomime.DRIVER_TYPE_FIREFOX)

# Set the page load timeout and window size
phantomime.set_page_load_timeout(30)
phantomime.set_window_size(1280, 720)

# Load a web page
phantomime.load_page("http://psyb0t.github.io/phantomime/test-page/")
```

Please find the comprehensive usage example [here](./example.py).

## Features

- Page interaction: Phantomime provides functions for loading web pages, scrolling, and checking if a page is ready or if certain text is present on a page.
- Element selection: Phantomime allows you to find elements by CSS or XPATH selectors.
- Visibility checks: You can check if an element is visible on the page, or wait for an element to become visible or invisible.
- iFrame handling: Phantomime allows you to switch to different iFrames within a page and interact with their contents.
- JS interactions: Phantomime can trigger JavaScript events like clicks and alerts.
- Cookie manipulation: Phantomime provides functions for adding and deleting cookies.
- Screenshots: You can take screenshots of the page, either as a base64 string or saved directly to a file.

## Troubleshooting

In case of any issues, make sure your Docker Engine is properly installed and running. If you still face issues, you may consider raising an issue in the [issues section](https://github.com/psyb0t/phantomime/issues) of the project repository.

## License

This software is licensed under the terms of the **Do What The Fuck You Want To Public License (WTFPL)**. This license allows you to use the software for any purposes, without any conditions or restrictions unless such restrictions are required by law. You can learn more about the license at http://www.wtfpl.net/about/.

By using this software, you agree to abide by the terms of the **WTFPL**. If you do not agree, please do not use, modify, or distribute the software.
