#!/usr/bin/python
# Insert auth_uri in [cinder] in nova.conf
import configparser

config = configparser.ConfigParser()
config.read('/etc/keystone/keystone.conf')

config['auth']['methods'] = 'external,password,token,oauth1,saml2'
config['auth']['saml2'] = 'keystone.auth.plugins.mapped.Mapped'

with open('/etc/keystone/keystone.conf', 'w') as configfile:
    config.write(configfile)
