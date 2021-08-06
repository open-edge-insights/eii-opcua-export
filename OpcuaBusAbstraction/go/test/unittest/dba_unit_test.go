/*
Copyright (c) 2021 Intel Corporation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

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
	databus "IEdgeInsights/OpcuaBusAbstraction/go"
	"fmt"
	"os"
	"reflect"
	"strconv"
	"testing"
	"time"

	"github.com/golang/glog"
)

func errHandler() {
	if r := recover(); r != nil {
		glog.Errorln(r)
		glog.Errorln("Exting Test program with ERROR!!!")
		os.Exit(1)
	}
}

var subResults = map[string]string{}
var pubStop = true
var count = -1

var contextConfig = map[string]string{
	"endpoint":    "opcua://localhost:65003",
	"direction":   "PUB",
	"certFile":    "/etc/ssl/opcua/opcua_server_certificate.der",
	"privateFile": "/etc/ssl/opcua/opcua_server_key.der",
	"trustFile":   "/etc/ssl/ca/ca_certificate.der",
}

var topicConfig = map[string]string{
	"ns":    "StreamManager",
	"name":  "classifier_results",
	"dType": "string",
}

func cbFunc(topic string, msg interface{}) {
	if count > -1 {
		subResults[strconv.Itoa(count)] = msg.(string)
	}
	fmt.Println("Received msg: " + msg.(string) + " on topic: " + topic)
	count = count + 1
}

func sub() {
	eiiDatabsub, err := databus.NewDataBus()

	if err != nil {
		panic(err)
	}
	contextConfigsub := map[string]string{
		"endpoint":    "opcua://localhost:65003",
		"direction":   "SUB",
		"name":        "StreamManager",
		"certFile":    "/etc/ssl/opcua/opcua_client_certificate.der",
		"privateFile": "/etc/ssl/opcua/opcua_client_key.der",
		"trustFile":   "/etc/ssl/ca/ca_certificate.der",
		"topic":       "classifier_results",
	}

	err = eiiDatabsub.ContextCreate(contextConfigsub)
	if err != nil {
		panic(err)
	}

	topicConfigArray := []map[string]string{topicConfig}
	err = eiiDatabsub.Subscribe(topicConfigArray, 1, "START", cbFunc)
	if err != nil {
		panic(err)
	}

	for pubStop {
		time.Sleep(10 * time.Second)
	}

}

// TODO:This test case is crashing and need fix
// Negative test case for subscription.
// Without publishing or without starting a server, subscriber or client should not start.
// Expected Result: Error on Subscribing for a topic.
func TestNegativeSub(t *testing.T) {

	fmt.Println("################## Sub Negative test case ###################")

	eiiDatabnsub, err := databus.NewDataBus()

	if err != nil {
		panic(err)
	}

	contextConfig["direction"] = "SUB"

	err = eiiDatabnsub.ContextCreate(contextConfig)
	if err == nil {
		panic(err)
	}

	topicConfigArray := []map[string]string{topicConfig}
	err = eiiDatabnsub.Subscribe(topicConfigArray, 1, "START", cbFunc)
	if err == nil {
		panic(err)
	}

	fmt.Println("################## Sub Negative test case completed ###################")
}

// Negative test case for contextDestroy
// ContextDestroy should fail if context is not created.
// Expected Results: Error on destroying a context.
func TestNegativeContextDestroy(t *testing.T) {
	fmt.Println("################## DataBus Negative Context Destroy Test###################")
	eiiDatabndes, err := databus.NewDataBus()

	err = eiiDatabndes.ContextDestroy()

	if err == nil {
		panic(err)
	}
	fmt.Println("################## DataBus Negative Context Destroy Test completed ###################")
}

// ToDO :This test case is failing and need fix
// Test case for message pattern and count
// Checks if all the points published are received correctly with out missing any of the points.
func TestPattern(t *testing.T) {
	fmt.Println("######################## Pattern Test ######################")

	publishcount := 0
	var keycount int
	eiiDatabsub, err := databus.NewDataBus()

	if err != nil {
		panic(err)
	}

	contextConfig["direction"] = "PUB"

	err = eiiDatabsub.ContextCreate(contextConfig)
	if err != nil {
		panic(err)
	}

	eiiDatabsub.Publish(topicConfig, "hello init")
	go sub()
	time.Sleep(10 * time.Second)
	for i := 0; i < 4; i++ {
		resultPub := fmt.Sprintf("%s %d", "Hello ", i)
		err = eiiDatabsub.Publish(topicConfig, resultPub)
		if err != nil {
			panic(err)
		}
		fmt.Println("Published result: " + resultPub)
		publishcount = i
	}

	pubStop = false
	fmt.Println("Published count is : " + strconv.Itoa(publishcount))

	for key, value := range subResults {
		intkey, _ := strconv.Atoi(key)
		if intkey > -1 {
			resultMap := fmt.Sprintf("%s %s", "Hello ", key)
			if value != resultMap {
				panic("Received results are not matching")
			}
		}
		keycount = intkey
	}

	if publishcount != keycount {
		panic("Message points are missed")
	}

	fmt.Println("##################Sub pattern Test completed###################")

}

// Test case for subscribe.
// Checks if client's subscription for a topic is successful and also if client is receivng the published points.
// Test for Subscribe API.
func TestSub(t *testing.T) {

	fmt.Println("##################Sub alone Test###################")

	eiiDatabpub, err := databus.NewDataBus()

	if err != nil {
		panic(err)
	}

	contextConfig["direction"] = "PUB"

	err = eiiDatabpub.ContextCreate(contextConfig)
	if err != nil {
		panic(err)
	}

	eiiDatabpub.Publish(topicConfig, "Hello Init")
	fmt.Print("Published result: Hello Init")
	go sub()
	time.Sleep(5 * time.Second)
	for i := 0; i < 5; i++ {
		result := fmt.Sprintf("%s %d", "Hello ", i)
		err = eiiDatabpub.Publish(topicConfig, result)
		if err != nil {
			panic(err)
		}
		fmt.Println("Published result: " + result)
	}
	pubStop = false

	time.Sleep(10 * time.Second)

	fmt.Println("##################Sub alone Test completed ###################")
}

// Test case for publish.
// Checks if server publishing points on a topic is successful.
// Test for Publish API.
func TestPub(t *testing.T) {
	fmt.Println("################## Pub alone Test ###################")
	eiiDatabpublish, err := databus.NewDataBus()

	if err != nil {
		panic(err)
	}

	contextConfig["direction"] = "PUB"

	err = eiiDatabpublish.ContextCreate(contextConfig)
	if err != nil {
		panic(err)
	}

	topicConfig := map[string]string{
		"name": contextConfig["topic"],
		"type": "string",
	}
	result := fmt.Sprintf("%s", "Hello Init ")
	err = eiiDatabpublish.Publish(topicConfig, result)
	if err != nil {
		panic(err)
	}
	fmt.Println("Published  " + result)

	fmt.Println("##################Pub alone Test completed###################")
}

// Test case for init.
// Checks if the new instance creation to Databus is successful.
// Test for NewDataBus Api.
func TestInit(t *testing.T) {
	fmt.Println("################## DataBus Init Test###################")
	eiiDatabInit, err := databus.NewDataBus()
	fmt.Println(reflect.TypeOf(eiiDatabInit))

	if err != nil {
		panic(err)
	}
	fmt.Println("################## DataBus Init Test completed ###################")
}

// 	Test case for context create.
// 	Checks if the context creation is succesful with different dirrection.
// 	Test for ContextCreate API.
func TestCreateContext(t *testing.T) {
	fmt.Println("################## DataBus Context Create Test###################")
	eiiDatabContextCreate, err := databus.NewDataBus()

	contextConfig["direction"] = "PUB"

	err = eiiDatabContextCreate.ContextCreate(contextConfig)

	if err != nil {
		panic(err)
	}

	fmt.Println("################## DataBus Context Create Test completed###################")
}

// 	Test case for context destroy
// 	When the context is created and if we want to remove the existing instance of server or client, contextDestroy
// 	removes the server and client and their configs.
// 	Test for ContextDestroy API.
func TestContextDestroy(t *testing.T) {
	fmt.Println("################## DataBus Context Destroy Test###################")
	eiiDatabContextDestroy, err := databus.NewDataBus()

	contextConfig["direction"] = "PUB"

	eiiDatabContextDestroy.ContextCreate(contextConfig)
	eiiDatabContextDestroy.ContextDestroy()

	if err != nil {
		panic(err)
	}
	fmt.Println("################## DataBus Context Destroy Test completed ###################")
}
