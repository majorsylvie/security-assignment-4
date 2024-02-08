from collections import defaultdict
import json
from typing import Any, DefaultDict, Dict, List, Tuple
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

def generate_flows_dict(packets):
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
    flows: Dict[Optional[Tuple[int,int]],List[Dict[str,int | bool]]] = defaultdict(list)
    
    for packet in packets:
        flow_tuple,slimmed_packet_dict = get_flow_for_and_slim_packet(packet)
        flows[flow_tuple].append(slimmed_packet_dict)

    return flows


        




if __name__ == "__main__":
    with open("ghost2024.json", "r") as ghost2024:
        packets = json.load(ghost2024)
        flows_dict =generate_flows_dict(packets)
