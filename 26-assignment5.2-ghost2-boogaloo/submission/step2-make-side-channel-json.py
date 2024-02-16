from collections import defaultdict
import json
from typing import Any, DefaultDict, Dict, List, Optional, Tuple
JSON_FILEPATH = "bfs.json"
# JSON_FILEPATH = "22_depth_packet_capture_attempt_2_feb12th_730pm.json"
# JSON_FILEPATH = "small.json"
HASH_VALUE_TO_FLOWS_MIDDLE_ANALYSIS_JSON = 'bfs_middle_analysis.json'

ANALYSIS_OUTPUT_FILEPATH = 'step2_bfs_flow_analysis.json'
# ANALYSIS_OUTPUT_FILEPATH = 'middle_analysis.json'
MY_IP='192.168.0.107'
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
    # print(f"top of generate flows dict")
    # optional typing for the key incase the get_flow_for_and_slim_packet 
    # helper function (somehow) can't identify a packets flow

    # interior type of packet dictionary is int or bool as it's either:
    #   an int for time sent and seq value
    #   a boolean for if it was sent by the server
    output_page_to_flows_mapping = defaultdict(dict)


    # string keys typing for testing, explanatory comment in for loop
    # flows: Dict[str,List[Dict[str,int | float | bool]]] = defaultdict(list)
    
    # variable to keep track of the current page we're on
    # will be updated whenever we reach a new malformed DNS query
    # starting as None since we haven't begun iteration
    curr_page_hash_value = None

    # will get grows as we encounter more packets
    # variable to keep track of the flows for the current page
    # then get associated with the curr_page_hash_value  in output_page_to_flows_mapping
    # when we find a new hash value
    curr_flows = defaultdict(list)

    for packet in packets:
        src = packet['_source']
        layers = src['layers']

        # first check if this is a DNS packet
        dns = layers.get('dns')
        # print(f"packet: {layers.keys()}")
        if dns is not None:
            print(f"DNS")
            # then this is a DNS packet, wooo!!!
            hash_value = get_hash_value_from_dns_layer(dns)

            if hash_value is not None and hash_value not in output_page_to_flows_mapping:
                # this means we are at the beggining of a new flow! 
                # since if the hash value was already in the output_page_to_flows_mapping 
                # then we've already found a DNS request for this hash_value
                # which would make sense since both A and AAAA records 
                # were being sent for the zzyyzzxx domains, so there could easily be 2 dns requests per hash

                # if this has happened, then I want to make sure that the flows dictionary
                # that has been previously built up get stored in the output dictionary
                # before we start making new flows for the new webpage
                if curr_page_hash_value is None:
                    curr_page_hash_value = hash_value
                elif curr_page_hash_value is not None:
                    # checking to make sure we have something to record
                    # print(f"saving current flows: {curr_flows}");
                    # print(f"saving: curr flows: {json.dumps(curr_flows,indent=2)}")
                    if curr_flows:
                        print(f"saving curr flows")
                        output_page_to_flows_mapping[curr_page_hash_value] = curr_flows

                    # now update current page
                    curr_page_hash_value = hash_value

                    # reset the current flows since we've moved on to a new page
                    curr_flows = defaultdict(list)

        else:
            print(f"NON DNS: {curr_page_hash_value}")
            # print(f"{curr_page_hash_value}")
            # then we're dealing with a non DNS packet
            # time to flow B)
            flow_tuple,slimmed_packet_dict = get_flow_for_and_slim_packet(packet,my_ip=my_ip,server_ip=server_ip)
            flow_tuple = str(flow_tuple)
            curr_flows[flow_tuple].append(slimmed_packet_dict)

        
        # alternate key's-as-strings for serializing the JSON and saving in a file
        # to validate that my code behaves as I want in final submission 
        # this flows dict will be disposed of where all I care about is the final data analysis.
        # string_flow_tuple = str(flow_tuple)
        # flows[string_flow_tuple].append(slimmed_packet_dict)

    print(curr_flows)
    output_page_to_flows_mapping[curr_page_hash_value] = curr_flows
    
    return output_page_to_flows_mapping

def get_hash_value_from_dns_layer(dns) -> int | None:
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

    output_hash_value = None

    queries = dns['Queries']
    # print(f"{queries}")
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

            if key == "indexindexindex":
                key = 0
            else:
                key = int(key)

            output_hash_value = key
        else:
            pass
            # print(f"failed to find")

    # win many victories
    return output_hash_value

def get_flow_for_and_slim_packet(packet,my_ip,server_ip) -> Tuple[Optional[Tuple[int,int]],Dict[str,int | float | bool]]:
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
        my_ip : the IP to consider as my's IP
        server_ip : the IP to consider as the server IP

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
        
    port_tuple = get_flow_port_tuple(ip=ip,tcp=tcp,my_ip=my_ip,server_ip=server_ip)

    slimmed_packet = slim_packet(ip=ip,tcp=tcp,my_ip=my_ip,server_ip=server_ip)

    return (port_tuple,slimmed_packet)



def slim_packet(ip,tcp,my_ip,server_ip) -> Dict[str,int | float | bool]:
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
            'seq' : sequence number as an integer
            'server_sent' : boolean of whether the packet was sent by the server
                            (where server is whatever the inputted server_ip arg is)
    """


    seq_number = int(tcp['tcp.seq'])

    # now determine if packet was sent by the server
    sent_by_server = None
    source_ip = ip['ip.src']

    if source_ip == BLASE_IP:
        sent_by_server = True

    elif source_ip == MY_IP:
        sent_by_server = False

    if sent_by_server is None:
        raise ValueError(f"got packet that was sent from neither ghost nor server ip, instead had ip: [{source_ip}]")


    # after assumbling all components of the slimmed packet,
    # let's make the dang dictionary
    slimmed_packet = {
            'seq'  : seq_number,
            'server_sent' : sent_by_server
            }

    return slimmed_packet

def get_flow_port_tuple(ip,tcp,my_ip,server_ip) -> Optional[Tuple[int,int]]:
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
    if source_ip == my_ip:
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
        total_flow_bytes = analyze_one_flow(flow_packet_list)

        # stringify key to allow easy JSON serialization
        flow_key = str(flow_tuple_key)

        analysis_dict[flow_key] = total_flow_bytes

    # return flow_analysis_values_dict
    return analysis_dict

def analyze_one_flow(flow_packet_list):
    """
    function to take in the list of slimmed packets for single flow 
    and output the analysis dictionary to be used 
    in the larger analysis dictionary in perform_and_print_flow_analysis

    Inputs:
        flow_packet_list : list of dictionaries, each one representing a single packet in the flow

    Output:
        total_bytes_from_server : integer of the total bytes sent from the server to ghost on this flow
    """
    # get total bytes
    # since we only want the seq numbers from server traffic, I add the if at the end of the generator
    server_seqs = [packet['seq'] for packet in flow_packet_list if packet['server_sent']]
    try:
        total_bytes_from_server = max(server_seqs)
    except:
        total_bytes_from_server = 0
    return total_bytes_from_server


def analyze_pcap(pcap_json_path="ghost2024.json",
                  my_ip=MY_IP,server_ip=BLASE_IP):
    """
    function to, from start till finish, analyze the pcap of all sites visitable with depth 22
    and return dictionary mapping hash_value to the total number of bytes transferred
    """
    with open(pcap_json_path, "r") as pcap_json:
        packets = json.load(pcap_json)
        flows_dict =generate_flows_dict(packets=packets,my_ip=my_ip,server_ip=server_ip)

        return flows_dict

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

def get_final_analysis_from_slimmed_flows(middle_analysis_json_path):
    """
    function to take in the middle analysis, which will have:
        page:
            list of flows:
                each flow containing all the packets
                and if they were sent from the server


    Into a dictionary (and serialized into json) with format:

        page:
            total bytes sent from server
            list of:
                flow : server bytes in flow
    """
    with open(middle_analysis_json_path, "r") as middle_analysis_json:
        page_dict = json.load(middle_analysis_json)

        pages = {}
        for page,flow_list in page_dict.items():
            # dictionary to store total information for the page
            page_details_dict = {}

            # dictionary mapping flow to total number of bytes
            flow_list_analysis_dict = perform_and_print_flow_analysis(flow_list)

            page_total_bytes = 0
            page_total_flows = 0
            for flow,total_bytes in flow_list_analysis_dict.items():
                page_total_flows += 1
                page_total_bytes += total_bytes
            
            page_details_dict['total bytes'] = page_total_bytes
            page_details_dict['total flows'] = page_total_flows
            page_details_dict['flows'] = flow_list_analysis_dict
            pages[page] = page_details_dict


    with open(ANALYSIS_OUTPUT_FILEPATH, 'w') as analysis_file:
        print(f"saving to {ANALYSIS_OUTPUT_FILEPATH}")

        json.dump(pages,fp=analysis_file,indent=2)


if __name__ == "__main__":
    print(f"starting")
    page_analysis_dict = analyze_pcap(JSON_FILEPATH)
    
    # print(json.dumps(page_analysis_dict,indent=2))
    # page_analysis_dict = json.dumps(ghost_analysis_dict,indent=2)
    
    with open(HASH_VALUE_TO_FLOWS_MIDDLE_ANALYSIS_JSON, 'w') as ghost_analysis_json_file:
        print(f"saving to {HASH_VALUE_TO_FLOWS_MIDDLE_ANALYSIS_JSON}")

        json.dump(page_analysis_dict,fp=ghost_analysis_json_file,indent=2)


    get_final_analysis_from_slimmed_flows(HASH_VALUE_TO_FLOWS_MIDDLE_ANALYSIS_JSON)
