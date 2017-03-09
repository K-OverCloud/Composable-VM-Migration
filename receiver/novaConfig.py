from keystoneauth1.identity import v3
from keystoneauth1 import session
from novaclient import client as novClient
from neutronclient.v2_0 import client as neutClient

def createInstance(novaClient, name, network):
   try:
        notActive = True
        while notActive:
                image = novaClient.images.find(name=name)
                if image.status == 'ACTIVE':
                        notActive = False
        print "Image uploaded\n"

        print "Create instance : %s" %(name)
        image = novaClient.images.find(name=name)
        flavor = novaClient.flavors.find(name="m1.small")
        net = novaClient.networks.find(label=network)
        nics = [{'net-id': net.id}]
        instance = novaClient.servers.create(name=name, image=image, flavor=flavor, nics=nics)
        return instance
   except Exception as e:
        print str(e)

def takeSnapshot(nova, instanceName):
    try:
	active = True
        while active:
        	instance = nova.servers.find(name=instanceName)
        	if instance.status == 'SHUTOFF':
                	active = False
        print "Stopped : %s \n" %(instanceName)

        print "Take snapshot of the instance : %s" %(instance.name)
        snapshot = nova.servers.create_image(instance.id, instance.name)
	print "Snapshot created\n"
        return snapshot
    except Exception as e:
        print(str(e))

def stopInstance(nova, instanceName):
    try:
        instance = nova.servers.find(name=instanceName)
        if instance.status == 'ACTIVE':
                print "Stop instance: %s" %(instance.name)
                instance.stop()
        else:
                print "Instance already stopped : %s \n" %(instance.id)
    except Exception as e:
        print(str(e))

def addFloatingIP(nova, instanceName, floatingIP):
    try:
        notActive = True
        while notActive:
		instance = nova.servers.find(name=instanceName)
                if instance.status == 'ACTIVE':
                        notActive = False
        print "Instance created\n"

        instance.add_floating_ip(floatingIP)
        print "Floating ip allocated : %s %s" %(instanceName, floatingIP)
    except Exception as e:
        print str(e)

