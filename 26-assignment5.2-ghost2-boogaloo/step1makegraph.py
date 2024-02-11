from typing import List
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests
# file to make the graph in memory via python

"""
Class to represent one individual page

defined as:
    it's own html hash value
    all other hash values that link to it

Constructing the graph is really constructing the edges.
Thus, steps will be:
    webscrape starting from index to find all depth 22 edges.
    ie:
        dfs using requests and beautiful soup to get the Hash values for some page
            keeping track of a depth as you recurse
        want to compartmentalize the code to find the edges and the code to make
        the networkx graph and print it with graphviz

        dictionary of hash : list of hashes
"""


BC = "https://blase.courses/"
def make_url(ghost_hash: int = None)-> str:
    """
    function to take in just a number from the HTML path in blase.courses
    and output a full URL string that can be fed directly to
    browser.get()

    Expects the integer representation of the HTML path:
        eg:
            starting page https://blase.courses/5235101353139427677.html
            is inputted as ghost_hash = 5235101353139427677

        if it get's none, will return the index's URL
    """
    if ghost_hash is None:
        return BC

    url_string = BC + str(ghost_hash) + ".html"
    return url_string



def test_one_webpage(url='https://blase.courses/')-> List[int]:
    """
    function to take one webpage and return the hash values of all the links on it
    """

    html = requests.get(url)
    # print(html.text)
    soup = BeautifulSoup(html.text, "lxml") # lxml is just the parser for reading the html
    links = soup.find_all('a', href=True) # this is the line that does what you want
    print(links)
    for link in links:
        href = link['href']
        path = urlparse(href).path

        # the path here will be of the form:
        #   "/hash_value.html"
        # i just want the hash_value
        path = path.replace("/","")
        # slitting on the . in .html
        path = path.split(".")[0]
        print(path)

def get_neighbors_from_hash_value(hash=None):
    """
    function to take in an individual hash value, and using requests and beautiful soup,
    return the list of all the hash values that are linked on it

    Inputs:
        hash: and integer hash value representing the path of the webpage
              if no hash is provided, this will get the href for the index

    Output:
        list of hash values as integers
    """

    output_list = []

    url = make_url(ghost_hash=hash)

    # url = "https://blase.courses/9120766452599220771.html"
    html = requests.get(str(url))

    # beautiful soup need the text of the webpage so it can
    # scrape anything
    soup = BeautifulSoup(html.text, "lxml")

    # this gets all the href'd <a> elements from the webpage
    links = soup.find_all('a', href=True)
    # print(links)
    for link in links:
        # the "link" variable will be the whole html tag
        # we only want to href key value pair, so we extract it
        href = link['href']

        # now we only want the actual path of the
        # https://blase.courses/[hash_value].html
        # url, so we use urlparse to direct grab it
        # the path here will be of the form:
        #   "/[hash_value].html"
        path = urlparse(href).path

        # i just want the hash_value, get rid of slash and html
        path = path.replace("/","")

        # splitting on the . in .html
        path = path.split(".")[0]
        # print(path)

        path_value = int(path)
        output_list.append(path_value)

    return output_list


if __name__ == "__main__":
    n= get_neighbors_from_hash_value(hash=9120766452599220771)
    print(n)
