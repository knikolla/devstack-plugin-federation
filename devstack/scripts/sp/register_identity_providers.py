#!/usr/bin/python
# Copyright 2016 Massachusetts Open Cloud
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import os
import subprocess

from keystoneclient import session as ksc_session
from keystoneclient.auth.identity import v3
from keystoneclient.v3 import client as keystone_v3

import python_hosts

# Source environment variables from file
# http://stackoverflow.com/questions/3503719/emulating-bash-source-in-python
command = ['bash', '-c', 'source ~/admin && env']
proc = subprocess.Popen(command, stdout = subprocess.PIPE)
for line in proc.stdout:
  (key, _, value) = line.partition("=")
  os.environ[key] = value
proc.communicate()

try:
    OS_AUTH_URL = os.environ['OS_AUTH_URL'].strip('\n')
    OS_PROJECT_NAME = os.environ['OS_PROJECT_NAME'].strip('\n')
    OS_USERNAME = os.environ['OS_USERNAME'].strip('\n')
    OS_PASSWORD = os.environ['OS_PASSWORD'].strip('\n')
    OS_USER_DOMAIN_ID = os.environ['OS_USER_DOMAIN_ID'].strip('\n')
    OS_PROJECT_DOMAIN_ID = os.environ['OS_PROJECT_DOMAIN_ID'].strip('\n')
except KeyError as e:
    raise SystemExit('%s environment variable not set.' % e)

def client_for_admin_user():
    auth = v3.Password(auth_url=OS_AUTH_URL,
                       username=OS_USERNAME,
                       password=OS_PASSWORD,
                       project_name=OS_PROJECT_NAME,
                       user_domain_id=OS_USER_DOMAIN_ID,
                       project_domain_id=OS_PROJECT_DOMAIN_ID)
    session = ksc_session.Session(auth=auth)
    return keystone_v3.Client(session=session)

# Used to execute all admin actions
client = client_for_admin_user()
print "print user list to varify client authentication and authorization"
print client.users.list()

def create_domain(client, name):
    try:
         d = client.domains.create(name=name)
    except:
         d = client.domains.find(name=name)
    return d

def create_group(client, name, domain):
    try:
         g = client.groups.create(name=name, domain=domain)
    except:
         g = client.groups.find(name=name)
    return g

def create_role(client, name):
    try:
        r = client.roles.create(name=name)
    except:
        r = client.roles.find(name=name)
    return r

def create_project(client, name):
    try:
        r = client.projects.create(name=name, domain='default')
    except:
        r = client.projects.find(name=name, domain='default')
    return r

print('\nCreating domain1')
domain1 = create_domain(client, 'domain1')

print('\nCreating group1')
group1 = create_group(client, 'group1', domain1)

print('\nCreating project fed-demo')
#project1 = create_project(client, 'fed-demo')
admin_project = client.projects.find(name='admin')

print('\nCreating role Member')
role1 = create_role(client, '_member_')

print('\nGrant role Member to group1 in domain1')
client.roles.grant(role1, group=group1, domain=domain1)
#client.roles.grant(role1, group=group1, project=project1)
client.roles.grant(role1, group=group1, project=admin_project)

print('\nList group1 role assignments')
client.role_assignments.list(group=group1)

def create_mapping(client, mapping_id, rules):
    try:
        m = client.federation.mappings.create(
            mapping_id=mapping_id, rules=rules)
    except:
        m = client.federation.mappings.update(
            mapping=mapping_id, rules=rules)
    return m

print('\nCreating mapping')
rules = [
{
    "local": [
        {
            "user": {
                "name": "federated_user",
                "domain": {
                    "name": "default"
                }
            },
            "group": {
                "id": group1.id
            }
        }
    ],
    "remote": [
        {
            "type": "openstack_user",
            "any_one_of": [
                "user1",
                "admin"
            ]
        }
    ]
}
]

mapping1 = create_mapping(client, mapping_id='keystone-idp-mapping', rules=rules)

def create_idp(client, id, remote_id):
    idp_ref = {'id': id,
               'remote_ids': [remote_id],
               'enabled': True}
    try:
        i = client.federation.identity_providers.create(**idp_ref)
    except:
        i = client.federation.identity_providers.find(id=id)
    return i

def create_protocol(client, protocol_id, idp, mapping):
    try:
        p = client.federation.protocols.create(protocol_id=protocol_id,
                                               identity_provider=idp,
                                               mapping=mapping)
    except:
        p = client.federation.protocols.update(identity_provider=idp, protocol=protocol_id, mapping=mapping)
    return p


hosts = python_hosts.Hosts()
for host in hosts.entries:
    if host.names is not None and 'idp' in host.names[0]:
        idp_ip = host.address
        break

print('\nRegister keystone-idp')
idp1 = create_idp(client, id='keystone-idp',
                  remote_id='http://' + idp_ip + ':35357/v3/OS-FEDERATION/saml2/idp')

print('\nRegister protocol')
protocol1 = create_protocol(client, protocol_id='saml2', idp=idp1,
                            mapping=mapping1)
