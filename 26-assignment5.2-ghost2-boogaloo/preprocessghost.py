from collections import defaultdict
import json
from typing import Any, DefaultDict, Dict, List, Optional, Tuple
JSON_FILEPATH = '22_depth_packet_capture_attempt_2_feb12th_730pm.json'
ANALYSIS_OUTPUT_FILEPATH = 'step2_22_depth_packet_capture_attempt_2_analysis.json'
MY_IP='192.168.0.7'
BLASE_IP='128.135.11.239'
PAGES = {
        'index': 'index',
        'ghost_start':5235101353139427677,
        5235101353139427677: [ 802362620749745974, 6845881726168158209, 1541437922809678587],
        }

def generate_flows_dict(packets,my_ip,server_ip):
    """
    function to take in the packets after being loaded from JSON
    and make a dictionary that has sorted all packets by their flow
    where a flow is explicitly defined as the combination of:
        (user port , blase.courses port)
    """

    """
    OOP as follows:
        # PART 1: FLOW IDENTIFICATION:

        Because my code purposefully does a malformed DNS query to 'hash-value-{hash_value}.zzyyzzxx'
        I can identify all the packets belonging to a flow as:
            the packets going between MY_IP and BLASE_IP 
            that are after a DNS (A or AAAA) query to a malformed site.

        This is because I have no parallelization and selenium's browser.get() only returns
        when the webpage has fully loaded, so because I always do:
            DNS .get()
            blase.courses .get()

        I will always find the DNS request first.

        Thus I iterate through the packets, going until I find a DNS A or AAAA record
        to some hash-value-{hash_value}.zzyyzzxx website, then:
            creating an entry for that hash_value in the dictionary (if it wasn't already found)

            then:
                for all subsequent packets until I reach the next DNS query:
                    associate it with a flow and retrieve:
                        whether it was sent by blase
                        the seq number

            thus producing a dictionary of the following:

                webpage hash value : {
                        flow_1 : list of related slimmed packet representation, aka: 
                        [
                            {
                                seq : SEQ NUMBER
                                server_sent : boolean of if packet was sent by server
                            },
                            {
                                another packet
                            },
                        ]
                        (perhaps) flow_2 : 
                        [
                            {
                                seq : SEQ NUMBER
                                server_sent : boolean of if packet was sent by server
                            },
                            {
                                probably another packet
                            },
                        ]
                        },
            next webpage hash value: {
                    same stuff!
                    }

    """
    # optional typing for the key incase the get_flow_for_and_slim_packet 
    # helper function (somehow) can't identify a packets flow

    # interior type of packet dictionary is int or bool as it's either:
    #   an int for time sent and seq value
    #   a boolean for if it was sent by the server
    output_page_to_flows_mapping = defaultdict(dict)

    # default dict so I can guarentee append even if this is the first discovered packet 
    flows: Dict[Optional[Tuple[int,int]],List[Dict[str,int | float | bool]]] = defaultdict(list)

    # string keys typing for testing, explanatory comment in for loop
    # flows: Dict[str,List[Dict[str,int | float | bool]]] = defaultdict(list)
    
    # variable to keep track of the current page we're on
    # will be updated whenever we reach a new malformed DNS query
    # starting as None since we haven't begun iteration
    curr_page_hash_value = None
    for packet in packets:
        src = packet['_source']
        layers = src['layers']

        # first check if this is a DNS packet
        dns = layers.get('dns')
        if dns is not None:
            # then this is a DNS packet, wooo!!!
            hash_value = get_hash_value_from_dns_layer(dns)


        flow_tuple,slimmed_packet_dict = get_flow_for_and_slim_packet(packet,ghost_ip=my_ip,server_ip=server_ip)
        flows[flow_tuple].append(slimmed_packet_dict)

        # alternate key's-as-strings for serializing the JSON and saving in a file
        # to validate that my code behaves as I want in final submission 
        # this flows dict will be disposed of where all I care about is the final data analysis.
        # string_flow_tuple = str(flow_tuple)
        # flows[string_flow_tuple].append(slimmed_packet_dict)

    return flows

def get_hash_value_from_dns_layer(dns) -> int:
    """
    function to take in the DNS layer of a DNS request packet 
    and return the hash value if it was a DNS request of the format:
        (A or AAAA) to:
        hash-value-{hash_value}.zzyyzzxx
    eg:
        hash-value-5235101353139427677.zzyyzzxx

    Inputs:
        dictionary representing the DNS layer of a DNS packet
    
    Outputs:
        hash_value integer if there is one
        None if the packet was a request for a non hash-value-{hash_value}.zzyyzzxx domain
    """
    # check if there is a hash value
    # the Queries field holds a dictionary of query to it's details, such as:
    """
    In [20]: d['Queries']
    Out[20]:
    {'hash-value-5235101353139427677.zzyyzzxx: type AAAA, class IN': {'dns.qry.name': 'hash-value-5235101353139427677.zzyyzzxx',
      'dns.qry.name.len': '39',
      'dns.count.labels': '2',
      'dns.qry.type': '28',
      'dns.qry.class': '0x0001'}}
    """
    queries = dns['Queries']
    for key in queries:
        if "zzyyzzxx" in key:
            # then I know this is for sure a DNS request made by me
            # thus I want to extract the hash value!
            # I know all domains will start with "hash-value-"
            # and that the hash_value I want to extract is always
            # immediately followed by ".zzyyzzxx"
            # thus I get rid of the hash-value- string before
            # and take the first results after splitting the string on the zzyyzzxx
            key = key.replace("hash-value-",'').split(".zzyyzzxx")[0]

            # cast to int because I want to 
            key = int(key)

    # convert hash value to integer

    # win many victories

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

def analyze_pcap(pcap_json_path="ghost2024.json",
                  my_ip=MY_IP,server_ip=BLASE_IP):
    """
    function to, from start till finish, analyze the pcap of all sites visitable with depth 22
    and return dictionary mapping hash_value to the total number of bytes transferred
    """
    with open(pcap_json_path, "r") as pcap_json:
        packets = json.load(pcap_json)
        flows_dict =generate_flows_dict(packets,my_ip=my_ip,server_ip=server_ip)

        analysis_dict = perform_and_print_flow_analysis(flows_dict)

    return analysis_dict




"""
same DNS layers
{
  "dns.id": "0xdda7",
  "dns.flags": "0x0100",
  "dns.flags_tree": {
    "dns.flags.response": "0",
    "dns.flags.opcode": "0",
    "dns.flags.truncated": "0",
    "dns.flags.recdesired": "1",
    "dns.flags.z": "0",
    "dns.flags.checkdisable": "0"
  },
  "dns.count.queries": "1",
  "dns.count.answers": "0",
  "dns.count.auth_rr": "0",
  "dns.count.add_rr": "0",
  "Queries": {
    "hash-value-indexindexindex.zzyyzzxx: type AAAA, class IN": {
      "dns.qry.name": "hash-value-indexindexindex.zzyyzzxx",
      "dns.qry.name.len": "35",
      "dns.count.labels": "2",
      "dns.qry.type": "28",
      "dns.qry.class": "0x0001"
    }
  },
  "dns.response_in": "6"
}
{
  "dns.id": "0xf9c9",
  "dns.flags": "0x0100",
  "dns.flags_tree": {
    "dns.flags.response": "0",
    "dns.flags.opcode": "0",
    "dns.flags.truncated": "0",
    "dns.flags.recdesired": "1",
    "dns.flags.z": "0",
    "dns.flags.checkdisable": "0"
  },
  "dns.count.queries": "1",
  "dns.count.answers": "0",
  "dns.count.auth_rr": "0",
  "dns.count.add_rr": "0",
  "Queries": {
    "hash-value-indexindexindex.zzyyzzxx: type A, class IN": {
      "dns.qry.name": "hash-value-indexindexindex.zzyyzzxx",
      "dns.qry.name.len": "35",
      "dns.count.labels": "2",
      "dns.qry.type": "1",
      "dns.qry.class": "0x0001"
    }
  },
  "dns.response_in": "8"
}
{
  "dns.id": "0x3059",
  "dns.flags": "0x0100",
  "dns.flags_tree": {
    "dns.flags.response": "0",
    "dns.flags.opcode": "0",
    "dns.flags.truncated": "0",
    "dns.flags.recdesired": "1",
    "dns.flags.z": "0",
    "dns.flags.checkdisable": "0"
  },
  "dns.count.queries": "1",
  "dns.count.answers": "0",
  "dns.count.auth_rr": "0",
  "dns.count.add_rr": "0",
  "Queries": {
    "hash-value-indexindexindex.zzyyzzxx: type A, class IN": {
      "dns.qry.name": "hash-value-indexindexindex.zzyyzzxx",
      "dns.qry.name.len": "35",
      "dns.count.labels": "2",
      "dns.qry.type": "1",
      "dns.qry.class": "0x0001"
    }
  },
  "dns.response_in": "26"
}
{
  "dns.id": "0x4c69",
  "dns.flags": "0x0100",
  "dns.flags_tree": {
    "dns.flags.response": "0",
    "dns.flags.opcode": "0",
    "dns.flags.truncated": "0",
    "dns.flags.recdesired": "1",
    "dns.flags.z": "0",
    "dns.flags.checkdisable": "0"
  },
  "dns.count.queries": "1",
  "dns.count.answers": "0",
  "dns.count.auth_rr": "0",
  "dns.count.add_rr": "0",
  "Queries": {
    "hash-value-indexindexindex.zzyyzzxx: type AAAA, class IN": {
      "dns.qry.name": "hash-value-indexindexindex.zzyyzzxx",
      "dns.qry.name.len": "35",
      "dns.count.labels": "2",
      "dns.qry.type": "28",
      "dns.qry.class": "0x0001"
    }
  },
  "dns.response_in": "60"
}
"""

if __name__ == "__main__":
    page_analysis_dict = analyze_pcap(JSON_FILEPATH)
    
    # ghost_analysis_json = json.dumps(ghost_analysis_dict,indent=2)
    with open(ANALYSIS_OUTPUT_FILEPATH, 'w') as ghost_analysis_json_file:
        json.dump(page_analysis_dict,fp=ghost_analysis_json_file,indent=2)

