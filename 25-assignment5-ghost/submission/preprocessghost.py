from collections import defaultdict
import json
from typing import Any, DefaultDict, Dict, List, Optional, Tuple
PAGES = {
        'index': 'index',
        'ghost_start':5235101353139427677,
        5235101353139427677: [ 802362620749745974, 6845881726168158209, 1541437922809678587],
        }

"""
we want data organized into flows

make a dict with: (ghostport , serverport)
    access ip, ip.src
        if ip/src == 192.168.1.101:
            then store tcp tcp.srcport, tcp tcp.dstport
        else if ip ip.src == 125.135.11.239:
            then store tcp tcp.dstport, tcp tcp.srcport

for each packet in a flow:
    tcp flags
    start and end time
    seq and ack number
        "ip.src"
    if sent from server 
    individual length
        frame frame.len IS A STRING NOT A NUMBER
        ""
"""

def generate_flows_dict(packets,ghost_ip,server_ip):
    """
    function to take in the packets after being loaded from JSON
    and make a dictionary that has sorted all packets by their flow
    where a flow is explicitly defined as the combination of:
        (user port , blase.courses port)
    """

    """
    OOP as follows:
        # PART 1: FLOW IDENTIFICATION:

        we must first figure out what flow to put this packet in before we 
        slim down its representation.

        A flow of packets is defined, by course staff, as exactly:
            (ghost tcp port, server tcp port)

        Thus we must find the TCP ports and, using our external knowledge 
        of what ghost and blase.courses IP's are, map those to 
        either being the ghost or the server

            Then after successfully identifying which ports are who's
            construct the literal tuple 
                (ghost tcp port, server tcp port)
            which will be used for the outputted dictionary's key.

            But before we actually do anything to this dictionary 
            it would be good to slim down the packet into 
            a representation that only has the fields I want
            for data analysis, leading to...


        # PART 2: PACKET RE-REPRESENTATION (for storage in flow dict list entry)

        because there's too much shit in JSON 
        that is not relevant to the data analysis

        my end goal is to be able to say the following, 
        per flow:
            total amount of bytes sent
            start and end times

        thus we need to capture the following information from a packet:

            time sent
                I'll use the relative time in seconds as reported 
                by wireshark since those are more readable numbers 
                than time since epoch or the full date in CST or UTC.

            seq value
                because across one flow, the seq value is monotonic increasing
                and represents the number of bytes successfully sent, 
                the maximum seq value in a flow should represent 
                the end total bytes sent, 
               
                however, there are two seq numbers per flow, 
                one for ghost, one from blase courses.
                and the actual direction that matters
                for side channel analysis is the data
                sent FROM blase.courses TO ghost
                    since the total data sent from the server
                    is where the size of each webpage loaded
                    would actually manifest.

                    all the ghost is doing is closing the browser
                    then making a GET request for a URL.

                    which is why we record the last field:

            if packet was sent from blase.courses (ip = 128.135.11.239)
                because then I can easily parse on this field 
                when trying to calculate the max Seq sent by the server

                and conversely I can also use this to find the max
                Ack number sent by the client to sanity check 
                that they are within a few bytes of one another
                    (allowing some tolerance because of RST's)
    """
    # optional typing for the key incase the get_flow_for_and_slim_packet 
    # helper function (somehow) can't identify a packets flow

    # interior type of packet dictionary is int or bool as it's either:
    #   an int for time sent and seq value
    #   a boolean for if it was sent by the server

    # default dict so I can guarentee append even if this is the first discovered packet 
    flows: Dict[Optional[Tuple[int,int]],List[Dict[str,int | float | bool]]] = defaultdict(list)

    # string keys typing for testing, explanatory comment in for loop
    # flows: Dict[str,List[Dict[str,int | float | bool]]] = defaultdict(list)
    
    for packet in packets:
        flow_tuple,slimmed_packet_dict = get_flow_for_and_slim_packet(packet,ghost_ip=ghost_ip,server_ip=server_ip)
        flows[flow_tuple].append(slimmed_packet_dict)

        # alternate key's-as-strings for serializing the JSON and saving in a file
        # to validate that my code behaves as I want in final submission 
        # this flows dict will be disposed of where all I care about is the final data analysis.
        # string_flow_tuple = str(flow_tuple)
        # flows[string_flow_tuple].append(slimmed_packet_dict)

    return flows

def get_flow_for_and_slim_packet(packet,ghost_ip,server_ip) -> Tuple[Optional[Tuple[int,int]],Dict[str,int | float | bool]]:
    """
    Function to take in an individual full packet as an in-memory dict
    made from the JSON exported directly from some wireshark packet capture
    and report both the tuple of:
        (ghost tcp ip, server tcp ip)

    as well as the following per packet:
        time sent
        seq value
        if packet was sent from blase.courses (ip = 128.135.11.239)

    Inputs:
        packet : dictionary representing a packet
        ghost_ip : the IP to consider as the ghost's IP
        server_ip : the IP to consider as the server IP

    both the ghost_ip and server_ip are given default arguments that are specific
    to the 2024 ghost packet capture, but this code can be generalized
    to adapt to any ghost and server port since the logic would 
    remain unchanged.

    Outputs:
        Tuple of:
            optional( int tuple ) of (ghost tcp port, server tcp port)
                to be used as the key in the larger flows dictionary

                optional to gracefully handle if we can't match a packet
                to a flow

            slimmed packet dictionary containined three fields:
                'time': relative time as as a float
                'seq' : sequence number as an integer
                'server_sent' : boolean of whether the packet was sent by the server
                                (where server is whatever the inputted server_ip arg is)

    """
    try:
        src = packet['_source']
        layers = src['layers']
        frame = layers['frame']
    except KeyError as e:
        raise KeyError(f"SOMEHOW got a packet with no src/layers/frame, error message: [{e}]");

    ip  = layers['ip']
    tcp = layers['tcp']
        
    port_tuple = get_flow_port_tuple(ip=ip,tcp=tcp,ghost_ip=ghost_ip,server_ip=server_ip)

    slimmed_packet = slim_packet(frame=frame,ip=ip,tcp=tcp,ghost_ip=ghost_ip,server_ip=server_ip)

    return (port_tuple,slimmed_packet)



def slim_packet(frame,ip,tcp,ghost_ip,server_ip) -> Dict[str,int | float | bool]:
    """
    Function to take in the frame, ip, and tcp layers of a packet 
    and return a dictionary of the slimmed representation. 

    Inputs:
        frame, ip, tcp : all dictionaries extracted representing identically named layers
                         inside a wireshark packet json

        ghost_ip : ip to consider as the "ghost" 
        server_ip : ip to consider as the "server"
            used for determining whether the packet was sent by the server

    Outputs:
        slimmed packet dictionary containined three fields:
            'time': relative time as as a float
            'seq' : sequence number as an integer
            'server_sent' : boolean of whether the packet was sent by the server
                            (where server is whatever the inputted server_ip arg is)
    """

    # conversion to float as all fields in exported json are strings
    relative_time = float(frame['frame.time_relative'])

    seq_number = int(tcp['tcp.seq'])

    # now determine if packet was sent by the server
    sent_by_server = None
    source_ip = ip['ip.src']

    if source_ip == server_ip:
        sent_by_server = True

    elif source_ip == ghost_ip:
        sent_by_server = False

    if sent_by_server is None:
        raise ValueError(f"got packet that was sent from neither ghost nor server ip, instead had ip: [{source_ip}]")


    # after assumbling all components of the slimmed packet,
    # let's make the dang dictionary
    slimmed_packet = {
            'time' : relative_time,
            'seq'  : seq_number,
            'server_sent' : sent_by_server
            }

    return slimmed_packet

def get_flow_port_tuple(ip,tcp,ghost_ip,server_ip) -> Optional[Tuple[int,int]]:
    """
    Function to take in the ip and tcp information from a packet
    and generate the tuple of:
        (ghost tcp port, server tcp port)

    Inputs:
        ip : ip dictionary for a wireshark packet
        tcp : tcp dictionary for a wireshark packet

        ghost_ip : ip to consider as the "ghost" 
        server_ip : ip to consider as the "server"

    Output:
        optional( int tuple ) of (ghost tcp port, server tcp port)
    """
    source_ip = ip['ip.src']
    dest_ip = ip['ip.dst']

    source_port =  tcp['tcp.srcport']
    dest_port = tcp['tcp.dstport']

    ghost_port = None
    server_port = None
    if source_ip == ghost_ip:
        ghost_port  = source_port
        server_port = dest_port

    elif source_ip == server_ip:
        server_port = source_port
        ghost_port  = dest_port

    # if we somehow failed to distinguish ports 
    # then we can't make a tuple of ghost,server, hence return None
    if ghost_port is None or server_port is None:
        return None


    # otherwise, if no errors occurred and we assigned the ghost and server port

    # cast to int
    ghost_port = int(ghost_port)
    server_port = int(server_port)

    # then successfully return my tuple!
    return (ghost_port,server_port)

"""
JSON field checking:

src = packet['_source']

layers = src['layers']

frame = layers['frame']
    relative_time = frame['frame.time_relative']

ip = layers['ip']
    ip['ip.src']
    ip['ip.dst']

tcp = layers['tcp']
    tcp['tcp.srcport']
    tcp['tcp.dstport']
    tcp['tcp.seq']
    tcp['tcp.ack']
    tcp['tcp.flags_tree']

"""

def perform_and_print_flow_analysis(flows):
    """
    Function take in the prepared flows dictionary and print to stdout 
    the data analysis wanted per flow.

    Specifically this will be:
        max serverside seq, representing the total number of bytes sent by the server
        min and max time

    Inputs:
        flows dictionary from generate_flows_dict()

    Outputs:
        dictionary storing the desired statistics per flow
        using stringified keys from the flows dictionary
        such that the outputted dictionary can be directly
        serialized to JSON
        
        will have fields:
            total_bytes_from_server : integer of the total bytes sent from the server to ghost on this flow
            min_time : minimum relative time
            max_time : maximum relative time
            time_range_string : stringified representation of the min and max time

    """
    analysis_dict = {}
    for flow_tuple_key,flow_packet_list in flows.items():
        flow_analysis_values_dict = analyze_one_flow(flow_packet_list)

        # stringify key to allow easy JSON serialization
        flow_key = str(flow_tuple_key)

        analysis_dict[flow_key] = flow_analysis_values_dict

    return analysis_dict

def analyze_one_flow(flow_packet_list):
    """
    function to take in the list of slimmed packets for single flow 
    and output the analysis dictionary to be used 
    in the larger analysis dictionary in perform_and_print_flow_analysis

    Inputs:
        flow_packet_list : list of dictionaries, each one representing a single packet in the flow

    Output:
        dictionary with (key : values):
            total_bytes_from_server : integer of the total bytes sent from the server to ghost on this flow
            min_time : minimum relative time
            max_time : maximum relative time
            time_range_string : stringified representation of the min and max time
    """
    # get total bytes
    # since we only want the seq numbers from server traffic, I add the if at the end of the generator
    server_seqs = [packet['seq'] for packet in flow_packet_list if packet['server_sent']]
    total_bytes_from_server = max(server_seqs)

    # time work
    times = [packet['time'] for packet in flow_packet_list]

    min_time = min(times)
    max_time = max(times)

    # cast to int for cleaner representation in string
    time_range_string = "[" + str(int(min_time)) + ", " + str(int(max_time)) + "]"

    # with parts assembled, make the dictionary!
    analysis_dict = {
            "total_bytes_from_server" : total_bytes_from_server,
            "min_time" : min_time,
            "max_time" : max_time,
            "time_range_string" : time_range_string
            }

    return analysis_dict

def analyze_ghost(ghost_json_path="ghost2024.json",
                  ghost_ip="192.168.1.101",server_ip="128.135.11.239"):
    """
    function to, from start till finish, analyze the ghost packet capture flows
    and return what I want
    """
    with open(ghost_json_path, "r") as ghost2024:
        packets = json.load(ghost2024)
        flows_dict =generate_flows_dict(packets,ghost_ip=ghost_ip,server_ip=server_ip)

        analysis_dict = perform_and_print_flow_analysis(flows_dict)

    return analysis_dict

if __name__ == "__main__":
    ghost_analysis_dict = analyze_ghost()
    
    # ghost_analysis_json = json.dumps(ghost_analysis_dict,indent=2)
    with open('ghost2024_analysis.json', 'w') as ghost_analysis_json_file:
        json.dump(ghost_analysis_dict,fp=ghost_analysis_json_file,indent=2)


