#!/usr/bin/env bash
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

KEYSTONE_SCRIPTS=$DEST/k2k-idp/devstack/scripts/

function install_idp(){
    if is_ubuntu; then
        install_package xmlsec1
        install_package python-pip
    fi
    sudo pip install pysaml2 configparser
}

function configure_idp(){
    if $IS_K2K_IDP; then
        iniset $KEYSTONE_CONF saml certfile "/etc/keystone/ssl/certs/ca.pem"
        iniset $KEYSTONE_CONF saml keyfile "/etc/keystone/ssl/private/cakey.pem"
        iniset $KEYSTONE_CONF saml idp_entity_id "http://$HOST_IP:5000/v3/OS-FEDERATION/saml2/idp"
        iniset $KEYSTONE_CONF saml idp_sso_endpoint "http://$HOST_IP:5000/v3/OS-FEDERATION/saml2/sso"
        iniset $KEYSTONE_CONF saml idp_metadata_path "/etc/keystone/keystone_idp_metadata.xml"

        keystone-manage pki_setup
        keystone-manage saml_idp_metadata > /etc/keystone/keystone_idp_metadata.xml

        # Restart Apache2/httpd
        if is_ubuntu; then
            restart_service apache2
        else
            restart_service httpd
        fi

        openstack --os-identity-api-version 3 service provider create \
            --auth-url $SP_AUTH_URL --service-provider-url $SP_URL sp
    fi
}

function install_sp() {
    if is_ubuntu; then
        install_package libxml2-dev
        install_package libxslt-dev
        install_package python-dev
        install_package xmlsec1
        install_package libapache2-mod-shib2
    else
        install_package xmlsec1
        install_package xmlsec1-openssl
        install_package libxml2-devel
        install_package libxslt-devel
        install_package python-devel
        install_package mod_ssl
    fi

    # Note(knikolla): Need to automate installation of shibboleth in CentOS

    sudo pip install pysaml2 lxml
}

function configure_sp() {
    if is_ubuntu; then
        sudo shib-keygen -f
    else
        ./etc/shibboleth/keygen.sh -f
    fi

    sudo python $KEYSTONE_SCRIPTS/sp/configure_apache.py
    sudo python $KEYSTONE_SCRIPTS/sp/configure_shibboleth.py

    iniset $KEYSTONE_CONF auth methods "external,password,token,oauth1,saml2"
    iniset $KEYSTONE_CONF auth saml2 "keystone.auth.plugins.mapped.Mapped"

    sudo a2enmod shib2

    # Restart Apache2/httpd
    if is_ubuntu; then
        restart_service apache2
    else
        restart_service httpd
    fi

    python $KEYSTONE_SCRIPTS/sp/register_identity_providers.py
}

if [[ "$1" == "stack" && "$2" == "install" ]]; then
    if $IS_K2K_IDP; then
        install_idp
    fi

    if $IS_K2K_SP; then
        install_sp
    fi

elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
    if $IS_K2K_IDP; then
        configure_idp
    fi

    if $IS_K2K_SP; then
        configure_sp
    fi

elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
    # Initialize and start the template service
    :
fi

if [[ "$1" == "unstack" ]]; then
    # Shut down template services
    # no-op
    :
fi

if [[ "$1" == "clean" ]]; then
    # Remove state and transient data
    # Remember clean.sh first calls unstack.sh
    # no-op
    :
fi