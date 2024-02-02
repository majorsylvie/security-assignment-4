
# TAKEN FROM ZACHARY ROTHSTEIN'S VERY KIND ED POST
# https://edstem.org/us/courses/51032/discussion/4207840?comment=9704860
# https://people.cs.uchicago.edu/~zrothstein/newSeleniumVMCode.txt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from pyvirtualdisplay import Display

HTTP_ONLY='HTTPonly'
HTTPS_ONLY='HTTPSonly'
BOTH_HTTP_AND_HTTPS='both'
NEITHER_HTTP_NOR_HTTPS='neither'

HTTPS='https'
HTTP='http'




def try_one_domain(domain="google.com"):
    """
    function to try a single domain via selenium, will do both 
    the http and https get and return the value to be associated 
    with this domain in the CSV.

    returns one of:
        HTTP_ONLY
        HTTPS_ONLY
        BOTH_HTTP_AND_HTTPS
        NEITHER_HTTP_NOR_HTTPS
    """
    # http first
    print(f"doing domain: {domain}");
    http_response_scheme = None
    try:
        driver.get("http://" + domain)
        # Wait to load the page
        time.sleep(.3)
        http_response_scheme = driver.current_url.split(":")[0]
    except Exception as e:
        print(f"errored during get with: {e}")



    if http_response_scheme == HTTPS:
        return HTTPS_ONLY

    # https
    https_response_scheme = None
    try:
        driver.get("https://" + domain)
        # Wait to load the page
        time.sleep(.3)
        https_response_scheme = driver.current_url.split(":")[0]
    except Exception as e:
        print(f"errored during get with: {e}")

    print(f"response schemes: \n\tHTTP : {http_response_scheme}\n\tHTTPS: {https_response_scheme}")


    # decide output:
    #if http_response_scheme == 


if __name__ == "__main__":
    display = Display(visible=0, size=(800, 600))
    display.start()

    # Set options for headless Chrome
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")  # Bypass OS security model, necessary for Docker containers
    options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

    # Assuming chromedriver is in PATH, otherwise specify the executable path
    driver = webdriver.Chrome(options=options)

    driver.set_page_load_timeout(10)

    print(try_one_domain("squid-cache.org"))


    driver.quit()
    display.stop()
