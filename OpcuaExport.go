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
	databus "IEdgeInsights/libs/DataBusAbstraction/go"
	util "IEdgeInsights/libs/common/go"
	"fmt"
	"os"
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
	opcuaBus opcuaBus
	msgBus   messageBus
}

//NewOpcuaExport function to create OpcuaExport instance
func NewOpcuaExport() (opcuaExport *OpcuaExport, err error) {
	opcuaExport = &OpcuaExport{}
	opcuaExport.opcuaBus.pubTopics = util.GetTopics("PUB")
	opcuaExport.msgBus.subTopics = util.GetTopics("SUB")
	pubConfigList := strings.Split(os.Getenv("OpcuaExportCfg"), ",")
	endpoint := pubConfigList[0] + "://" + pubConfigList[1]

	// TODO: add support for both prod and dev mode
	opcuaContext := map[string]string{
		"direction":   "PUB",
		"endpoint":    endpoint,
		"certFile":    "",
		"privateFile": "",
		"trustFile":   "",
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
	return opcuaExport, err
}

// Subscribe function spawns worker thread to subscribe to EIS message bus and starts publishing data to opcua
func (opcuaExport *OpcuaExport) Subscribe() {
	glog.Infof("-- Initializing message bus context")

	for _, topic := range opcuaExport.msgBus.subTopics {
		config := util.GetTopicConfig(topic, "SUB")
		go worker(opcuaExport, config, topic)
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
	opcuaExport, err := NewOpcuaExport()
	if err != nil {
		glog.Errorf("Opcua-Export instance creation Error: %v", err)
		os.Exit(1)
	}
	opcuaExport.Subscribe()
	select {}
}
