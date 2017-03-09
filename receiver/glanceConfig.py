from glanceclient import Client as glanceClient
from glanceclient.common import utils

def uploadImage(glance, imageName, path):
    try:
        print "Upload image : %s" %(imageName)
        image = glance.images.create(name=imageName)
        glance.images.update(image.id, disk_format='qcow2')
        glance.images.update(image.id, container_format='bare')
        glance.images.upload(image.id, open(path,'rb'))
    except Exception as e:
        print str(e)

def downloadImage(glance, snapshotId, imageName, path):
    try:
        print "Download snapshot of the instance %s" %(snapshotId)

        d = glance.images.data(snapshotId)
        utils.save_image(d, path + '/'+ imageName + '.raw')
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

