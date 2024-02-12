import json
from os import getloadavg
import networkx as nx
from typing import Dict, List, Optional
from typing_extensions import Set
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

def dfs(start=None,depth_limit=22):
    mapping = {}
    dfs_recursive_helper(mapping=mapping, curr_depth=0,depth_limit=depth_limit)
    return mapping

def dfs_recursive_helper(mapping: Dict[int,int] = None,
                         curr_page: Optional[int]=None,
                         visited: Optional[Set[int]] = None,
                         curr_depth: int=0,
                         depth_limit: int =22):


    """
    function to recurse through blase.courses webpages until the depth limit is reached
    recording the mapping of hash value to available hyperlinks in a dictionary

    depth is calculated as "total number of clicks"
    where the ghost is assumed to start on the index page, having done 0 clicks
        thus, clicking on the one link on index to the 5235 webpage would be click 1

    Inputs:
        curr_page: hash value of current node, if None is provided, starts at the index
        visited: a visited set of hash values, if None is provided, will use an empty set
        mapping: dictionary mapping hashvalues to hashvalues, based on what pages link where
        curr_depth: the current depth, as defined above
        depth_limit: fixed limit on the depth  recursion will stop either when there are no more nodes, or the depth limit is reached

    Outputs:
        nothing, mapping variable is updated in place
    """
    # visited set of hash values
    if visited is None:
        visited = set()

    if mapping is None:
        mapping = {}

    neighbors = get_neighbors_from_hash_value(hash=curr_page)

    # now that we've recorded the neighbors, we've successfully visited this link
    # thus add it to the set
    # print(f"curr_page : {curr_page} with type: {type(curr_page)}")
    visited.add(curr_page)
    # print(visited)


    # if this is the last (aka 22nd) click
    if curr_depth == depth_limit:
        mapping[curr_page] = []
        return

    # similarly, now that we've visited this link, add it's neighbors to the growing mapping
    mapping[curr_page] = neighbors

    # otherwise, if we still have more clicks to do, recurse down the neighbors
    # incrementing the click count by one to conceptually represent going from
    # the curr node (which was click number curr_depth)
    # and clicking on another node (setting current node to the neighbor hash value,
    # and increasing click count by one)
    for hash_value in neighbors:
        if hash_value in visited:
            continue
        new_depth = curr_depth + 1
        # recurse!! woooo
        dfs_recursive_helper( curr_page=hash_value, visited=visited, mapping=mapping, curr_depth=new_depth, depth_limit=depth_limit )








def test_neighbors():
    n= get_neighbors_from_hash_value(hash=9120766452599220771)
    for a in n:
        ns = get_neighbors_from_hash_value(hash=a)
        print(f'LAYER DEEPER: {a}')
        print(ns)

    print(n)


def make_digraph_from_json(json_filepath='22_depth_traversal.json'):
    """
    function to take in a json file from the output of dfs()
    and use NetworkX to make a directed graph modeling hyperlinks
    betweeen blase.courses classes.

    This is to then be used to construct a visual representation using graphviz
    """
    # first get the json into memory
    with open(json_filepath, 'r') as readfile:
        hyperlink_json = json.load(readfile)

    print(len(hyperlink_json.keys()))

    G = nx.DiGraph()
    for source,hyperlinks in hyperlink_json.items():
        # print(f"{source} : {hyperlinks}")
        for hash_value in hyperlinks:
            edge = (source,hash_value)
            G.add_edge(*edge)

    print(f"node count: {len(G.nodes)}")
    return G


def traverse_and_save_json(depth_limit=22):
    mapping = dfs(depth_limit=depth_limit)
    # print(mapping)
    filepath = f'{depth_limit}_depth_traversal.json'
    with open(filepath, 'w') as writefile:
        json.dump(mapping,fp=writefile,indent=2)

    return filepath


sdfp -x overlap - scale
sfdp -x -Goverlap=scale -Tsvg dotfile > yoursvghere.svg

if __name__ == "__main__":
    json_filepath = traverse_and_save_json(depth_limit=23)
    make_digraph_from_json(json_filepath)
    json_filepath = traverse_and_save_json(depth_limit=24)
    make_digraph_from_json(json_filepath)
    json_filepath = traverse_and_save_json(depth_limit=22)
    make_digraph_from_json(json_filepath)
    # make_digraph_from_json('22_depth_traversal.json')
