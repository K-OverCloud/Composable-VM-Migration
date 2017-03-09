import json
import traceback

def getNetworkInfo(file_path):
    data = config_json_read(file_path)
    networkInfo = data["Networks"]

    return networkInfo

def getRouterInfo(file_path):
    data = config_json_read(file_path)
    routerInfo = data["Routers"]

    return routerInfo

def getInstanceInfo(file_path):
    data = config_json_read(file_path)
    instanceInfo = data["VMs"]
    return instanceInfo

def getNameToIP(file_path):
    data = config_json_read(file_path)
    instances = data["VMs"] 
    
    nameToIPInfo = {}
    for instance in instances:
        nameToIPInfo[instance["name"]] = instance["FloatingIP"]
    
    return nameToIPInfo

def getNameToNetwork(file_path):
    data = config_json_read(file_path)
    instances = data["VMs"] 
    networks = data["Networks"]

    nameToNetworkInfo = {}
    for instance in instances:
        for network in networks:
             if network["subnets"][0]["name"] == instance["Subnet"]:
                  networkName = network["name"]
        nameToNetworkInfo[instance["name"]] = networkName
    
    return nameToNetworkInfo

def getFloatingipInfo(file_path):
    data = config_json_read(file_path)
    floatingipInfo = data["FloatingIPs"]

    return floatingipInfo

def config_json_write(file_path, json_data):
    try:
         with open(file_path,"w+") as write_file:
              json.dump(json_data, write_file)
              write_file.close()
    except Exception:
         traceback.print_exc()
         return None

def config_json_read(file_path):
    try:
         with open(file_path,"r") as read_file:
              json_data = json.load(read_file)
              read_file.close()
    except Exception:
              traceback.print_exc()
              return None

    return json_data



