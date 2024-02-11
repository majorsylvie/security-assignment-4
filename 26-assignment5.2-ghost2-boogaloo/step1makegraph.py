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

if __name__ == "__main__":
    test_one_webpage()
