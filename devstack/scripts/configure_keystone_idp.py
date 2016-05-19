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

import configparser
import sys

idp_ip = sys.argv[1]

config = configparser.ConfigParser()
config.read('/etc/keystone/keystone.conf')

config['saml']['certfile'] = '/etc/keystone/ssl/certs/ca.pem'
config['saml']['keyfile'] = '/etc/keystone/ssl/private/cakey.pem'
config['saml']['idp_entity_id'] = 'http://' + idp_ip + ':5000/v3/OS-FEDERATION/saml2/idp'
config['saml']['idp_sso_endpoint'] = 'http://' + idp_ip + ':5000/v3/OS-FEDERATION/saml2/sso'
config['saml']['idp_metadata_path'] = '/etc/keystone/keystone_idp_metadata.xml'

with open('/etc/keystone/keystone.conf', 'w') as configfile:
    config.write(configfile)
