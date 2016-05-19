#!/usr/bin/env bash

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
        sudo python $KEYSTONE_SCRIPTS/k2k-idp/configure_keystone.py $IDP_IP

        keystone-manage pki_setup
        keystone-manage saml_idp_metadata > /etc/keystone/keystone_idp_metadata.xml

        # Restart Apache2/httpd
        if is_ubuntu; then
            restart_service apache2
        else
            restart_service httpd
        fi

        # python $KEYSTONE_SCRIPTS/k2k-idp/register_service_providers.py
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

    sudo pip install pysaml2 lxml
    sudo pip install configparser python-hosts
}

function configure_sp() {
    if is_ubuntu; then
        sudo shib-keygen -f
    else
        ./etc/shibboleth/keygen.sh -f
    fi

    sudo python $KEYSTONE_SCRIPTS/k2k-sp/configure_apache.py
    sudo python $KEYSTONE_SCRIPTS/k2k-sp/configure_shibboleth.py
    sudo python $KEYSTONE_SCRIPTS/k2k-sp/configure_keystone.py

    sudo a2enmod shib2

    # Restart Apache2/httpd
    if is_ubuntu; then
        restart_service apache2
    else
        restart_service httpd
    fi

    python $KEYSTONE_SCRIPTS/k2k-sp/register_identity_providers.py
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