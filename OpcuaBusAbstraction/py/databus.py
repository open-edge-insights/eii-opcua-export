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

from threading import Event
from threading import Thread, Lock
from queue import Queue
from databusopcua import DatabOpcua

# type of DataBus
BUS_TYPES = {"OPCUA": "opcua:"}


def worker(data_q, event, func, log):
    '''! Worker function to fetch data from queue and trigger call_bck
    @param data_q(Queue)    queue to store/get data
    @param event(Event)    event to notify the worker thread status
    @param func(callback) that sends out the subscribed data back to the caller
    @param              log logger object
    '''

    logger = log
    while True:
        if event.is_set():
            logger.info("Worker Done")
            break
        try:
            sub_dict = data_q.get(timeout=2)
            func(sub_dict["topic"], sub_dict["data"])
            data_q.task_done()
        except Exception:
            # TODO: pass only for Empty exception
            # logger.error("Exception passed")
            pass
    return

# TODO: This library needs to be architected well to have an
# interface which needs to be implemented by it's sub-classes


class DataBus:
    """DataBus class
    """

    def __init__(self, log):
        """! Creates an instance of DataBus"""

        self.logger = log
        self.bus_type = None
        self.direction = "NONE"
        self.pub_topics = {}
        self.sub_topics = {}
        self.bus = None
        self.mutex = Lock()

    def context_create(self, contextcreate):

        '''! context_create function creates the opcua server/client (pub/sub)
             context based on `contextcreate`.direction field
        @param contextcreate(dict)  contextcreate for opcua pub/sub
                                    publisher (server) - If all certs/keys are
                                    set to empty string in contextcreate,the
                                    opcua server starts in insecure mode.
                                    If not, it starts in secure mode.

                                    subscriber (client)- If all certs/keys are
                                    set to empty string in contextcreate,the
                                    opcua client tries to establishes insecure
                                    connection. If not, it tries to establish
                                    secure connection with the opcua server

               contextcreate(dict) fields:
                 - "direction"       : PUB/SUB/NONE - Mutually exclusive
                 - "endpoint"        : messagebus endpoint address
                                       ex:OPCUA -> opcua://0.0.0.0:4840/
                 - "certFile"        : server/client certificate file
                 - "privateFile"     : server/client private key file
                 - "trustFile"       : ca cert used to sign server/client cert
                 - "trustedListSize" : number of trustFiles
         @return Exception: raise Exception in case of errors
        '''
        try:
            self.mutex.acquire()
            endpoint = contextcreate["endpoint"]
            # TODO: Check for unique pub/sub contextName?
            if endpoint.split('//')[0] == BUS_TYPES["OPCUA"]:
                self.bus_type = BUS_TYPES["OPCUA"]
                self.bus = DatabOpcua(self.logger)
            else:
                raise Exception("Not a supported bus_type")
            self.logger.info(contextcreate)
            try:
                self.bus.create_context(contextcreate)
            except Exception:
                self.logger.exception("{} Failure!!!".format(
                    self.context_create.__name__))
                raise
            if contextcreate["direction"] == "PUB":
                self.direction = "PUB"
            elif contextcreate["direction"] == "SUB":
                self.direction = "SUB"
            else:
                raise Exception("Not a supported BusDirection")
        finally:
            self.mutex.release()

    def publish(self, topic_config, data):

        '''! publish function for publishing the data by opcua server process
        @param  topic_config(dict)   opcua `struct TopicConfig` structure

                topic_config(dict) fields:
                  - "ns"  : Namespace name
                  - "name": Topic name
                  - "type": Data type associated with the topic
        @param  data(string)        data to be written to opcua variable
        @return Exception:  raise Exception in case of errors
        '''

        if "opcua" in self.bus_type:
            try:
                self.bus.send(topic_config, data)
            except Exception:
                self.logger.exception("{} Failure!!!".format(
                    self.publish.__name__))
                raise

    def subscribe(self, topic_config, topic_config_count, trig, call_bck=None):

        '''! subscribe function makes the subscription to the list of
             opcua variables (topics) in topic_config array
        @param  topic_config(array)    array of topic_config instances

                topic_config(dict) fields:
                  - "ns"  : Namespace name
                  - "name": Topic name
                  - "type": Data type associated with the topic
        @param  topic_configCount(int) length of topic_config array
        @param  trig(string)          opcua trigger ex: START | STOP
        @param  call_bck(c_callback)  callback that sends out the subscribed
                                      data back to the caller
        @return Exception:  raise Exception in case of errors
        '''

        if "opcua" in self.bus_type:
            try:
                if (self.direction == "SUB") and (trig == "START") and \
                   (call_bck is not None):
                    data_q = Queue()
                    event = Event()
                    event.clear()
                    thread = Thread(target=worker,
                                    args=(data_q, event, call_bck,
                                          self.logger))
                    thread.deamon = True
                    thread.start()
                    self.bus.receive(topic_config, topic_config_count,
                                     "START", data_q)
            except Exception:
                self.logger.exception("receive {} Failure!!!".format(
                    self.subscribe.__name__))
                raise

    def context_destroy(self):

        '''! context_destroy function destroys the opcua server/client
             context
        '''

        try:
            if "opcua" in self.bus_type:
                self.mutex.acquire()
                try:
                    self.bus.destroy_context()
                    self.bus.direction = " "
                except Exception:
                    self.logger.error("{} Failure!!!".format(
                        self.context_destroy.__name__))
                    raise
                finally:
                    self.mutex.release()
        except Exception:
            self.logger.exception("{} Failure!!!".format(
                self.context_destroy.__name__))
            raise
