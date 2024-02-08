import json
from preprocessghost import *

if __name__ == "__main__":
    server_ip="128.135.11.239"
    my_ip="192.168.0.107"
    yourself_analysis_dict = analyze_ghost(ghost_json_path='yourcapture.json',ghost_ip=my_ip,server_ip=server_ip)
    
    # yourself_analysis_json = json.dumps(yourself_analysis_dict,indent=2)
    with open('yourself2024_analysis.json', 'w') as yourself_analysis_json_file:
        json.dump(yourself_analysis_dict,fp=yourself_analysis_json_file,indent=2)


