'''
Created on Nov 15, 2016
@author: Wise Lab
'''

import pymysql
import os

   
def stopInstance(instanceName):
    os.system("nova stop "+instanceName)
    print "..................stopping  %s " %(instanceName)
    
    return 0

def takeSnapshot(cursor, instanceName):
    #Check instance status
    active = True 
    
    while active:
         cursor.execute("SELECT vm_state FROM instances WHERE hostname = '"+instanceName+"' ORDER BY id DESC LIMIT 1;")
         vm_state = cursor.fetchone()
         if str(vm_state[0]) == 'stopped':
                     active = False    
    
    print "Stopped: %s \n" %(str(data[i]))

    print "Take a snapshot of the instance %s" %(instanceName) 
    os.system("nova image-create --poll "+instanceName+" "+instanceName)

    return 0

def downloadImage(cursor, instanceName):
    #Check image is created
    imageActive = False
    
    while imageActive:
         cursor.execute("SELECT id FROM images WHERE name = '"+instanceName+"' and status = 'active';")
         imageId = cursor.fetchone()
         if imageId[0]:
              imageActive = True

    print "Snapshot completed, image name: %s \n" %(instanceName)
    
    print "..................downloading image"

    #Get id of the image
    cursor.execute("SELECT id FROM images WHERE name = '"+instanceName+"' and status = 'active';")
    imageId = cursor.fetchone()
    
    #Download image 
    os.system("glance image-download --file ~/images/"+instanceName+".raw "+str(imageId[0]))
    print "Completed to download the image %s \n" %(instanceName)

    return 0

def connectDB(hostIP, hostPort, userID, userPass, dbName):
    dbConnection = pymysql.connect(host = hostIP, port = hostPort, user = userID, passwd = userPass, db = dbName, charset='utf8', autocommit=True)
  
    return dbConnection

def sendFile(fileName, remoteDir):
    os.system("bbcp -P 2 -V -s 16 ~/images/%s %s" %(fileName, remoteDir))

def deleteInstance(instanceName):
    os.system("nova delete %s" %(instanceName))     
 
if __name__=='__main__':
    os.system("figlet WiSe Lab")

    #Get number of VMs to migrate
    getNumber = raw_input("Input number of VMs to migrate:")
    instanceNumber = int(getNumber)
    
    #Get MariaDB access information
    controllerIP = str(raw_input("Input controller IP:"))
    dbPort = int(raw_input("Input DB access port:"))
    userName = str(raw_input("DB user name:"))
    userPass = str(raw_input("DB access password:"))
    
    #Get receiver site host information
    receiverHostName  = str(raw_input("Input receiver host name:"))
    receiverHostIP  = str(raw_input("Input receiver host IP :"))
    receiverDirectory  = str(raw_input("Input directory for receiving images:"))

    #Connect to nova DB
    novaDBconnection = connectDB(controllerIP, dbPort, userName, userPass, 'nova')
    cursor1 = novaDBconnection.cursor()
    cursor2 = novaDBconnection.cursor()

    #Connect to glance DB
    glanceDBconnection = connectDB(controllerIP, dbPort, userName,userPass, 'glance')
    cursor3 = glanceDBconnection.cursor()

    #Get all active host name
    cursor1.execute("SELECT hostname FROM instances WHERE vm_state = 'Active';")
    data = [r[0] for r in cursor1.fetchall()]
    
    #Migrate instances sequencially
    for i in range(instanceNumber): 
        stopInstance(str(data[i]))
        takeSnapshot(cursor2, str(data[i]))
        returnMsgD = downloadImage(cursor3, str(data[i]))
        
        if returnMsgD == 0: 
              deleteInstance(str(data[i]))
              image = str(data[i])+'.raw'
              sendFile(image, receiverHostName+'@'+receiverHostIP+':'+receiverDirectory)   
                 
              print "Migrated an instance %s" %(str(data[i]))
              print "****************************************\n\n"
    
    print "Migration completed, and sent completed message. "
    sendFile('completed', receiverHostName+'@'+receiverHostIP+':'+receiverDirectory)

    #Close DB connections
    novaDBconnection.close()
    glanceDBconnection.close()

