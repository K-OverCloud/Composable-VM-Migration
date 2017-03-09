from keystoneauth1.identity import v3
from keystoneauth1 import session
from novaclient import client as novClient
from neutronclient.v2_0 import client as neutClient
from glanceclient import Client as glanceClient
from glanceclient.common import utils

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


def getGlanceClient(controllerIP, username, password, project_name, user_domain_name, project_domain_name):
    auth = v3.Password(auth_url= 'http://'+controllerIP+':35357/v3',
                           username = username,
                           password= password,
                           project_name = project_name,
                           user_domain_name = user_domain_name,
                           project_domain_name = project_domain_name)
    sess = session.Session(auth=auth)
    glance = glanceClient("2", session=sess)

    return glance
