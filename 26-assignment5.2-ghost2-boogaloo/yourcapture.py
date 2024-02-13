# be sure to run the following first:
# python3 -m pip install selenium
# python3 -m pip install webdriver-manager

import json
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

BC = 'https://blase.courses/'
SLEEP_DURATION_IN_SECONDS = 10
DNS_TIMEOUT_DURATION_IN_SECONDS = 0.1
PAGES = {
        'index': 'index',
        'ghost_start':5235101353139427677,
        5235101353139427677: [ 802362620749745974, 6845881726168158209, 1541437922809678587],
        }

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


def visit_one_page(browser, hash_number=None):
    """
    function to visit a single page for a particular browser

    Will also add issue a DNS request as a flag to mark right before visiting a page

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

    plant_dns_flag(browser=browser,hash_number=hash_number)
    # url must be well constructed now as 
    # we've guarenteed to have an output from make_url
    browser.get(url)

    browser.quit()


def make_dns_flag_url(hash_number):
    """
    function to make a malicious malformed url for the DNS flag planting strategy.
    Will be of format:

        hash-value-{hash_number}.zzyyzzxx

    Inputs:
        hash_number : optional integer, None meaning index

    Output:
        string for the url
    """
    if hash_number is not None:
        hash_string = str(hash_number)
    else:
        # having fun with urls :)
        hash_string = "indexindexindex"

    url = "http://hash-value-" + hash_string + ".zzyyzzxx"
    return url

def plant_dns_flag(browser,hash_number):
    """
    function to take in a hash number and make a malformed DNS A record request
    to:

        hash-value-{hash_number}.zzyyzzxx
    
    This will be used to easily tell me when each new website is being visited

    Because selenium is run in series, there are never multiple requests
    Specifically, selenium's browser.get() will not return until the entire contents of the page finish loading
    Thus, by placing these DNS requests, when parsing the packet capture from wireshark, all I have to do is parse packets until I find a DNS 
    query, then see if its of the form 

        hash-value-{hash_number}.zzyyzzxx

    and immediately after the next packets sent between my IP and 128.135.11.239 will be for sure the next flow!

    Inputs:
        browser : selenium browser instance, hopefully generated from get_new_selenium_browser()
        hash_number : optional integer for the hash number, None means we're visiting the index

    Outputs:
        none, should just do browser.get()
    """
    url = make_dns_flag_url(hash_number)
    
    # make timeout really short since we literally do not at all care about getting an actual response
    browser.set_page_load_timeout(DNS_TIMEOUT_DURATION_IN_SECONDS)
    try:
        browser.get(url)
    except Exception as e:
        print(f"selenium probably timed out: {e}")
    browser.set_page_load_timeout(SLEEP_DURATION_IN_SECONDS)

def visit_all_nodes_in_json(json_filepath='22_depth_traversal.json'):
    """
    helper function to do all the visiting, 
    based on the nodes in a json file that captures all possible nodes 
    in a 22-depth traversal of blase.courses

    waiting SLEEP_DURATION_IN_SECONDS seconds between each, closing the browser like ghost does each time

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
    hash_number_list = get_node_list_from_json(json_filepath)

    for hash_number in hash_number_list:
        make_new_browser_and_visit_page(chrome_options=chrome_options,hash_number=hash_number)

def get_node_list_from_json(json_filepath='22_depth_traversal.json'):
    """
    function to get all the nodes to visit for selenium
    when given a json file representing all the pages and links
    between blase.courses sites
    """
    with open(json_filepath, 'r') as readfile:
        hyperlink_json = json.load(readfile)

        # None representing the index
        output = [None]

        for hash_string in hyperlink_json.keys():
            # index stored with key 'null' in JSON
            # can't convert null into an integer
            # which is why None is preadded to the output list
            if hash_string != 'null':
                hash_value = int(hash_string)
                # print(f"{hash_value}, {type(hash_value)}")
                output.append(hash_value)

        return output


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
    visit_all_nodes_in_json()
