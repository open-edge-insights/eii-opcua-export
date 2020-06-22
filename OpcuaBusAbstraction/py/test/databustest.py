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
import argparse
import sys
import logging
from DataBus import databus

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s : %(levelname)s : \
                    %(name)s : [%(filename)s] :' +
                    '%(funcName)s : in line : [%(lineno)d] : %(message)s')
LOGGER = logging.getLogger(__name__)


class DataBusTest:
    """
      DataBusTest class
    """
    def __init__(self):
        pass

    @classmethod
    def cb_func(cls, topic, msg):
        """
          callback function
        """
        LOGGER.info("Msg: {} received on topic: {}".format(msg, topic))

    def main(self):
        """
          main function
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('-endpoint',
                            help="Provide the messagebus details (Eg: \
                            opcua://localhost:4840)")
        parser.add_argument('-direction', help="one of \'PUB | SUB\'")
        parser.add_argument('-ns', help="namespace")
        parser.add_argument('-topics',
                            help="list of comma separated topics (Eg: \
                            topic1,topic2) ")
        parser.add_argument('-certFile',
                            help="provide server/client certificate\
                            file in der format as value")
        parser.add_argument('-privateFile',
                            help="provide server or client private\
                            key file in der format as \
                                            value")
        parser.add_argument('-trustFile',
                            help="provide ca cert file in der format \
                            as value")

        args = parser.parse_args()

        context_config = {"endpoint": args.endpoint,
                          "direction": args.direction,
                          "certFile": args.certFile,
                          "privateFile": args.privateFile,
                          "trustFile": args.trustFile}
        try:
            eisdbus = databus(LOGGER)
            eisdbus.ContextCreate(context_config)
            topic_configs = []
            topics_list = args.topics.split(',')
            for topic in topics_list:
                topic_configs.append({"ns": args.ns,
                                      "name": topic,
                                      "dType": "string"})

            if args.direction == "PUB":
                for i in range(0, 20):
                    for topic_config in topic_configs:
                        result = "{0} {1}".format(topic_config["name"], i)
                        eisdbus.Publish(topic_config, result)
                        print("Published [" + result + "]")
                        time.sleep(1)
            elif args.direction == "SUB":
                eisdbus.Subscribe(topic_configs, len(topic_configs), 'START',
                                  self.cb_func)

                # flag = "START"
                while True:
                    time.sleep(60)
            else:
                raise Exception("Wrong direction flag for databus!!!")
        except KeyboardInterrupt as err:
            LOGGER.exception("Received SIGTERM signal, doing app shutdown")
            LOGGER.exception("Exception: {}".format(err))
            eisdbus.ContextDestroy()
            sys.exit(-1)
        except Exception as err:
            LOGGER.exception("Exception: {}".format(err))


if __name__ == "__main__":
    data_bus_test = DataBusTest()
    data_bus_test.main()
