/*
Copyright (c) 2019 Intel Corporation.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

package main

import (
	eismsgbus "EISMessageBus/eismsgbus"
	configmgr "IEdgeInsights/common/libs/ConfigManager"
	databus "IEdgeInsights/OpcuaExport/OpcuaBusAbstraction/go"
	util "IEdgeInsights/common/util"
	msgbusutil "IEdgeInsights/common/util/msgbusutil"
	"flag"
	"fmt"
	"io/ioutil"
	"os"
	"strconv"
	"strings"

	"github.com/golang/glog"
)

// OpcuaExportApp interface
type OpcuaExportApp interface {
	Subscribe()
	Publish(data interface{})
}

// struct for opcuaBus related configurations
type opcuaBus struct {
	opcuaDatab databus.DataBus
	pubTopics  []string
}

// struct for messageBus related configurations
type messageBus struct {
	subTopics []string
}

// OpcuaExport struct with both opcuaBus and messageBus configurations
type OpcuaExport struct {
	opcuaBus     opcuaBus
	msgBus       messageBus
	devMode      bool
	cfgMgrConfig map[string]string
}

//NewOpcuaExport function to create OpcuaExport instance
func NewOpcuaExport() (opcuaExport *OpcuaExport, err error) {
	var opcuaContext map[string]string
	opcuaExport = &OpcuaExport{}
	devMode, err := strconv.ParseBool(os.Getenv("DEV_MODE"))
	if err != nil {
		glog.Errorf("string to bool conversion error")
		os.Exit(1)
	}
	opcuaExport.devMode = devMode
	opcuaExport.opcuaBus.pubTopics = msgbusutil.GetTopics("PUB")
	opcuaExport.msgBus.subTopics = msgbusutil.GetTopics("SUB")
	pubConfigList := strings.Split(os.Getenv("OpcuaExportCfg"), ",")
	endpoint := pubConfigList[0] + "://" + pubConfigList[1]

	// TODO: add support for both prod and dev mode
	appName := os.Getenv("AppName")
	opcuaExport.cfgMgrConfig = util.GetCryptoMap(appName)

	opcuaContext = map[string]string{
		"direction": "PUB",
		"endpoint":  endpoint,
	}
	opcuaContext["certFile"] = ""
	opcuaContext["privateFile"] = ""
	opcuaContext["trustFile"] = ""

	opcuaCerts := []string{"/tmp/opcua_server_cert.der", "/tmp/opcua_server_key.der", "/tmp/ca_cert.der"}
	opcuaExportKeys := []string{"/OpcuaExport/server_cert", "/OpcuaExport/server_key", "/OpcuaExport/ca_cert"}

	if !opcuaExport.devMode {

		cfgMgr := configmgr.Init("etcd", opcuaExport.cfgMgrConfig)
		i := 0
		for _, opcuaExportKey := range opcuaExportKeys {
			opcuaCertFile, err := cfgMgr.GetConfig(opcuaExportKey)
			if err != nil {
				glog.Fatal(err)
			}
			certFile := []byte(opcuaCertFile)
			err = ioutil.WriteFile(opcuaCerts[i], certFile, 0644)
			i++
		}
		opcuaContext["certFile"] = opcuaCerts[0]
		opcuaContext["privateFile"] = opcuaCerts[1]
		opcuaContext["trustFile"] = opcuaCerts[2]
	}

	opcuaExport.opcuaBus.opcuaDatab, err = databus.NewDataBus()
	if err != nil {
		glog.Errorf("New DataBus Instance creation Error: %v", err)
		return opcuaExport, err
	}

	err = opcuaExport.opcuaBus.opcuaDatab.ContextCreate(opcuaContext)
	if err != nil {
		glog.Errorf("DataBus-OPCUA context creation Error: %v", err)
		return opcuaExport, err
	}

	for _, opcuaCert := range opcuaCerts {
		_, statErr := os.Stat(opcuaCert)
		if statErr == nil {
			glog.V(1).Infof("Removing %v", opcuaCert)
			err = os.Remove(opcuaCert)
			if err != nil {
				glog.Errorf("Error while removing opcua cert file %v", err)
			}
		}
	}
	return opcuaExport, err
}

// Subscribe function spawns worker thread to subscribe to EIS message bus and starts publishing data to opcua
func (opcuaExport *OpcuaExport) Subscribe() {
	glog.Infof("-- Initializing message bus context")

	for _, subTopicCfg := range opcuaExport.msgBus.subTopics {
		msgBusConfig := msgbusutil.GetMessageBusConfig(subTopicCfg, "SUB", opcuaExport.devMode,
			opcuaExport.cfgMgrConfig)
		subTopicCfg := strings.Split(subTopicCfg, "/")
		go worker(opcuaExport, msgBusConfig, subTopicCfg[1])
	}
}

func worker(opcuaExport *OpcuaExport, config map[string]interface{}, topic string) {
	defer opcuaExport.opcuaBus.opcuaDatab.ContextDestroy()

	client, err := eismsgbus.NewMsgbusClient(config)
	if err != nil {
		glog.Errorf("-- Error initializing message bus context: %v\n", err)
		return
	}
	defer client.Close()
	subscriber, err := client.NewSubscriber(topic)
	if err != nil {
		glog.Errorf("-- Error subscribing to topic: %v\n", err)
		return
	}
	defer subscriber.Close()

	for {
		select {
		case msg := <-subscriber.MessageChannel:
			glog.V(1).Infof("-- Received Message: %v\n", msg.Data)
			opcuaExport.Publish(msg.Data)
		case err := <-subscriber.ErrorChannel:
			glog.Errorf("-- Error receiving message: %v\n", err)
		}
	}
}

// Publish function publishes data to opcua clients
func (opcuaExport *OpcuaExport) Publish(data interface{}) {
	pubTopics := opcuaExport.opcuaBus.pubTopics
	topicConfigs := make([]map[string]string, len(pubTopics))
	for i, pubTopic := range pubTopics {
		topicConfigs[i] = map[string]string{"ns": "StreamManager", "name": pubTopic, "dType": "string"}
	}
	for _, topicConfig := range topicConfigs {
		opcuaData := fmt.Sprintf("%s %v", topicConfig["name"], data)
		opcuaExport.opcuaBus.opcuaDatab.Publish(topicConfig, opcuaData)
		glog.Infof("Published data: %v on topic: %s\n", opcuaData, topicConfig)
	}
}

func main() {
	flag.Parse()
	flag.Set("logtostderr", "true")
	opcuaExport, err := NewOpcuaExport()
	if err != nil {
		glog.Errorf("Opcua-Export instance creation Error: %v", err)
		os.Exit(1)
	}
	opcuaExport.Subscribe()
	select {}
}
