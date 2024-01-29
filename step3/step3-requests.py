import requests
import logging
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

    if https is None:
        prefix = 'http://'
    else:
        prefix = 'https://'

    test_url = prefix + test_domain 

    try:
        response = requests.get(test_url, timeout=TIMEOUT)
    except requests.exceptions.RequestException as e:  
        logging.warning(f"failed with exception: {e}")
        return None

    response_url = response.url

    return response_url.split(":")[0]

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
    http_request_scheme = try_url_and_get_scheme(domain,https=False)


    HTTP_ONLY='HTTPonly'
    HTTPS_ONLY='HTTPSonly'
    BOTH_HTTP_AND_HTTPS='both'
    NEITHER_HTTP_NOR_HTTPS='neiher'

    HTTPS='https'
    HTTP='http'

    if http_request_scheme == HTTPS:
        # if a site redirect HTTP to HTTPS
        # that means it's only accessible on HTTPS
        return HTTPS_ONLY

    https_request_scheme = try_url_and_get_scheme(domain,https=True)

    # this should never happen!
    if https_request_scheme == HTTP:
        logging.error(f"HTTPS request returned HTTP scheme, sad :(")


    # punnet square of responses
    if http_request_scheme is None and https_request_scheme is None:
        return NEITHER_HTTP_NOR_HTTPS

    elif http_request_scheme == HTTP and https_request_scheme is None:
        return HTTP_ONLY

    elif http_request_scheme is None and https_request_scheme == HTTPS:
        return HTTPS_ONLY

    elif http_request_scheme == HTTP and https_request_scheme == HTTPS:
        return NEITHER_HTTP_NOR_HTTPS


if __name__ == "__main__":
    test_domains = [
        "google.com",
        "facebook.com",
        "github.com",
        "chicagoreader.com",
        "itturnsoutgrantdoesnotlikehotdogs.fyi",
        "squid-cache.org"
    ]
# scheme = try_url_and_get_scheme(test_domain)
for test_domain in test_domains:
    scheme = return_quadrant_for_domain(test_domain)
    print(f"{test_domain} : scheme: {scheme}")
