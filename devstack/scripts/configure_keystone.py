#!/usr/bin/python
# Insert SAML configuration in keystone.conf
import configparser, sys

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
