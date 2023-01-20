# phantomime

Phantomime is an embeddable headless browser package for Python that provides a simplified interface for interacting with web pages using Selenium and Selenium Hub.

## Requirements

- [Docker Engine](https://docs.docker.com/engine/installation/)

## Installation

`pip install git+https://github.com/psyb0t/phantomime.git#egg=phantomime`

## Usage

```python
from phantomime import phantomime

# start the selenium hub container and connect the selenium WebDriver to it
phantomime.start(phantomime.DRIVER_TYPE_FIREFOX)

# load a page
phantomime.load_page("https://www.example.com")

# check if page is ready
phantomime.is_page_ready()

# get page title
print(phantomime.page_title())

# stop the container
phantomime.stop()
```
