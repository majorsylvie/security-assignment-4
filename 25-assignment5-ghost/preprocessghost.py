import json
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
    if sent from server 
        "ip.src"
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
if __name__ == "__main__":
    with open("ghost2024.json", "r") as ghost2024:
        packets = json.load(ghost2024)
        flows_dict =generate_flows_dict(packets)
