# copy of non-useragent code :)
import pandas as pd
import requests
from typing import Tuple

debug = True

# thanks alec
def dlog(string):
    if debug:
        print(string)
    else:
        return

TIMEOUT = 10
TOPSITES = "step0-topsites.csv"
OTHERSITES = "step0-othersites.csv"

TOPSITES_OUTPUT = "step3-topsites-useragent.csv"
OTHERSITES_OUTPUT = "step3-othersites-useragent.csv"

FIREFOX_HEADERS = {
    "Host":"websparrow.org",
    "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language":"en-US,en;q=0.5",
    "Accept-Encoding":"gzip, deflate, br",
    "Referer":"https://duckduckgo.com/",
    "DNT":"1",
    "Connection":"keep-alive",
    "Upgrade-Insecure-Requests":"1",
    "Pragma":"no-cache",
    "Cache-Control":"no-cache",
}
CUSTOM_HEADERS_FROM_STEP2_EXAMPLE = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
    "Accept-Encoding": "gzip, deflate", 
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8", 
    "Dnt": "0", 
    "Upgrade-Insecure-Requests": "1", 
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36", 
}

SCRAPE_HERO_BASE_HEADER = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Dnt': '1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/83.0.4103.97 Safari/537.36',
    'X-Amzn-Trace-Id': 'Root=1-5ee7bbec-779382315873aa33227a5df6'}

def try_url_and_get_scheme(domain,https=False):
    """
    function to makea get request to a domain with either
    https or http.
    Defaults to http, but can also do https

    Outputs:
        if successful, outputs the scheme of the response.url
        if it fails, return None

    """

    if not https:
        prefix = 'http://'
    else:
        prefix = 'https://'

    test_url = prefix + domain 

    dlog(f"querying url: {test_url}")
    try:
        # my firefox headers didn't work so I took the ones from step2
        #response = requests.get(test_url, timeout=TIMEOUT, headers=FIREFOX_HEADERS)
        #response = requests.get(test_url, timeout=TIMEOUT, headers=CUSTOM_HEADERS_FROM_STEP2_EXAMPLE)
        headers = SCRAPE_HERO_BASE_HEADER.copy()
        response = requests.get(test_url, timeout=TIMEOUT, headers=SCRAPE_HERO_BASE_HEADER )
        #response = requests.get(test_url, timeout=TIMEOUT)# , headers=CUSTOM_HEADERS_FROM_STEP2_EXAMPLE)
    except requests.exceptions.RequestException as e:  
        dlog(f"failed with exception: {e}")
        return (None,None)
    except:
        dlog(f"OTHER EXCEPTION ON GET")
        return (None,None)

    response_url = response.url
    # dlog(f"response url: {response_url}")

    scheme = response_url.split(":")[0]
    status_code = response.status_code
    return (scheme,status_code)

def return_quadrant_for_domain(domain) -> Tuple[str | None, int | None]:
    """
    function to take a domain name, make at most 2 GET requests
        always makes an HTTP request
        if the HTTP request does not redirect to HTTP:
            then we know that the site is only accessible via HTTPS
        else:
            make an HTTP request.

    regardless of exactly how many requests are made, 
    this function returnings one of the following strings:
        'HTTPSonly'
            if only accessible with HTTPS (such as redirecting)
        'HTTPonly'
            if only accessible with HTTP, failing a HTTPS request
        'both'
            both HTTP and HTTPS requests
        'neither'
    """
    http_request_scheme,http_status_code = try_url_and_get_scheme(domain,https=False)

    HTTP_ONLY='HTTPonly'
    HTTPS_ONLY='HTTPSonly'
    BOTH_HTTP_AND_HTTPS='both'
    NEITHER_HTTP_NOR_HTTPS='neither'

    HTTPS='https'
    HTTP='http'

    # don't cre about https response code
    https_request_scheme,https_status_code = try_url_and_get_scheme(domain,https=True)

    # this should never happen!
    if https_request_scheme == HTTP:
        dlog(f"XXXXXXXXXXXXX HTTPS request returned HTTP scheme, sad :(")

    # if we get both HTTPS and HTTP status codes, then only pick HTTPS
    status_code = None
    if https_status_code is not None:
        dlog(f"choosing only HTTPS status code when given both HTTPS: {http_status_code}, HTTP: {http_status_code}")
        status_code = https_status_code
    else:
        status_code = http_status_code


    # punnet square of responses
    dlog(f"INSIDE RETURN========")
    dlog(f": HTTP  scheme,code : {http_request_scheme}, {http_status_code}")
    dlog(f": HTTPS scheme,code : {https_request_scheme}, {https_status_code}")
    if http_request_scheme is None and https_request_scheme is None:
        dlog(f"\tdouble none")
        return NEITHER_HTTP_NOR_HTTPS,None

    elif http_request_scheme == HTTP and https_request_scheme is None:
        dlog(f"\tONLY HTTP")
        return HTTP_ONLY,status_code

    elif http_request_scheme is None and https_request_scheme == HTTPS:
        dlog(f"\tONLY HTTPS")
        return HTTPS_ONLY,status_code

    elif http_request_scheme == HTTP and https_request_scheme == HTTPS:
        dlog(f"\tBOTH HTTPS AND HTTPS ")
        return BOTH_HTTP_AND_HTTPS,status_code

    # if both the schemes returned HTTPS then HTTP was redirected
    # thus I will record this as HTTPS only since 
    # HTTP traffic was not allowed to actually happen
    elif http_request_scheme == HTTPS and https_request_scheme == HTTPS:
        dlog(f"\tBOTH HTTPS AND HTTPS ")
        return HTTPS_ONLY,status_code
    else:
        dlog(f"\t NONE??????????????\n")
        return None,None

def test_handful():
    test_domains = [
        "google.com",
        "facebook.com",
        "github.com",
        "chicagoreader.com",
        "washington.edu",
        "itturnsoutgrantdoesnotlikehotdogs.fyi",
        "squid-cache.org"
    ]
    
    for test_domain in test_domains:
        scheme,status_code = return_quadrant_for_domain(test_domain)
        print(f"{test_domain} : scheme: {scheme} : status_code: {status_code}")

def try_domain_from_pandas_row(row):
    domain = row['domain']
    scheme,status_code = return_quadrant_for_domain(domain)
    return scheme,status_code
    


def test_small_topsites():
    df = pd.read_csv("topsite_small.csv",names=['ranking','domain'])
    ROW = 1
    application = df.apply(try_domain_from_pandas_row, axis=ROW)

    # https://stackoverflow.com/questions/29550414/how-can-i-split-a-column-of-tuples-in-a-pandas-dataframe
    df[['HTTP availability','status code']] = pd.DataFrame(application.tolist(), index=df.index)
    print(df)


def try_csv(csv_path="topsite_small.csv"):
    df = pd.read_csv(csv_path, names=['ranking','domain'])
    ROW = 1
    application = df.apply(try_domain_from_pandas_row, axis=ROW)

    # https://stackoverflow.com/questions/29550414/how-can-i-split-a-column-of-tuples-in-a-pandas-dataframe
    df[['HTTP availability','status code']] = pd.DataFrame(application.tolist(), index=df.index)

    # actually save the output to avoid misery of a useless long run
    
    # default path for testing input
    output_path = csv_path + "OUTPUT.csv"
    
    # requested output CSV names from assignment
    if csv_path == TOPSITES:
        output_path = TOPSITES_OUTPUT
    elif csv_path == OTHERSITES:
        output_path = OTHERSITES_OUTPUT

    if output_path == csv_path:
        output_path += "_1.csv"

    print(df)
    df.to_csv(output_path)

if __name__ == "__main__":
    try_csv("topsite_small.csv")
    #try_csv(TOPSITES)
    # try_csv(OTHERSITES)

