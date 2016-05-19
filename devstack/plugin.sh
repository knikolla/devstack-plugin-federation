#!/usr/bin/env bash

K2K_SCRIPTS=$DEST/k2k-idp/devstack/scripts/

function install_idp(){
    if $IS_K2K_IDP; then
        if is_ubuntu; then
            install_package xmlsec1
            install_package python-pip
        fi
    fi
    sudo pip install pysaml2 configparser python-hosts
}

function configure_idp(){
    if $IS_K2K_IDP; then
        sudo python $K2K_IDP_SCRIPTS/configure_keystone_idp.py $IDP_IP

        keystone-manage pki_setup
        keystone-manage saml_idp_metadata > /etc/keystone/keystone_idp_metadata.xml

        # Restart Apache2/httpd
        if is_ubuntu; then
            restart_service apache2
        else
            restart_service httpd
        fi

        python $K2K_IDP_SCRIPTS/register_service_providers.py
    fi
}


if [[ "$1" == "stack" && "$2" == "pre-install" ]]; then
    # Set up system services
    echo_summary "Installing packages"


elif [[ "$1" == "stack" && "$2" == "install" ]]; then
    # Perform installation of service source
    echo_summary "Installing Template"
    install_idp

elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
    # Configure after the other layer 1 and 2 services have been configured
    echo_summary "Configuring Template"
    configure_idp

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