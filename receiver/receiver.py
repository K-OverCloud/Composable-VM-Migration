'''
Created on March 7, 2017
@author: Jax, Hani
'''

import pyinotify
import os
import time

import json
import traceback
import logging

from keystoneauth1.identity import v3
from keystoneauth1 import session
from novaclient import client as novClient
from neutronclient.v2_0 import client as neutClient

from getClient import *
from utils import *
from neutronConfig import *
from novaConfig import *
from glanceConfig import *

logging.basicConfig(filename='~/composableMigration/log/receiver.log',level=logging.DEBUG)
logger = logging.getLogger()


wm = pyinotify.WatchManager()  # Watch Manager
mask = pyinotify.IN_CLOSE_WRITE | pyinotify.IN_CREATE  # watched events

controllerIP = raw_input("Controller IP:")
username = raw_input("User id:")
password = raw_input("Password:")
project_name = raw_input("Project name:")
user_domain_name = raw_input("User domain name:")
project_domain_name = raw_input("Project domain name:")

#Directories
config_completed_dir = ""
remote_dir = ""
config_file_path = ""
images_file_path = ""

class EventHandler(pyinotify.ProcessEvent):
    
    def process_IN_CREATE(self, event):
        rcvDir = event.pathname.split("/")
        rcvFile = rcvDir[len(rcvDir)-1]
        
        if rcvFile == 'completed':
           print "Received complete message, migration completed!!!"
           exit()
        else:                   
           print "Recieving a file named:", rcvFile
   
    def process_IN_CLOSE_WRITE(self, event):
        rcvDir = event.pathname.split("/")
        rcvFile = rcvDir[len(rcvDir)-1]
        
        if rcvFile == "configuration.json":
            os.system("chmod o+r ~/images/configuration.json")
            configureNetwork( event.pathname, neutron, nova)
            sendFile(config_completed_dir, remote_dir)
        elif rcvFile == 'completed':
           print "Received complete message, migration completed!!!"
           exit()
        else:
           print "Completed to recieve the file %s in a directory: %s\n" %(rcvFile,event.pathname)
           rcvFileSplit = rcvFile.split(".")
           imageName = rcvFileSplit[0]
           
           print "Start to upload image"
           uploadImage(glance, imageName, event.pathname)
           
           print "Start to create a VM"
           instance(imageName, config_file_path, nova) 
            
def sendFile(fileDir, remoteDir):
    os.system("bbcp -P 2 -V -s 16 %s %s" %(fileDir, remoteDir))
          
def instance(name, config_file_path, novaClient):
     networkList = getNameToNetwork(config_file_path)
     print networkList[name]
     instance = createInstance(novaClient, name, networkList[name])
     print "completed to create a VM \n"
     
     floatingIPList = getNameToIP(config_file_path)
     addFloatingIP(novaClient, instance.name, floatingIPList[name])
     print "Allocated floating IP %s" %(floatingIPList[name])



def configureNetwork(config_file_path, neutronClient, novaClient):
    networks = getNetworkInfo(config_file_path)

    for networkInfo in networks:
          network =  createNetwork(neutronClient, networkInfo["name"], "true", networkInfo["external"],networkInfo["network_type"], networkInfo["shared"])
          print "Created a network:", networkInfo["name"]
          networkID = network["network"]["id"]
          for subnet in networkInfo["subnets"]:
               createSubnet(neutronClient, subnet["name"], subnet["cidr"], subnet["ip_version"], networkID)
               print "Created a subnet %s in the network %s" %(subnet["name"], networkInfo["name"])

    routers = getRouterInfo(config_file_path)

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
    nova = getNovaClient(controllerIP, username, password, project_name, user_domain_name, project_domain_name)
    neutron = getNeutronClient(controllerIP, username, password, project_name, user_domain_name, project_domain_name)
    glance = getGlanceClient(controllerIP, username, password, project_name, user_domain_name, project_domain_name)

    handler = EventHandler()
    notifier = pyinotify.Notifier(wm, handler)
    wdd = wm.add_watch(images_file_path, mask, rec=True)
    
    print "Waiting to receive migrated images ...\n"

    notifier.loop()
