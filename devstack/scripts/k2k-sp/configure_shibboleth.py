#!/usr/bin/python
'''#########################################################
 File: configure_shibboleth.py
 Author: Kyle Liberti <kliberti@bu.edu>
         Kristi Nikolla <knikolla@bu.edu>
 Desc: Parses shibboleth xml files and adds in proper
       XML tags to enable shibboleth authentication for
       keystone to keystone.

 Target Versions: Python2, shibboleth 2.5.2
 lxml lib: http://lxml.de/index.html

 Dependencies
 -----------------
 RHEL based:
 yum install libxml2-devel libxslt-devel python-devel

 Debian based:
 sudo apt-get install libxml2-dev libxslt-dev python-dev

 Both:
 sudo pip install lxml
######################################################## '''
from lxml import etree as ET

import python_hosts
hosts = python_hosts.Hosts()
for host in hosts.entries:
    if host.names is not None and 'idp' in host.names[0]:
        IDP_IP = host.address
        break

SHIBBOLETH_VERSION = "2.5.2" #For debugging purposes

#/etc/shibboleth/attribute-map.xml and /etc/shibboleth/shibboleth2.xml
#Files to be altered
INPUT_ATTRIBUTE_MAP_FILE = "/etc/shibboleth/attribute-map.xml"
INPUT_SHIBBOLETH2_FILE = "/etc/shibboleth/shibboleth2.xml"

OUTPUT_ATTRIBUTE_MAP_FILE = "/etc/shibboleth/attribute-map.xml"
OUTPUT_SHIBBOLETH2_FILE = "/etc/shibboleth/shibboleth2.xml"

# Tags to be added into shibboleth-map.xml
OPENSTACK_TAG = "{urn:mace:shibboleth:2.0:attribute-map}Attribute"
OPENSTACK_ATTRIB = [{'name': 'openstack_user', 'id': 'openstack_user'},
{'name': 'openstack_roles', 'id': 'openstack_roles'},
{'name': 'openstack_project', 'id': 'openstack_project'}  ]

# Tags to be added into shibboleth2.xml
SSO_NAME = "{urn:mace:shibboleth:2.0:native:sp:config}SSO"
SSO_ATTRIB_KEY = "entityID"
SSO_ATTRIB_VALUE = "http://" + IDP_IP + ":5000/v3/OS-FEDERATION/saml2/idp"
SSO_ATTRIBS = {SSO_ATTRIB_KEY: SSO_ATTRIB_VALUE}
METADATA_NAME = "{urn:mace:shibboleth:2.0:native:sp:config}MetadataProvider"
METADATA_URI= "http://" + IDP_IP + ":5000/v3/OS-FEDERATION/saml2/metadata"
METADATA_ATTRIB = {'type':'XML', 'uri': METADATA_URI}

parser = ET.XMLParser(remove_blank_text=False)
# Parse XML into ElementTree
tree_attribute_map = ET.parse(INPUT_ATTRIBUTE_MAP_FILE, parser)
tree_shibboleth2 = ET.parse(INPUT_SHIBBOLETH2_FILE, parser)

# Convert ElementTree into Python dictionary
root_attribute_map = tree_attribute_map.getroot()
root_shibboleth2 = tree_shibboleth2.getroot()

#For debugging purposes
def printTags(root):
   for tag in root.iter():
      print(tag.tag, tag.attrib)

# insert openstack tags in /etc/shibboleth/attribute-map.xml
def insertOpenstackTagsToAttributeMap():
    # Check for openstack tags in /etc/shibboleth/attribute-map.xml
    attribute_map_tags = [(i.tag, i.attrib )for i in root_attribute_map]
    for attrib in OPENSTACK_ATTRIB:
        if ((OPENSTACK_TAG, attrib) not in attribute_map_tags):
           root_attribute_map.insert(1, ET.Element(OPENSTACK_TAG, attrib))


#Insert SSO tags into /etc/shibboleth/shibboleth2.xml
def insertSSOTags():
  try:
     #editing existing SSO tag
     sso_attrib_dict = [tag.attrib for tag in root_shibboleth2.iter() if tag.tag == SSO_NAME][0]
     [sso_attrib_dict.pop(attrib) for attrib in sso_attrib_dict.keys() if attrib != SSO_ATTRIB_KEY]
     sso_attrib_dict[SSO_ATTRIB_KEY] = SSO_ATTRIB_VALUE

  except: #No SSO tags in file
     print "There is no SSO tags in", INPUT_SHIBBOLETH2_FILE
     try:
        print "Adding necessary tags"
        children = root_shibboleth2[3][1]
        children.insert(1, ET.Element(SSO_NAME, SSO_ATTRIBS))
        print "SSO Tags added"
     except:
        print "ERROR: Can't insert SSO tags to", INPUT_SHIBBOLETH2_FILE
        print "Make sure you are using targeted Shibboleth version", SHIBBOLETH_VERSION
        pass
     pass

#Insert Metadata tags into /etc/shibboleth/shibboleth2.xml
def insertMetadataTag():
 # Check for metadata tags shibboleth tags in /etc/shibboleth/shibboleth2.xml
 shibboleth2_tags = [(i.tag, i.attrib )for i in root_shibboleth2.iter()]
 shibboleth2_names = [ i.tag for i in root_shibboleth2.iter()]

 if(METADATA_NAME in shibboleth2_names):
   if((METADATA_NAME, METADATA_ATTRIB) not in shibboleth2_tags):
      metadata_attrib_dict = [tag.attrib for tag in root_shibboleth2.iter() if tag.tag == METADATA_NAME][0]
      [metadata_attrib_dict.pop(attrib) for attrib in metadata_attrib_dict.keys() if attrib != "type" and attrib != "uri" ]
      metadata_attrib_dict["type"] = "XML"
      metadata_attrib_dict["uri"] = METADATA_URI
      #tree_shibboleth2.write(OUTPUT_SHIBBOLETH2_FILE)
 else:
     try:
        children = root_shibboleth2[3]
        children.insert(6, ET.Element(METADATA_NAME, METADATA_ATTRIB))
     except:
        print "ERROR: Can't insert Metadata tags to", INPUT_SHIBBOLETH2_FILE
        print "Make sure you are using targeted Shibboleth version", SHIBBOLETH_VERSION
        pass

def insertOpenstackTags():
   insertOpenstackTagsToAttributeMap()
   insertSSOTags()
   insertMetadataTag()
   tree_shibboleth2.write(OUTPUT_SHIBBOLETH2_FILE)
   tree_attribute_map.write(OUTPUT_ATTRIBUTE_MAP_FILE)


insertOpenstackTags()
