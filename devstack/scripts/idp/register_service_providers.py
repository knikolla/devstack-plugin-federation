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
import sys

from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client

sp_ip = sys.argv[1]


def get_env_variables():
    c = dict()
    try:
        c['auth_url'] = os.environ['OS_AUTH_URL'].strip('\n')
        c['project_name'] = os.environ['OS_PROJECT_NAME'].strip('\n')
        c['username'] = os.environ['OS_USERNAME'].strip('\n')
        c['password'] = os.environ['OS_PASSWORD'].strip('\n')
        c['user_domain_id'] = os.environ['OS_USER_DOMAIN_ID'].strip('\n')
        c['project_domain_id'] = os.environ['OS_PROJECT_DOMAIN_ID'].strip('\n')
        return c
    except KeyError as e:
        raise SystemExit('%s environment variable not set.' % e)


def create_client(credentials):
    auth = v3.Password(**credentials)
    sess = session.Session(auth=auth)
    return client.Client(session=sess)


def register_sp(client, sp_id, sp_ip):
    sp_url = "http://" + sp_ip + ":5000/Shibboleth.sso/SAML2/ECP"
    auth_url = "http://" + sp_ip + ":35357/v3/OS-FEDERATION/identity_providers/keystone-idp/protocols/saml2/auth"

    return client.federation.service_providers.create(id=sp_id,
                                                      sp_url=sp_url,
                                                      auth_url=auth_url,
                                                      enabled=True)

if __name__ == '__main__':
    credentials = get_env_variables()
    ksclient = create_client(credentials)
    register_sp(client=ksclient,
                sp_id='sp',
                sp_ip=sp_ip)