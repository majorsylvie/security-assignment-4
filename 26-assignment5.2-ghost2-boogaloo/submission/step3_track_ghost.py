import networkx as nx
ANALYSIS_OUTPUT_FILEPATH = 'step2_22_depth_packet_capture_attempt_2_analysis.json'
GRAPH_DOTFILE = '22_depth_graph_dotfile.dot'

def track_ghost(graph_dotfile_path=GRAPH_DOTFILE,analysis_output_filepath=ANALYSIS_OUTPUT_FILEPATH):
    """

    """
    G = nx.DiGraph(nx.nx_pydot.read_dot(graph_dotfile_path))
    return G

if __name__ == "__main__":
    track_ghost()
