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
* Run publisher

	1. Make sure data is getting published over EIS Message Bus

		To run a test publiser follow below steps
	```
	$cd [repo]/OpcuaExport/test/
	$go run publisher.go -devmode true/false
	```

* To Run test opcua client subscrier

        1. Make sure data is getting published from OpcuaExport

        To run a test subscriber follow below steps
        ```
        $cd [repo]/libs/OpcuaBusAbstraction/c/test

        Follow README, mainly follow Pre-requisites section and run below command as currently OpcuaExport is not enbaled with opcua security

	$make sub_insecure

	```
