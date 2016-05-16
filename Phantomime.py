import os
import base64
import atexit

from time import sleep
from random import choice
from subprocess import check_output, Popen
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

verbose = True
"""Print general status strings or not

Value:
True of False
"""

window_size = (2560, 1600)
"""The window size

Value:
Two integer value tuple (width, height)
"""

ppy_jQuery = '__ppy__jQuery'
"""The jQuery function name to use when injecting

Value:
Unique function name string
"""

driver = 'firefox'
abs_path = os.path.dirname(os.path.realpath(__file__))
jQuery_file = '%s/jquery.js' % abs_path
Browser = None

def set_driver(d):
  """Set the Selenium driver to use
  
  Arguments:
  d -- driver string (firefox | chrome)
  """
  global driver
  
  d = d.lower()
  supported_drivers = ['firefox', 'chrome']
  if d not in supported_drivers:
    raise Exception(
      'Invalid driver. Supported: %s' % ', '.join(supported_drivers)
    )
  
  driver = d
  
  return True

def start_docker_machine(container_name, port):
  if verbose:
    print 'Starting docker machine %s...' % container_name
  
  try:
    Popen(
      ('/usr/bin/env docker run --rm --name="%s" -p 127.0.0.1:%s:4444 '
      'selenium/standalone-%s >> /dev/null') % (
        container_name, str(port), driver
      ), shell=True
    )
    
    return True
  except:
    return False

def docker_machine_running(container_name, t=30, c=1):
  if c >= t:
    return False
  
  if verbose:
    print 'Checking docker machine %s is running [%s/%s]...' % (
      container_name, str(c), str(t)
    )
  
  docker_ps_a = check_output(
    '/usr/bin/env docker ps -a', shell=True
  )
  
  if not container_name in docker_ps_a:
    sleep(1)
    c += 1
    return docker_machine_running(container_name, t, c)
  
  return True

def stop_docker_machine(container_name):
  if verbose:
    print 'Stopping docker machine %s...' % container_name
  
  try:
    check_output(
      '/usr/bin/env docker stop %s' % container_name,
      shell=True, stderr=open(os.devnull, 'w')
    )
    
    return True
  except:
    return False

def connect_to_selenium(port, t=30, c=1):
  global Browser
  
  if c >= t:
    return False
  
  try:
    if verbose:
      print ('Connecting to docker selenium server '
      'http://127.0.0.1:%s/wd/hub [%s/%s]...') % (str(port), str(c), str(t))
    
    if driver == 'chrome':
      desired_caps = DesiredCapabilities.CHROME
    elif driver == 'firefox':
      desired_caps = DesiredCapabilities.FIREFOX
    
    Browser = webdriver.Remote(
      command_executor='http://127.0.0.1:%s/wd/hub' % str(port),
      desired_capabilities=desired_caps
    )
  except:
    c += 1
    sleep(1)
    connect_to_selenium(port, t, c)
  
  return True

def new_container_name():
  docker_ps_a = check_output(
    '/usr/bin/env docker ps -a', shell=True
  )
  container_name = 'selenium-%s-%s' % (driver, str(
    choice(range(100000, 500000)))
  )
  while container_name in docker_ps_a:
    container_name = choice(range(100000, 500000))
  
  return container_name

def new_local_port():
  netstat = check_output(
    '/usr/bin/env netstat -lpn', shell=True
  )
  port = str(choice(range(5000, 10000)))
  while ':%s' % port in netstat:
    port = str(choice(range(5000, 10000)))
  
  return int(port)

def init():
  """Initiate the browser by finding
  an unused port for the Selenium server and
  an unused container name, then starting the
  Selenium server docker machine and connecting
  to it
  
  Returns:
  Two value tuple (container_name, container_port)
  """
  container_port = new_local_port()
  container_name = new_container_name()
  
  atexit.register(stop_docker_machine, container_name)
  start_docker_machine(container_name, container_port)

  if not docker_machine_running(container_name):
    raise Exception('Failed to start Selenium docker machine')

  if not connect_to_selenium(container_port):
    raise Exception('Could not connect to Selenium server')
  
  Browser.set_window_size(window_size[0], window_size[1])
  
  return (container_name, container_port)

def load_page(url):
  """Loads a URL in the browser window
  
  Arguments:
  url -- the URL string to be loaded
  
  Returns:
  The current page source or False
  """
  if verbose:
    print 'Loading page %s...' % url
  
  try:
    Browser.get(url)
    
    if verbose:
      print 'Current page title: %s...' % page_title()
    
    return Browser.page_source
  except:
    return False

def page_ready():
  """Check if the page has finished loading
  
  Returns:
  True or False
  """
  if verbose:
    print 'Checking page ready...'
  
  return Browser.execute_script(
    'return document.readyState == "complete";'
  )

def wait_page_ready(t=10, c=1):
  """Waits for a page to finish loading
  
  Arguments:
  t -- the timeout in seconds (default = 10)
  
  Returns:
  True or False
  """
  if verbose:
    print 'Browser wait page ready [%s/%s]...' % (str(c), str(t))
  
  if c >= t:
    return False
  
  if not page_ready():
    sleep(1)
    c += 1
    return wait_page_ready(t, c)
  
  return True

def page_title():
  """Return the current page title
  """
  return Browser.title

def scroll_page():
  """Scroll the current page down to the
  maximum scroll height
  """
  if verbose:
    print 'Scrolling page...'
  
  return runjs('window.scrollTo(0, document.body.scrollHeight);')

def page_contains_text(text):
  """Check if the page contains the specified text string
  
  Arguments:
  text -- the text string to search for
  
  Returns:
  True of False
  """
  if verbose:
    print 'Checking if page contains text...'
  
  if find_elements('XPATH', '//*[contains(text(), "%s")]' % text):
    return True
  
  return False

def wait_page_contains_text(text, t=5, c=1):
  """Wait for the page to contain the specified text strng
  
  Arguments:
  text -- the text string to search for
  t -- the timeout in seconds (default = 5)
  
  Returns:
  True or False
  """
  if verbose:
    print 'Waiting for page to contain text "%s"... [%s/%s]' % (text, c, t) 
  
  if c >= t:
    return False
  
  if not page_contains_text(text):
    sleep(1)
    c += 1
    return wait_page_contains_text(text, t, c)
  
  return True

def wait_element_visible(by, sel, t=2):
  """Wait for the specified element to become visible
  
  Arguments:
  by -- the type of query used to select the element (XPATH | CSS)
  sel -- the selector
  t -- the timeout in seconds (default = 2)
  
  Returns:
  The first visible Selenium WebDriver Element or False
  """
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

def wait_element_not_visible(by, sel, t=2):
  """Wait for the specified element to become invisible
  
  Arguments:
  by -- the type of query used to select the element (XPATH | CSS)
  sel -- the selector
  t -- the timeout in seconds (default = 2)
  
  Returns:
  True or False
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

def wait_element_exists(by, sel, t=2):
  """Wait for the specified element to exist
  
  Arguments:
  by -- the type of query used to select the element (XPATH | CSS)
  sel -- the selector
  t -- the timeout in seconds (default = 2)
  
  Returns:
  The first existing Selenium WebDriver Element or False
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

def wait_element_not_exists(by, sel, t=2):
  """Wait for the specified element to not exist
  
  Arguments:
  by -- the type of query used to select the element (XPATH | CSS)
  sel -- the selector
  t -- the timeout in seconds (default = 2)
  
  Returns:
  True or False
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

def find_elements(by, sel):
  """Find all elements on page based on selector
  
  Arguments:
  by -- the type of query used to select the element (XPATH | CSS)
  sel -- the selector
  
  Returns:
  List of Selenium WebDriver Elements or False
  """
  if verbose:
    print 'Finding %s:%s...' % (by, sel)
  
  if by not in ['XPATH', 'CSS', 'CSS_SELECTOR']:
    raise Exception('Invalid SELECT BY type')
  
  if by == 'CSS':
    by = 'CSS_SELECTOR'
  
  try:
    return Browser.find_elements(getattr(By, by), sel)
  except:
    return False

def scroll_to_element(element):
  """Scroll the page to the specified element
  
  Arguments:
  element -- the Selenium WebDriver Element to scroll to
  """
  if verbose:
    print 'Scrolling to element...'
  
  return Browser.execute_script(
    'return arguments[0].scrollIntoView(true);', element
  )

def hover_on_element(element):
  """Hover over an element
  
  Arguments:
  element -- the Selenium WebDriver Element to hover on
  
  Returns:
  True of False
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

def click_by_js(element):
  """Clicks on element by triggering .click() using JavaScript
  
  Arguments:
  element -- the Selenium WebDriver Element to click
  
  Returns:
  True or False
  """
  if verbose:
    print 'Clicking on element by js...'
  
  try:
    Browser.execute_script('arguments[0].click();', element)
    return True
  except:
    return False

def select_option(select_el, by, val):
  """Select an option from a select dropdown
  
  Arguments:
  select_el -- the Selenium WebDriver Element select dropdown
  by -- the type of the value used (index | text | value)
  val -- the value of the option to select
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

def inject_ppy_jquery():
  """Inject jQuery in the page using the Phantomime.ppy_jQuery
  variable value as the function name (default = __ppy__jQuery())
  """
  if verbose:
    print 'Injecting Phantomime.py jQuery...'
  
  with open(jQuery_file, 'r') as f:
    runjs(f.read().replace(
      '__ppy__jQuery', ppy_jQuery
    ).replace('__ppy__$', ppy_jQuery))

def runjs(js):
  """Run JavaScript code on the page
  
  Arguments:
  js -- the JavaScript code
  
  Returns:
  The result of the JavaScript code
  """
  if verbose:
    print 'Running JavaScript code...'
  
  return Browser.execute_script(js)

def wait_for_alert(t=3):
  """Wait for an alert box to be present
  
  Arguments:
  t -- the timeout in seconds (default = 3)
  
  Returns:
  The alert Selenium object or False
  """
  if verbose:
    print 'Waiting for alert to pop...'
  
  try:
    WebDriverWait(Browser, t).until(EC.alert_is_present())
    
    return Browser.switch_to_alert()
  except TimeoutException:
    return False

def clear_cookies():
  """Clear all cookies set for the current domain
  """
  Browser.delete_all_cookies()

def wait(t=10, c=1):
  """Wait for a specified amount of seconds
  
  Arguments:
  t -- the timeout in seconds (default = 10)
  """
  if verbose:
    print 'Browser wait [%s/%s]...' % (str(c), str(t))
  
  if c >= t:
    return True
  
  sleep(1)
  c += 1
  return wait(t, c)

def screenshot(t='base64', fname=None):
  """Take a screenshot of the current browser window
  
  Arguments:
  t -- the type of the screenshot (default=base64 | raw | file)
  *fname -- the file name of the .png file (used when t = file; default=None)
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