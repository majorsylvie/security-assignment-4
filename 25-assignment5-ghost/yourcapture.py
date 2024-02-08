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
SLEEP_DURATION_IN_SECONDS = 20

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



def get_selenium_browser_options():
    """
    function to only return the chrome_options variable from the example code
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disk-cache-size=0")
    chrome_options.add_argument("--disable-application-cache")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-component-extensions-with-background-pages")
    chrome_options.add_argument("--no-default-browser-check")

    return chrome_options

def get_new_selenium_browser(chrome_options):
    """
    function to setup and return the selenium "browser" object
    as represented in the example

    This is because all we will do is, once the driver is set up, 
    is .get() and .close() the browser. thus I want to abstract away all
    other selenium setup to this function

    Input:
        chrome_options : as returned by get_selenium_browser_options()
    """

    service = ChromeService(executable_path=ChromeDriverManager().install())
    # start the actual driver 
    browser = webdriver.Chrome(service=service, options=chrome_options)

    return browser


def visit_one_page(browser, hash_number=None,sleep=True):
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

    # controlled sleep
    if sleep:
        time.sleep(SLEEP_DURATION_IN_SECONDS)


    browser.quit()

# -------------------------------

PAGES = {
        'index': 'index',
        'ghost_start':5235101353139427677,
        5235101353139427677: [ 802362620749745974, 6845881726168158209, 1541437922809678587],
        }

def visit_all_pages_depth_1():
    """
    helper function to do all the visiting, 
    starting at the index, 
    then the ghost's starting page (5235...)
    then each of the linked pages on 5235 in printed order

    waiting 20 seconds between each, closing the browser like ghost does each time

    thus I can run wireshark while just running this function and get a sample of all the pages! 
    woooo

    Inputs:
        None

    Outputs:
        None, wireshark should capture the packet data
    """

    chrome_options = get_selenium_browser_options()
    first_page = PAGES["ghost_start"]

    # None added such that the index is visited
    hash_number_list = [None, first_page]+ PAGES[first_page]

    for hash_number in hash_number_list:
        make_new_browser_and_visit_page(chrome_options=chrome_options,hash_number=hash_number)

def make_new_browser_and_visit_page(chrome_options,hash_number=None):
    """
    helper to fully create a new browser from the chrome options 
    and visit the page indicated by the hash number.

    If the hash number is None, then visit-one_page will visit the index

    Inputs:
        chrome_options: the same chrome_options to be used for all visits
        hash_number : hash number representing the webpage to visit

    Outputs:
        None
    """
    browser = get_new_selenium_browser(chrome_options)
    visit_one_page(browser=browser,hash_number=hash_number)



if __name__ == "__main__":
    visit_all_pages_depth_1()
