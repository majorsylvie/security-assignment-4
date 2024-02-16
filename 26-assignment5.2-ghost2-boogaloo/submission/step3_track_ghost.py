from typing import List
import networkx as nx
ALL_PAGES_SIDECHANNEL_JSON = 'step2_22_depth_packet_capture_attempt_2_analysis.json'
UNWEIGHTED_GRAPH_DOTFILE = '22_depth_graph_dotfile.dot'
UPDATED_GRAPH_DOTFILE = '22_depth_post_analysis_graph_dotfile.dot'
PATH_GUESS_OUTPUT_FILE = 'step3_guessed_path.txt'


# analysis files
GHOST_MOVEMENT_ANALYSIS_FILE = 'ghost2024_page_to_flow_analysis'

def track_ghost(step1_graph_dotfile=UNWEIGHTED_GRAPH_DOTFILE,
                ghost_movement_sidechannel_analysis_filepath=GHOST_MOVEMENT_ANALYSIS_FILE,
                estimated_path_outfile_path=PATH_GUESS_OUTPUT_FILE,
                graph=None) -> List[str | int]:
    """
    function to track the ghost from start till finish, using the 
    sidechannel analysis of all nodes in the network using the 
    updated graph generated from the weighted_graph_dotfile

    then traversing the graph by trying to match the sidechannel information 
    (planned to just be the number of bytes), 
    to then output a path as a List of integers (+ "index" as the first element)

    and write that result to the analysis_output_filepath
    

    """
    if graph is None:
        g = nx.DiGraph(nx.nx_pydot.read_dot(step1_graph_dotfile))
    else:
        g = graph
    return asef

def update_sitemap_graph_with_sidechannel_analysis(input_graph_path=UNWEIGHTED_GRAPH_DOTFILE,
                                                   output_graph_dotfile_path=UPDATED_GRAPH_DOTFILE,
                                                   all_pages_sidechannel_analysis_file=ALL_PAGES_SIDECHANNEL_JSON) -> nx.DiGraph:
    """
    function to take the graph found from step 1 and update it with the side channel analysis information
    collected in step 2

    this will make the actual traversal easier since then we only have to deal with a weighted graph traversal.

    Inputs:
        input_graph_path: the path to the sitemap with no information associated with each node
        output_graph_dotfile_path: the path to write the newly updated graph's dotfile to

    Outputs:
        the in-memory networkx graph
        also will write the graph as a dotfile to the output_graph_dotfile_path
    """
    g = nx.DiGraph(nx.nx_pydot.read_dot(input_graph_path))




    nx.drawing.nx_pydot.write_dot(g,output_graph_dotfile_path)

if __name__ == "__main__":
    track_ghost(step1_graph_dotfile=UNWEIGHTED_GRAPH_DOTFILE,ghost_movement_sidechannel_analysis_filepath=GHOST_MOVEMENT_ANALYSIS_FILE,estimated_path_outfile_path=PATH_GUESS_OUTPUT_FILE,graph=None)
