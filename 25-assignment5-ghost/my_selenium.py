# be sure to run the following first:
# python3 -m pip install selenium
# python3 -m pip install webdriver-manager
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

BC = 'https://blase.courses/'
def make_url(ghost_hash: int)-> str:
    """
    function to take in just a number from the HTML path in blase.courses
    and output a full URL string that can be fed directly to 
    browser.get()

    Expects the integer representation of the HTML path:
        eg:
            starting page https://blase.courses/5235101353139427677.html
            is inputted as ghost_hash = 5235101353139427677
    """
    url_string = BC + str(ghost_hash) + ".html "
    return url_string




def get_selenium_browser():
    """
    function to setup and return the selenium "browser" object
    as represented in the example

    This is because all we will do is, once the driver is set up, 
    is .get() and .close() the browser. thus I want to abstract away all
    other selenium setup to this function
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disk-cache-size=0")
    chrome_options.add_argument("--disable-application-cache")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-component-extensions-with-background-pages")
    chrome_options.add_argument("--no-default-browser-check")

    service = ChromeService(executable_path=ChromeDriverManager().install())
    # start the actual driver 
    browser = webdriver.Chrome(service=service, options=chrome_options)

    # at this point, my code will visit a link, then close the browser with 
    # browser.close()

def visit_one_page(browser, hash_number=None):
    """
    function to visit a single page for a particular browser

    Inputs:
        hash_number: numeric representation of the html page, 
                     using the syntax of needed in make_url

                     default is None, which will call on the index.html

    Outputs:
        None
    """
    url = None
    if hash_number is None:
        url = make_url(PAGES['index'])
    else:
        assert isinstance(hash_number,int)
        url = make_url(hash_number)

    if url is None:
        raise ValueError(f'somehow still had an empty URL after everything in visit_one_page with hash_number: {hash_number}')

    # url must be well constructed now as 
    # we've guarenteed to have an output from make_url
    browser.get(url)

# -------------------------------

PAGES = {
        'index': 'index',
        'ghost_start':5235101353139427677,
        5235101353139427677: [ 802362620749745974, 6845881726168158209, 1541437922809678587],
        }

if __name__ == "__main__":
    print(make_url(PAGES[5235101353139427677][0]))
