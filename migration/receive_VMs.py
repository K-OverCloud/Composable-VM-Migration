'''
Created on Nov 15, 2016
@author: Wise Lab
'''

import pyinotify
import os

wm = pyinotify.WatchManager()  # Watch Manager
mask = pyinotify.IN_CLOSE_WRITE | pyinotify.IN_CREATE  # watched events

class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        rcvDir = event.pathname.split("/")
        rcvFile = rcvDir[len(rcvDir)-1]
        
        #Check migration is completed or not
        if rcvFile == 'completed':
           print "\n\n Received complete message, migration completed!!!"
           exit()
        else:                   
           print "Recieving a file named:", rcvFile

    def process_IN_CLOSE_WRITE(self, event):
        rcvDir = event.pathname.split("/")
        rcvFile = rcvDir[len(rcvDir)-1]
        
        #Check migration is completed or not
        if rcvFile == 'completed':
           print "\n\n Received complete message, migration completed!!!"
           exit()
        else:
            print "Completed to recieve the file %s in a directory: %s\n" %(rcvFile,event.pathname)
       
        print "Start to upload image"
        rcvFileSplit = rcvFile.split(".")
        imageName = rcvFileSplit[0]
        #Upload image to glance
        os.system("openstack image create %s --file %s --disk-format qcow2 --container-format bare --public" %(imageName, event.pathname))
        #Create VM using uploaded image
        print "Start to create instance"
        os.system("nova boot --image %s --flavor m1.tiny %s" %(imageName, imageName))

if __name__=='__main__':
    #Get directory to receive images
    receiveDir = str(raw_input("Inpute directory to receive images:"))

    print "Waiting to receive migrated images ...\n"
    handler = EventHandler()
    notifier = pyinotify.Notifier(wm, handler)
    wdd = wm.add_watch(receiveDir, mask, rec=True)

    notifier.loop()
