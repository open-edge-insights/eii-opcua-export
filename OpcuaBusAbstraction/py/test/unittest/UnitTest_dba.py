"""
Copyright (c) 2018 Intel Corporation.

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
"""

import time
import unittest
import threading
import logging
from DataBus import databus

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s : %(levelname)s : \
                    %(name)s : [%(filename)s] :' +
                    '%(funcName)s : in line : [%(lineno)d] : %(message)s')
logger = logging.getLogger(__name__)

subscribe_results = {}
pubStop = True
count = -1
contextConfig = {
                    "endpoint": "opcua://localhost:65003",
                    "name": "StreamManager",
                    "direction": "SUB",
                    "topic": "classifier_results",
                    "certFile": "/etc/ssl/opcua/opcua_client_certificate.der",
                    "privateFile": "/etc/ssl/opcua/opcua_client_key.der",
                    "trustFile": "/etc/ssl/ca/ca_certificate.der"
                    }

topicConfig = {
                    "ns": "StreamManager",
                    "name": "classifier_results",
                    "dType": "string"
                    }


class TestDBA(unittest.TestCase):

    def cbFunc(self, topic, msg):
        global count
        if(count > -1):
            subscribe_results[str(count)] = msg
        logger.info("Msg: {} received on topic: {}".format(msg, topic))
        count = count + 1

    def subscribe(self):
        eisdbussub = databus(logger)
        contextConfigsub = {
                    "endpoint": "opcua://localhost:65003",
                    "direction": "SUB",
                    "certFile": "/etc/ssl/opcua/opcua_client_certificate.der",
                    "privateFile": "/etc/ssl/opcua/opcua_client_key.der",
                    "trustFile": "/etc/ssl/ca/ca_certificate.der"
                    }

        eisdbussub.ContextCreate(contextConfigsub)
        topicConfigs = []
        topicConfigs.append(topicConfig)
        eisdbussub.Subscribe(topicConfigs, 1, "START", self.cbFunc)
        while pubStop:
            pass

    def test_a_negativeSubTest(self):
        """
        TODO: This test case is crashing.Need fix.
        Negative test case for subscription.
        Without publishing or without starting a server,
            subscriber or client should not start.
        Expected Result: Error on Subscribing for a topic.
        """

        print("########## Testing Negative Sub Test ##########")
        eisdbusnsub = databus(logger)

        contextConfig["direction"] = "SUB"

        try:
            eisdbusnsub.ContextCreate(contextConfig)
            topicConfigs = []
            topicConfigs.append(topicConfig)
            eisdbusnsub.Subscribe(topicConfigs, 1, "START", self.cbFunc)
            while pubStop:
                pass
        except Exception as e:
            print("Error expected, Negative test case passed \
                   with error:", str(e))
        print("########## Testing Negative Sub Test Completed ##########\n\n")

    def test_b_negativeContextDestroy(self):
        """
        Negative test case for contextDestroy
        ContextDestroy should fail if context is not created.
        Expected Results: Error on destroying a context.
        """

        print("########## Testing Negative Context Destroy Test ##########")
        eisdbusndes = databus(logger)
        try:
            eisdbusndes.ContextDestroy()
        except Exception as e:
            print("Error is expected, Negative test case passed \
                   with error:", str(e))
        print("########## Testing Negative Context Destroy \
              Test Completed ##########\n\n")

    def test_c_pattern(self):
        """
        TODO: This test cases is failing.Need fix.
        Test case for message pattern and count
        Checks if all the points published are received correctly with
            out missing any of the points.
        """

        print("########## Testing message pattern ##########")
        global pubStop
        publishcount = 0
        eisdbuspat = databus(logger)

        contextConfig["direction"] = "PUB"
        eisdbuspat.ContextCreate(contextConfig)
        eisdbuspat.Publish(topicConfig, "Hello Init")
        sub_thread = threading.Thread(
            target=self.subscribe)
        sub_thread.start()
        time.sleep(5)
        for i in range(0, 3):
            result = "Hello {}".format(i)
            eisdbuspat.Publish(topicConfig, result)
            print("Published [" + result + "]")
            publishcount = i
            time.sleep(5)

        pubStop = False

        for key, value in subscribe_results.items():
            intkey = int(key)
            if(intkey > -1):
                resultmap = "Hello {}".format(key)
                if(value != resultmap):
                    raise TestDBA("Values Published and received \
                                  are not equal\n")

        if((publishcount + 1) != len(subscribe_results)):
            raise TestDBA("All the values published are not received, \
                         messages are dropped")

        print("########## Testing of  \
              message pattern completed ##########\n\n")

    def test_d_subscribe(self):
        """
        Test case for subscribe.
        Checks if client's subscription for a topic is successful and
            also if client is receivng the published points.
        Test for Subscribe API.
        """

        print("########## Testing Subscribe Test ##########")
        global pubStop
        eisdbussub = databus(logger)

        contextConfig["direction"] = "PUB"
        eisdbussub.ContextCreate(contextConfig)
        eisdbussub.Publish(topicConfig, "Hello Init")
        sub_thread = threading.Thread(
            target=self.subscribe)
        sub_thread.start()
        time.sleep(5)
        for i in range(0, 3):
            result = "Hello {}".format(i)
            eisdbussub.Publish(topicConfig, result)
            print("Published [" + result + "]")
            time.sleep(5)

        pubStop = False
        print("########## Testing Subscribe Test Completed ##########\n\n")

    def test_e_publish(self):
        """
        Test case for publish.
        Checks if server publishing points on a topic is successful.
        Test for Publish API.
        """

        print("########## Testing Publish Test ##########")
        eisdbuspub = databus(logger)

        contextConfig["direction"] = "PUB"
        eisdbuspub.ContextCreate(contextConfig)
        for i in range(0, 3):
            result = "Hello {}".format(i)
            eisdbuspub.Publish(topicConfig, result)
            print("Published [" + result + "]")
            time.sleep(5)

        print("########## Testing Publish Test Completed ##########\n\n")

    def test_f_init(self):
        """
        Test case for init.
        Checks if the new instance creation to Databus is successful.
        Test for NewDataBus Api.
        """

        print("########## Testing Init Test ##########")
        try:
            eisdbusinit = databus(logger)
        except Exception as e:
            logger.exception("Exception: {} in \
                             creating {}".format(e, eisdbusinit))
        print("########## Testing Init Test Completed ##########\n\n")

    def test_g_createContext(self):
        """
        Test case for context create.
        Checks if the context creation is succesful with different dirrection.
        Test for ContextCreate API.
        """

        print("########## Testing Context create Test ##########")
        eisdbuscreate = databus(logger)
        contextConfig["direction"] = "PUB"
        try:
            eisdbuscreate.ContextCreate(contextConfig)
        except Exception as e:
            logger.exception("Exception: {}".format(e))

        print("########## Testing Context create Test \
              Completed ##########\n\n")

    def test_h_contextDestroy(self):
        """
        Test case for context destroy
        When the context is created and if we want to remove the existing
            instance of server or client, contextDestroy removes the server
            and client and their configs.
        Test for ContextDestroy API.
        """

        print("########## Testing Context Destroy Test ##########")
        eisdbusdes = databus(logger)
        contextConfig["direction"] = "PUB"
        eisdbusdes.ContextCreate(contextConfig)
        try:
            eisdbusdes.ContextDestroy()
        except Exception as e:
            logger.exception("Exception: {}".format(e))

        print("########## Testing Context Destroy \
              Test Completed ##########\n\n")


if __name__ == "__main__":
    unittest.main()
