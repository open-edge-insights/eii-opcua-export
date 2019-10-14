# `OpcuaExport`

OpcuaExoprt service subscribes to classified results from EIS message bus(VideoAnalytics) and starts publishing meta data to opcua clients


## `Configuration`

For more details on Etcd and MessageBus endpoint configuration, visit [Etcd_and_MsgBus_Endpoint_Configuration](../Etcd_and_MsgBus_Endpoint_Configuration.md).

## `Installation`

* Follow [provision/README.md](../README#provision-eis.md) for EIS provisioning
  if not done already as part of EIS stack setup

* Run OpcuaExport

	1. Build and Run OpcuaExport as container
        ```
        $ cd [repo]/docker_setup
        $ docker-compose up --build ia_opcua_export
       ```

* To Run test opcua client subscrier

        1. Make sure data is getting published from OpcuaExport

        To run a test subscriber follow below steps
        ```
        Follow README [repo]/libs/OpcuaBusAbstraction/c/test
	```
