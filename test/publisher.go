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
	"flag"
	"time"
        "os"
        "strconv"
        "github.com/golang/glog"
)

func main() {
	portArg := flag.String("port", "", "port")
	topic := flag.String("topic", "", "topic")
	flag.Parse()
        flag.Lookup("alsologtostderr").Value.Set("true")
        defer glog.Flush()

        port, err := strconv.ParseInt(*portArg, 10, 64)
	if err != nil {
		glog.Errorf("string to int64 converstion Error: %v", err)
		os.Exit(1)
	}

        host := map[string]interface{}{
		"host": "*",
		"port": port,
	}
        config := map[string]interface{}{
		"type": "zmq_tcp",
		"zmq_tcp_publish": host,
	}


	glog.Infof("-- Initializing message bus context")
	client, err := eismsgbus.NewMsgbusClient(config)
	if err != nil {
		glog.Errorf("-- Error initializing message bus context: %v\n", err)
		return
	}
	defer client.Close()

	glog.Infof("-- Creating publisher for topic %s\n", *topic)
	publisher, err := client.NewPublisher(*topic)
	if err != nil {
		glog.Errorf("-- Error creating publisher: %v\n", err)
		return
	}
	defer publisher.Close()

	glog.Infof("-- Running...")
	msg := map[string]interface{}{"hello": "world"}
	for {
		err = publisher.Publish(msg)
		if err != nil {
			glog.Errorf("-- Failed to publish message: %v\n", err)
			return
		}
		time.Sleep(1 * time.Second)
	}
}
