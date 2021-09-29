**Contents**

- [OpcuaExport](#opcuaexport)
  - [Configuration](#configuration)
  - [Service bring up](#service-bring-up)
  - [Known issues](#known-issues)

# OpcuaExport

OpcuaExport service serves as as OPCUA server subscribring to classified results from EII message bus(VideoAnalytics) and starts publishing meta data to OPCUA clients

## Configuration

For more details on Etcd secrets and messagebus endpoint configuration, visit [Etcd_Secrets_Configuration.md](https://github.com/open-edge-insights/eii-core/blob/master/Etcd_Secrets_Configuration.md) and
[MessageBus Configuration](https://github.com/open-edge-insights/eii-core/blob/master/common/libs/ConfigMgr/README.md#interfaces) respectively.

## Service bring up

* Please use below steps to generate opcua client certificates before running test client subscriber for production mode.

    1. Please go through the below sections to have OpcuaExport 
       service built and launch it:
        - [../README.md#generate-deployment-and-configuration-files](https://github.com/open-edge-insights/eii-core/blob/master/README.md#generate-deployment-and-configuration-files)
        - [../README.md#provision](https://github.com/open-edge-insights/eii-core/blob/master/README.md#provision)
        - [../README.md#build-and-run-eii-videotimeseries-use-cases](https://github.com/open-edge-insights/eii-core/blob/master/README.md#build-and-run-eii-videotimeseries-use-cases)

    2. Update opcua client certificate access so that sample test program 
       can access the certificates.

        ```sh
            sudo chmod -R 755 ../../build/provision/Certificates
        ```

        > **Caution**: This step will make the certs insecure. Please do not do it on a production machine.

* To run a test subscriber follow README at [OpcuaExport/OpcuaBusAbstraction/c/test](OpcuaBusAbstraction/c/test)

## OPCUA client apps

* OpcuaExport service has been validated with below 3rd party OPCUA client apps:
  * OPCUA CTT tool (https://opcfoundation.org/developer-tools/certification-test-tools/opc-ua-compliance-test-tool-uactt/)
  * UaExpert (https://www.unified-automation.com/downloads/opc-ua-clients.html)
  * Integrated Objects (https://integrationobjects.com/sioth-opc/sioth-opc-unified-architecture/opc-ua-client/)
  * Prosys OPCUA client app(https://www.prosysopc.com/products/opc-ua-browser/)

### Note:
* To connect with OPCUA client apps, User needs to take backup [opcua_client_certificate.der](../build/provision/Certificates/opcua/opcua_client_certificate.der) and copy OPCUA client apps certificate to it.
```sh
    sudo chmod -R 755 ../../build/provision/Certificates
    cp <OPCUA client apps certificate> ../build/provision/Certificates/opcua/opcua_client_certificate.der
```
Make sure to down all the eii services and up to reflect the changes.

* Running in Kubernetes Environment
To connect with OPCUA client apps, User needs to copy OPCUA client apps certificate to [opcua_client_certificate.der](../build/helm-eii/eii-provision/Certificates/opcua/opcua_client_certificate.der).

Install provision and deploy helm chart
```sh
     $ cd ../build/helm-eii/
     $ helm install eii-provision eii-provision/
     $ helm install eii-deploy eii-deploy/
```
Access Opcua server using "opc.tcp://<Host IP>:32003" endpoint.
