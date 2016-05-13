#!/usr/bin/python
# Registers the service providers present in /etc/hosts
# Authors: Minying Lu, Kyle Liberti, Kristi Nikolla
# Boston Universtiy - Massachusetts Open Cloud
import os, subprocess

import python_hosts

from keystoneclient import session as ksc_session
from keystoneclient.auth.identity import v3
from keystoneclient.v3 import client as keystone_v3

import keystoneauth1.exceptions.http

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
    OS_PROJECT_ID = os.environ['OS_PROJECT_ID'].strip('\n')
    OS_USER_ID = os.environ['OS_USER_ID'].strip('\n')
    OS_PASSWORD = os.environ['OS_PASSWORD'].strip('\n')
except KeyError as e:
    raise SystemExit('%s environment variable not set.' % e)


def client_for_admin_user():
    auth = v3.Password(auth_url=OS_AUTH_URL,
                       user_id=OS_USER_ID,
                       password=OS_PASSWORD,
                       project_id=OS_PROJECT_ID)
    session = ksc_session.Session(auth=auth)
    return keystone_v3.Client(session=session)


def create_sp(client, sp_id, sp_url, auth_url):
        sp_ref = {'id': sp_id,
                  'sp_url': sp_url,
                  'auth_url': auth_url,
                  'enabled': True}
        return client.federation.service_providers.create(**sp_ref)

# Used to execute all admin actions
client = client_for_admin_user()
print "print user list to verify client object"
print client.users.list()

# Extract hosts information
hosts = python_hosts.Hosts()

service_providers = []
for host in hosts.entries:
    if host.names is not None and 'sp' in host.names[0]:
        service_providers.append({'id': host.names[0], 'address': host.address})

for sp in service_providers:
    try:
        client.federation.service_providers.get(sp['id'])
        #Note(knikolla): SP is already registered, skip.
    except keystoneauth1.exceptions.http.NotFound:
        #Note(knikolla): SP is not already registered.
        SP_url="http://" + sp['address'] + ":5000/Shibboleth.sso/SAML2/ECP"
        AUTH_url="http://" + sp['address'] + ":35357/v3/OS-FEDERATION/identity_providers/keystone-idp/protocols/saml2/auth"

        print('\nCreate SP')

        create_sp(client, sp['id'], SP_url, AUTH_url)