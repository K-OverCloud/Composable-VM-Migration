'''
Created on March 2, 2017
@author: Jargal, Hani
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
from glanceclient import Client as glanceClient
from glanceclient.common import utils as utilsGlance

from getClient import *
from utils import *
from neutronConfig import *
from novaConfig import *
from glanceConfig import *
from getConfigurations import *


logging.basicConfig(filename = log_dir ,level=logging.DEBUG)
logger = logging.getLogger()


wm = pyinotify.WatchManager()  # Watch Manager
mask = pyinotify.IN_CLOSE_WRITE | pyinotify.IN_CREATE  # watched events

# OpenStack authentication
controllerIP = raw_input("Controller IP:")
username = raw_input("User id:")
password = raw_input("Password:")
project_name = raw_input("Project name:")
user_domain_name = raw_input("User domain name:")
project_domain_name = raw_input("Project domain name:")

#Directories
log_dir = ""
config_file_path = ""
images_path = " "
remote_dir = ""
completed_file_dir = ""

#Migration order list
migrationOrder = []

class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        rcvDir = event.pathname.split("/")
        rcvFile = rcvDir[len(rcvDir)-1]
        print "Recieving a file named:", rcvFile

    def process_IN_CLOSE_WRITE(self, event):
        rcvDir = event.pathname.split("/")
        rcvFile = rcvDir[len(rcvDir)-1]

        if rcvFile == 'configurationCompleted':
           print "\n Received configuration completed message from destination, migration start!!!"
           startMigration(nova, glance, migrationOrder, images_path, remote_dir)

def sendFile(filePath, remoteDir):
    os.system("bbcp -P 2 -V -s 16 %s %s" %(filePath, remoteDir))

def deleteInstance(instanceName):
    os.system("nova delete %s" %(instanceName))     

def startMigration(nova, glance, migrationOrder, images_path, remoteDir):
    print "Start Migration"
    for instanceName in migrationOrder: 
        stopInstance(nova, instanceName)
        snapshotId = takeSnapshot(nova, instanceName)
        if snapshotId:
              downloadImage(glance, snapshotId, instanceName, images_path)
        image = instanceName+'.raw'
        time.sleep(5)
        sendFile(images_path+image, remoteDir)   
                 
        print "Migrated an instance %s" %(instanceName)
        print "****************************************\n\n"
    
    print "Migration completed, and sent completed message. "
    sendFile(completed_file_dir, remoteDir)
    
    exit()


if __name__== '__main__':
    os.system("figlet WiSe Lab")
    nova = getNovaClient(controllerIP, username, password, project_name, user_domain_name, project_domain_name)
    neutron = getNeutronClient(controllerIP, username, password, project_name, user_domain_name, project_domain_name)
    glance = getGlanceClient(controllerIP, username, password, project_name, user_domain_name, project_domain_name)

    updateHostConfig(config_file_path, nova, neutron)
    updateNetworkConfig(config_file_path, neutron)
    sendFile(config_file_path, remote_dir)
    
    handler = EventHandler()
    notifier = pyinotify.Notifier(wm, handler)
    wdd = wm.add_watch(images_path, mask, rec=True)
    
    notifier.loop()
