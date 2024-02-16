from typing import List, Tuple
import networkx as nx
import json

# output file
PATH_GUESS_OUTPUT_FILE = 'step3_guessed_path.txt'

# analysis files
GHOST_MOVEMENT_ANALYSIS_FILE = 'ghost2024_page_to_flows_analysis.json'
# ALL_PAGES_SIDECHANNEL_JSON = 'step2_22_depth_packet_capture_attempt_2_analysis.json'
ALL_PAGES_SIDECHANNEL_JSON = 'step2_bfs_flow_analysis.json'

#BFS traveral file
# UNWEIGHTED_GRAPH_DOTFILE = '22_depth_graph_dotfile.dot'
UNWEIGHTED_GRAPH_DOTFILE = 'bfs_dotfile.dot'
# UPDATED_GRAPH_DOTFILE = '22_depth_post_analysis_graph_dotfile.dot'

class PathWithError():
    def __init__(self, path = None, errors = None, max_length = 22) -> None:
        self.max_length = max_length
        if path is None:
            self.hash_value_path = []
        else:
            self.hash_value_path = path.copy()
        if errors is None:
            self.percent_error_at_each_step = []
        else:
            self.percent_error_at_each_step = errors.copy()

        self._cumulative_error = 0

    def add_node_and_error(self,hash_value: int | None, percent_error: int):
        """
        function to add another node to a path
        """
        # since we were told paths are to hav all unique nodes
        # then I can simply error if you try to add one that's bad
        if hash_value in self.hash_value_path:
            raise ValueError(f"trying to add hash_value already in path: {hash_value}")

        self.hash_value_path.append(hash_value)
        self.percent_error_at_each_step.append(percent_error)

    def pop(self) -> None:
        """
        method to remove the head from the path and errors
        return None
        """
        self.path.pop()
        self.percent_error_at_each_step.pop()

    @property
    def error(self):
        return sum(self.percent_error_at_each_step)

    @property
    def head(self):
        return self.hash_value_path[-1]

    @property
    def path(self):
        return self.hash_value_path

    @property
    def path_len(self):
        return len(self.hash_value_path)

    def __repr__(self):
        output = ""
        output += f"head      : {self.head}\n"
        output += f"path      : {self.path}\n"
        output += f"errors    : {self.percent_error_at_each_step}\n"
        output += f"sum error : {self.error}\n"

        return output

    def copy(self):
        new_path = self.path.copy()
        new_path_errors = self.percent_error_at_each_step.copy()
        max_length = self.max_length

        return PathWithError(path=new_path,errors=new_path_errors,max_length=max_length)

        

    @property
    def done(self) -> bool:
        """
        method to return if the path is complete
        completion being a path of length 22

        and some validation
        """
        if len(set(self.path)) != len(self.path):
            raise ValueError(f"duplicate found in path! set and list of path not same length")

        path_done = self.path_len == self.max_length

        return path_done


# def copy_and_extend_path(source_path: PathWithError) -> PathWithError:
#     pass


def track_ghost(step1_graph_dotfile=UNWEIGHTED_GRAPH_DOTFILE,
                ghost_movement_sidechannel_analysis_filepath=GHOST_MOVEMENT_ANALYSIS_FILE,
                estimated_path_outfile_path=PATH_GUESS_OUTPUT_FILE,
                ) -> List[str | int]:
    """
    function to track the ghost from start till finish, using the 
    sidechannel analysis of all nodes in the network using the 
    updated graph generated from the weighted_graph_dotfile

    then traversing the graph by trying to match the sidechannel information 
    (planned to just be the number of bytes), 
    to then output a path as a List of integers (+ "index" as the first element)

    and write that result to the analysis_output_filepath
    

    """
    g = nx.DiGraph(nx.nx_pydot.read_dot(step1_graph_dotfile))

    ghost_path = json.load(open(GHOST_MOVEMENT_ANALYSIS_FILE,'r'))

    all_paths: List[PathWithError] = []

    def backtrack(candidate_path: PathWithError):
        if candidate_path.done:
            copied_path = candidate_path.copy()
            all_paths.append(copied_path)
            return
        
        # iterate all possible candidates.
        for next_candidate in list_of_candidates:
            if is_valid(next_candidate):
                # try this partial candidate solution
                place(next_candidate)
                # given the candidate, explore further.
                backtrack(next_candidate)
                # backtrack
                remove(next_candidate)

    """
    this will be a list of:
    Tuple (
            Tuple
                ( 
                 path steps as list of integers (all starting with None for the index)
                 ,
                 percent error in total bytes sent from server at each step
                 as list of integers)
                )
            ,
            cumulative error
            )
    """
    all_paths_with_error: List[Tuple[Tuple[List[int | None],List[int]],int]] = []


    return asef

# def update_sitemap_graph_with_sidechannel_analysis(input_graph_path=UNWEIGHTED_GRAPH_DOTFILE,
#                                                    output_graph_dotfile_path=UPDATED_GRAPH_DOTFILE,
#                                                    all_pages_sidechannel_analysis_file=ALL_PAGES_SIDECHANNEL_JSON) -> nx.DiGraph:
#     """
#     function to take the graph found from step 1 and update it with the side channel analysis information
#     collected in step 2

#     this will make the actual traversal easier since then we only have to deal with a weighted graph traversal.

#     Inputs:
#         input_graph_path: the path to the sitemap with no information associated with each node
#         output_graph_dotfile_path: the path to write the newly updated graph's dotfile to

#     Outputs:
#         the in-memory networkx graph
#         also will write the graph as a dotfile to the output_graph_dotfile_path
#     """
#     g = nx.DiGraph(nx.nx_pydot.read_dot(input_graph_path))




#     nx.drawing.nx_pydot.write_dot(g,output_graph_dotfile_path)

if __name__ == "__main__":
    track_ghost()
