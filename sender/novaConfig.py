def createInstance(novaClient, name, network):
   image = novaClient.images.find(name=name)
   flavor = novaClient.flavors.find(name="m1.small")
   net = novaClient.networks.find(label=network)
   nics = [{'net-id': net.id}]
   instance = novaClient.servers.create(name=name, image=image, flavor=flavor, nics=nics)
    
   return instance

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

def deleteInstance(nova, instanceName):
    try:
	instance = nova.servers.find(name=instanceName)
	instance.delete()
	print "Instance deleted : %s\n" %(instanceName)
    except Exception as e:
	print str(e)

def addFloatingIP(instance, floatingIP):
    instance.add_floating_ip(floatingIP)


