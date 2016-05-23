# devstack-plugin-federation

# Setup
```bash
# local.conf
# Enable the plugin by adding the following line to local.conf
enable_plugin federation https://github.com/knikolla/devstack-plugin-federation.git
```

## K2K Identity Provider
```bash
# local.conf
# Enable the K2K Identity Provider service
enable_service k2k-idp
```

After the setup is done, register the federated Keystone service providers with:
```bash
export SP_IP=10.1.2.3
export SP_ID=service_provider
export SP_URL="http://$SP_IP:5000/Shibboleth.sso/SAML2/ECP"
export SP_AUTH_url="http://$SP_IP:35357/v3/OS-FEDERATION/identity_providers/keystone-idp/protocols/saml2/auth"
openstack --os-identity-api-version 3 service provider create \
    --auth-url $SP_AUTH_URL --service-provider-url $SP_URL $SP_ID
```

## Federation Service Provider
(Temporarily K2K Specific)
```bash
# local.conf
# Enable the Federation Service Provider (temporarily k2k specific instructions)
enable_service federation-sp
IDP_REMOTE_ID=http://XXX.YYY.ZZZ:35357/v3/OS-FEDERATION/saml2/idp
IDP_METADATA=http://XXX.YYY.ZZZ:5000/v3/OS-FEDERATION/saml2/metadata
IDP_ID=idp
FEDERATION_PROTOCOL=saml2
```