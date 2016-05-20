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
import sys, fileinput, re, platform

distro = platform.linux_distribution()[0].lower()
if 'ubuntu' in distro or 'debian' in distro:
    keystone_conf_path = '/etc/apache2/sites-available/keystone.conf'
elif 'centos' in distro or 'red hat' in distro:
    keystone_conf_path = '/etc/httpd/conf.d/keystone.conf'

print('Modifying %s', keystone_conf_path)

def modify_apache2_keyconf():
    fh=fileinput.input(keystone_conf_path, inplace=True)
    for line in fh:
        repl=line + '    WSGIScriptAliasMatch ^(/v3/OS-FEDERATION/identity_providers/.*?/protocols/.*?/auth)$ /var/www/keystone/main/$1'
        line=re.sub('\<VirtualHost \*\:5000\>', repl, line)
        sys.stdout.write(line)
    fh.close()

    text = '<Location /Shibboleth.sso>\n' + '    SetHandler shib\n' + '</Location>\n\n' + '<LocationMatch /v3/OS-FEDERATION/identity_providers/.*?/protocols/saml2/auth>\n' + '    ShibRequestSetting requireSession 1\n' + '    AuthType shibboleth\n' + '    ShibExportAssertion Off\n' + '    Require valid-user\n' + '</LocationMatch>'
    with open(keystone_conf_path, 'a') as file:
        file.write(text)

modify_apache2_keyconf()

