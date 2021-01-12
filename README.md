# `OpcuaExport`

OpcuaExoprt service subscribes to classified results from EIS message bus(VideoAnalytics) and starts publishing meta data to opcua clients


## `Configuration`

For more details on Etcd secrets and messagebus endpoint configuration, visit [Etcd_Secrets_Configuration.md](../Etcd_Secrets_Configuration.md) and
[MessageBus Configuration](../common/libs/ConfigMgr/README.md#interfaces) respectively.

## `Installation`

* Follow steps 1-5 of main [EIS README](../README.md) if not done already as part of EIS stack setup

* Please use below steps to generate opcua client certificates before running test client subscriber for production mode.
   1. Append following key in `certs' in [build/provision/config/x509_cert_config.json](../build/provision/config/x509_cert_config.json) file.
        ```
                {
                "opcua": {
			"client_alt_name": "",
			"output_format": "DER"
                         }
                }
        ```

    2. Re-provision EIS using below command in `[WORKDIR]/IEdgeInsights/build/provision` folder to reprovision EIS.

        ```
        $ sudo ./provision_eis.sh <path_to_eis_docker_compose_file>

        eq. $ sudo ./provision_eis.sh ../docker-compose.yml

        ```

      
    3. Update opcua client certificate access so that sample test program can access the certificates.
	
	```

        sudo chmod -R 755 ../../build/provision/Certificates/ca
        sudo chmod -R 755 ../../build/provision/Certificates/opcua
	
	 ```

    Caution: This step will make the certs insecure. Please do not do it on a production machine.
            

* To run a test subscriber follow README at [OpcuaExport/OpcuaBusAbstraction/c/test](OpcuaBusAbstraction/c/test)

