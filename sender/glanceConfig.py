from keystoneauth1.identity import v3
from keystoneauth1 import session
from novaclient import client as novClient
from neutronclient.v2_0 import client as neutClient
from glanceclient import Client as glanceClient
from glanceclient.common import utils as utilsGlance



def uploadImage(glance, imageName, path):
    try:
        print "Upload image : %s" %(imageName)
        image = glance.images.create(name=imageName)
        glance.images.update(image.id, disk_format='qcow2')
        glance.images.update(image.id, container_format='bare')
        glance.images.upload(image.id, open(path,'rb'))
        print "Image uploaded\n"
    except Exception as e:
        print str(e)

def downloadImage(glance, snapshotId, imageName, path):
    try:
        notActive = True
	while notActive:
		image = glance.images.get(snapshotId)
		if image.status == 'active':
			notActive = False
	print "Snapshot created\n"

	print "Download snapshot of the instance %s" %(snapshotId)
        d = glance.images.data(snapshotId) 
        utilsGlance.save_image(d, path+imageName+'.raw' )
        print "Completed to download image\n"
    except Exception as e:
        #print(str(e))
        print "Completed to download image\n"

def deleteImage(glance, snapshotId):
    try:
        print "Delete image : %s" %(snapshotId)
        glance.images.delete(snapshotId)
        print "Image Deleted\n"
    except Exception as e:
        print str(e)


