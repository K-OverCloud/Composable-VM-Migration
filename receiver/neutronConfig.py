def createNetwork(neutronClient, name, admin_state_up, external, network_type, shared):
    networkInfo  = {"name": name, 
                    "admin_state_up": admin_state_up, 
                    "router:external": external, 
                    "provider:network_type": network_type, 
                    "shared": shared}       
    network = neutronClient.create_network({'network':networkInfo})
   
    return network

def createSubnet(neutronClient, name, cidr, ip_version, network_id):
    subnetInfo = {"name": name,
                  "cidr": cidr,
                  "ip_version": ip_version,
                  "network_id": network_id
                 }
    subnet = neutronClient.create_subnet({'subnet':subnetInfo})
    
    return subnet

def createRouter(neutronClient, name, network_id, enable_snat, ip_address, subnet_id, admin_state_up):
    routerInfo = {"name": name ,"external_gateway_info":{ "network_id": network_id, "enable_snat": enable_snat,"external_fixed_ips":[{"ip_address": ip_address, "subnet_id": subnet_id}]}, "admin_state_up": admin_state_up}
    router = neutronClient.create_router({"router":routerInfo})
     
    return router

def connectSubnetToRouter(neutronClient, router_id, subnet_id):
    
    neutronClient.add_interface_router(router_id, {"subnet_id": subnet_id})

