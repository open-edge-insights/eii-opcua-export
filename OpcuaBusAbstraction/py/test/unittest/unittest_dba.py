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
LOGGER = logging.getLogger(__name__)

SUBSCRIBE_RESULTS = {}
PUB_STOP = True
COUNT = -1
CONTEXT_CONFIG = {"endpoint": "opcua://localhost:65003",
                  "name": "StreamManager",
                  "direction": "SUB",
                  "topic": "classifier_results",
                  "certFile": "/etc/ssl/opcua/opcua_client_certificate.der",
                  "privateFile": "/etc/ssl/opcua/opcua_client_key.der",
                  "trustFile": "/etc/ssl/ca/ca_certificate.der"
                 }

TOPIC_CONFIG = {"ns": "StreamManager",
                "name": "classifier_results",
                "dType": "string"
               }


class TestDBA(unittest.TestCase):
    """TestDBA class
    """
    @classmethod
    def cb_func(cls, topic, msg):
        """callback function
        """
        global COUNT
        if COUNT > -1:
            SUBSCRIBE_RESULTS[str(COUNT)] = msg
        LOGGER.info("Msg: {} received on topic: {}".format(msg, topic))
        COUNT = COUNT + 1

    def subscribe(self):
        """subscribe function
        """
        eiidbussub = databus(LOGGER)
        context_config_sub = {"endpoint": "opcua://localhost:65003",
                              "direction": "SUB",
                              "certFile": "/etc/ssl/opcua/opcua_\
                              client_certificate.der",
                              "privateFile": "/etc/ssl/opcua/opcua\
                              _client_key.der",
                              "trustFile": "/etc/ssl/ca/ca_certificate.der"
                             }

        eiidbussub.ContextCreate(context_config_sub)
        topic_configs = []
        topic_configs.append(TOPIC_CONFIG)
        eiidbussub.Subscribe(topic_configs, 1, "START", self.cb_func)
        while PUB_STOP:
            pass

    def test_a_negative_sub_test(self):
        """
        TODO: This test case is crashing.Need fix.
        Negative test case for subscription.
        Without publishing or without starting a server,
            subscriber or client should not start.
        Expected Result: Error on Subscribing for a topic.
        """

        print("########## Testing Negative Sub Test ##########")
        eiidbusnsub = databus(LOGGER)

        CONTEXT_CONFIG["direction"] = "SUB"

        try:
            eiidbusnsub.ContextCreate(CONTEXT_CONFIG)
            topic_configs = []
            topic_configs.append(TOPIC_CONFIG)
            eiidbusnsub.Subscribe(topic_configs, 1, "START", self.cb_func)
            while PUB_STOP:
                pass
        except Exception as err:
            print("Error expected, Negative test case passed \
                   with error:", str(err))
        print("########## Testing Negative Sub Test Completed ##########\n\n")

    @classmethod
    def test_b_negative_context_destroy(cls):
        """
        Negative test case for contextDestroy
        ContextDestroy should fail if context is not created.
        Expected Results: Error on destroying a context.
        """

        print("########## Testing Negative Context Destroy Test ##########")
        eiidbusndes = databus(LOGGER)
        try:
            eiidbusndes.ContextDestroy()
        except Exception as err:
            print("Error is expected, Negative test case passed \
                   with error:", str(err))
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
        global PUB_STOP
        publishcount = 0
        eiidbuspat = databus(LOGGER)

        CONTEXT_CONFIG["direction"] = "PUB"
        eiidbuspat.ContextCreate(CONTEXT_CONFIG)
        eiidbuspat.Publish(TOPIC_CONFIG, "Hello Init")
        sub_thread = threading.Thread(
            target=self.subscribe)
        sub_thread.start()
        time.sleep(5)
        for i in range(0, 3):
            result = "Hello {}".format(i)
            eiidbuspat.Publish(TOPIC_CONFIG, result)
            print("Published [" + result + "]")
            publishcount = i
            time.sleep(5)

        PUB_STOP = False

        for key, value in SUBSCRIBE_RESULTS.items():
            intkey = int(key)
            if intkey > -1:
                resultmap = "Hello {}".format(key)
                if value != resultmap:
                    raise TestDBA("Values Published and received \
                                  are not equal\n")

        if (publishcount + 1) != len(SUBSCRIBE_RESULTS):
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
        global PUB_STOP
        eiidbussub = databus(LOGGER)

        CONTEXT_CONFIG["direction"] = "PUB"
        eiidbussub.ContextCreate(CONTEXT_CONFIG)
        eiidbussub.Publish(TOPIC_CONFIG, "Hello Init")
        sub_thread = threading.Thread(
            target=self.subscribe)
        sub_thread.start()
        time.sleep(5)
        for i in range(0, 3):
            result = "Hello {}".format(i)
            eiidbussub.Publish(TOPIC_CONFIG, result)
            print("Published [" + result + "]")
            time.sleep(5)

        PUB_STOP = False
        print("########## Testing Subscribe Test Completed ##########\n\n")

    @classmethod
    def test_e_publish(cls):
        """
        Test case for publish.
        Checks if server publishing points on a topic is successful.
        Test for Publish API.
        """

        print("########## Testing Publish Test ##########")
        eiidbuspub = databus(LOGGER)

        CONTEXT_CONFIG["direction"] = "PUB"
        eiidbuspub.ContextCreate(CONTEXT_CONFIG)
        for i in range(0, 3):
            result = "Hello {}".format(i)
            eiidbuspub.Publish(TOPIC_CONFIG, result)
            print("Published [" + result + "]")
            time.sleep(5)

        print("########## Testing Publish Test Completed ##########\n\n")

    @classmethod
    def test_f_init(cls):
        """
        Test case for init.
        Checks if the new instance creation to Databus is successful.
        Test for NewDataBus Api.
        """

        print("########## Testing Init Test ##########")
        try:
            eiidbusinit = databus(LOGGER)
        except Exception as err:
            LOGGER.exception("Exception: {} in \
                             creating {}".format(err, eiidbusinit))
        print("########## Testing Init Test Completed ##########\n\n")

    @classmethod
    def test_g_create_context(cls):
        """
        Test case for context create.
        Checks if the context creation is succesful with different dirrection.
        Test for ContextCreate API.
        """

        print("########## Testing Context create Test ##########")
        eiidbuscreate = databus(LOGGER)
        CONTEXT_CONFIG["direction"] = "PUB"
        try:
            eiidbuscreate.ContextCreate(CONTEXT_CONFIG)
        except Exception as err:
            LOGGER.exception("Exception: {}".format(err))

        print("########## Testing Context create Test \
              Completed ##########\n\n")

    @classmethod
    def test_h_context_destroy(cls):
        """
        Test case for context destroy
        When the context is created and if we want to remove the existing
            instance of server or client, contextDestroy removes the server
            and client and their configs.
        Test for ContextDestroy API.
        """

        print("########## Testing Context Destroy Test ##########")
        eiidbusdes = databus(LOGGER)
        CONTEXT_CONFIG["direction"] = "PUB"
        eiidbusdes.ContextCreate(CONTEXT_CONFIG)
        try:
            eiidbusdes.ContextDestroy()
        except Exception as err:
            LOGGER.exception("Exception: {}".format(err))

        print("########## Testing Context Destroy \
              Test Completed ##########\n\n")


if __name__ == "__main__":
    unittest.main()
