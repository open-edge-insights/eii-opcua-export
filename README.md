# `OpcuaExport`

OpcuaExoprt service subscribes to classified results from EIS message bus(VideoAnalytics) and starts publishing meta data to opcua clients


## `Configuration`

OpcuaExport configurations 
OpcuaExport related configurations are added in the docker-compose.yaml as environment variables under ia_opcua_export service. 

Below are the necessary configurations to be added,

```
SubTopics: <List of topics OpcuaExport will subscribe to> 
Subtopicname_cfg: <zmq_tcp/zmq_ipc, ipaddress:port>
PubTopics: <List of topics OpcuaExport will publish>
OpcuaExportCfg: "opcua,<host>:<port>"
```
Example is as shown below:

```
SubTopics: "camera1_stream_results"
camera1_stream_results_cfg: "zmq_tcp,127.0.0.1:65013"
PubTopics: "cam_serial1_results,cam_serial2_results"
OpcuaExportCfg: "opcua,localhost:65003"
```

## `Installation`

* Run OpcuaExport

	1. Build and Run OpcuaExport as container
        ```
        $ cd [repo]/docker_setup
        $ ln -sf OpcuaExport/.dockerignore ../.dockerignore
        $ docker-compose up --build OpcuaExport        
       ```
* Run publisher

	1. Make sure data is getting published over EIS Message Bus

		To run a test publiser follow below steps
	```
	$cd [repo]/OpcuaExport/test/
    	$go run publisher.go -port <port, data to be published to> -topic <topic name>
   	Ex: $go run publisher.go -port 65013 -topic camera1_stream_results
