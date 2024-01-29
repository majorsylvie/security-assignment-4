import requests

debug = False

def dlog(string):
    if debug:
        print(string)
    else:
        return

"""
for a webstite:
    request http
    if we redirect:
        output: HTTPSonly
    if http fails:
        make https request

    determin out:
        if both failed:
            output neither
        if http succeeded and https failed:
            output HTTPonly
        if http failed and https succeeded:
            output HTTPSonly
        if both succeded:
            output both
"""

TIMEOUT = 0.5

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

    test_url = prefix + test_domain 

    dlog(f"querying url: {test_url}")
    try:
        response = requests.get(test_url, timeout=TIMEOUT)
    except requests.exceptions.RequestException as e:  
        dlog(f"failed with exception: {e}")
        return (None,None)

    response_url = response.url
    dlog(f"response url: {response_url}")

    scheme = response_url.split(":")[0]
    status_code = response.status_code
    return (scheme,status_code)

def return_quadrant_for_domain(domain):
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
    NEITHER_HTTP_NOR_HTTPS='neiher'

    HTTPS='https'
    HTTP='http'

    dlog(f"http scheme : {http_request_scheme}")

    if http_request_scheme == HTTPS:
        # if a site redirect HTTP to HTTPS
        # that means it's only accessible on HTTPS
        return HTTPS_ONLY,http_status_code

    # don't cre about https response code
    https_request_scheme,_ = try_url_and_get_scheme(domain,https=True)

    # this should never happen!
    if https_request_scheme == HTTP:
        dlog(f"HTTPS request returned HTTP scheme, sad :(")


    dlog(f"https scheme: {https_request_scheme}")

    # punnet square of responses
    if http_request_scheme is None and https_request_scheme is None:
        return NEITHER_HTTP_NOR_HTTPS,None

    elif http_request_scheme == HTTP and https_request_scheme is None:
        return HTTP_ONLY,http_status_code

    elif http_request_scheme is None and https_request_scheme == HTTPS:
        return HTTPS_ONLY,http_status_code

    elif http_request_scheme == HTTP and https_request_scheme == HTTPS:
        return BOTH_HTTP_AND_HTTPS,http_status_code


if __name__ == "__main__":
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
