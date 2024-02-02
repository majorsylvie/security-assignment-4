
# TAKEN FROM ZACHARY ROTHSTEIN'S VERY KIND ED POST
# https://edstem.org/us/courses/51032/discussion/4207840?comment=9704860
# https://people.cs.uchicago.edu/~zrothstein/newSeleniumVMCode.txt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from pyvirtualdisplay import Display
import pandas as pd
from multiprocessing import Process

HTTP_ONLY='HTTPonly'
HTTPS_ONLY='HTTPSonly'
BOTH_HTTP_AND_HTTPS='both'
NEITHER_HTTP_NOR_HTTPS='neither'

HTTPS='https'
HTTP='http'

TOPSITES='step0-topsites.csv'
OTHERSITES='step0-othersites.csv'



def try_one_domain(driver,domain="google.com"):
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
    if http_response_scheme == HTTP and https_response_scheme == HTTPS:
        return BOTH_HTTP_AND_HTTPS
    if http_response_scheme == HTTP and https_response_scheme is None:
        return HTTP_ONLY
    if http_response_scheme is None and https_response_scheme == HTTPS:
        return HTTPS_ONLY
    if http_response_scheme is None and https_response_scheme is None:
        return NEITHER_HTTP_NOR_HTTPS
    else:
        print(f"FAILED TO PARSE HTTPS RESPONSE CODE")
        print(f"response schemes: \n\tHTTP : {http_response_scheme}\n\tHTTPS: {https_response_scheme}")
        return None

def try_domain_from_pandas_row(row,driver):
    domain = row['domain']
    result = try_one_domain(driver,domain=domain)
    return result

def try_csv(driver,csv_path="topsite_small.csv"):
    df = pd.read_csv(csv_path, names=['ranking','domain'])
    ROW = 1
    df['http result'] = df.apply(try_domain_from_pandas_row, driver=driver, axis=ROW)

    # default path for testing input
    output_path = csv_path + "OUTPUT.csv"

    # requested output CSV names from assignment
    if csv_path == TOPSITES:
        output_path = "step4-topsites-certs.csv"
    elif csv_path == OTHERSITES:
        output_path = "step4-othersites-certs.csv"

    if output_path == csv_path:
        output_path += "_1.csv"

    print(df)
    # drop previous headers
    df = df[df['domain'] != 'domain']
    df.to_csv(output_path, index=False)

def run_it_all(top=True):
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
    try_csv(driver=driver)
    return

    if top:
        try_csv(csv_path=TOPSITES,driver=driver)
    else:
        try_csv(csv_path=OTHERSITES,driver=driver)

    driver.quit()
    display.stop()


if __name__ == "__main__":
    run_it_all(top=True)
    #run_it_all(top=False)
