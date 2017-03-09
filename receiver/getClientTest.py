from keystoneauth1.identity import v3
from keystoneauth1 import session
from novaclient import client as novClient
from neutronclient.v2_0 import client as neutClient
from neutronConfig import *
from utils import *

def getNeutronClient(controllerIP, username, password, project_name, user_domain_name, project_domain_name):
    auth = v3.Password(auth_url= 'http://'+controllerIP+':35357/v3',
                           username = username,
                           password= password,
                           project_name = project_name,
                           user_domain_name = user_domain_name,
                           project_domain_name = project_domain_name)
    sess = session.Session(auth=auth)
    neutron = neutClient.Client(session=sess)
    return neutron

def getNovaClient(controllerIP, username, password, project_name, user_domain_name, project_domain_name):
    auth = v3.Password(auth_url= 'http://'+controllerIP+':35357/v3',
                           username = username,
                           password= password,
                           project_name = project_name,
                           user_domain_name = user_domain_name,
                           project_domain_name = project_domain_name)
    sess = session.Session(auth=auth)
    nova = novClient.Client("2.1", session=sess)

    return nova

def configureNetwork(configFilePath, neutronClient, novaClient):
    networks = getNetworkInfo(configFilePath)

    for networkInfo in networks:
          network =  createNetwork(neutronClient, networkInfo["name"], "true", networkInfo["external"],networkInfo["network_type"], networkInfo["shared"])
          print "Created a network:", networkInfo["name"]
          networkID = network["network"]["id"]
          for subnet in networkInfo["subnets"]:
               createSubnet(neutronClient, subnet["name"], subnet["cidr"], subnet["ip_version"], networkID)
               print "Created a subnet %s in the network %s" %(subnet["name"], networkInfo["name"]) 
           
    routers = getRouterInfo(configFilePath)

    for routerInfo in routers:
         network_name = routerInfo["external_gateway_info"]["network"]
         network_id = novaClient.networks.find(label=network_name).id
         for subnet in neutronClient.list_subnets()["subnets"]:
              if subnet["network_id"] == network_id:
                        subnet_id = subnet["id"]
         name =  routerInfo["name"]
         admin_state_up = routerInfo["admin_state_up"]
         enable_snat =  routerInfo["external_gateway_info"]["enable_snat"]
         ip_address =  routerInfo["external_gateway_info"]["external_fixed_ips"][0]["ip_address"]

         router = createRouter(neutronClient, name, network_id, enable_snat, ip_address, subnet_id, admin_state_up)
         if router:
             print "Created a router:", name

    for networkInfo in networks:
        external = networkInfo["external"]
        if  str(external) == "False":
               networkName = networkInfo["name"]
               network_id = novaClient.networks.find(label=networkName).id  
               for subnet in neutronClient.list_subnets()["subnets"]:
                     if subnet["network_id"] == network_id:
                          subnet_id = subnet["id"]
                          connectSubnetToRouter(neutronClient, router["router"]["id"], subnet_id)
                          print "Connected the subnet %s to the rourer %s" %(subnet["name"], router["router"]["name"])

if __name__=='__main__':
    neutron =  getNeutronClient('172.26.17.153', 'admin', '2229', 'admin', 'default', 'default')
    nova =  getNovaClient('172.26.17.153', 'admin', '2229', 'admin', 'default', 'default')
    #networkInfo = {'name': 'mynetwork', 'admin_state_up': True, 'router:external':True, 'provider:network_type':'vxlan', 'shared': True}
    """networkID =  nova.networks.find(label='Extnet').id
    for subnet in  neutron.list_subnets()["subnets"]:
              if subnet["network_id"] == networkID:
                      subnetID = subnet["id"]
    router = createRouter(neutron, "routerTest", networkID, "true", "172.26.17.49", subnetID, "true") 
    print router["router"]["id"]  """
    configFilePath = "/home/controller2/testCode/configuration.json"
    configureNetwork(configFilePath, neutron, nova)
