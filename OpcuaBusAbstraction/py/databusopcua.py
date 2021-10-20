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

import open62541W

# TODO: This brings in a limitation of multiple different contexts
# if one wants to receive the callbacks registered for different
# streams from a single process. Need to implement this better
FUNC = None
G_QUEUE = None


def cb_func(topic, msg):
    """callback function
    """
    # TODO: Find the root cause for this behavior and fix it
    # This is to address extra character that seems to come in the json
    # formatted `msg` C string in pyx callback
    # Here, number 123 and 125 refers to ascii values of "{" and "}"
    # respectively
    if msg[0] == 123 and msg[-1] != 125:
        last_brace_index = msg.rfind(125)
        msg_byte_arr = bytearray(msg)
        # This is to ignore the 2 additional hex chars eg. \x01\x02
        msg = bytes(msg_byte_arr[:last_brace_index+1])
    msg = msg.decode("utf-8")
    topic = topic.decode("utf-8")
    G_QUEUE.put({"topic": topic, "data": msg})


class DatabOpcua:
    '''Creates and manages a databus OPCUA context'''

    def __init__(self, log):
        self.logger = log
        self.direction = None
        self.dev_mode = False

    def create_context(self, context_config):
        '''Creates a new messagebus context
        Arguments:
            context_config<dict>: Messagebus params to create the context
                <fields>
                "direction": PUB/SUB/NONE - Mutually exclusive
                "name": context namespace (PUB/SUB context namespaces
                        match)
                "endpoint": messagebus endpoint address
                    <format> proto://host:port/, proto://host:port/.../
                    <examples>
                    OPCUA -> opcua://0.0.0.0:65003
                "cert_file"   : server/client certificate file
                "private_file": server/client private key file
                "trust_file"  : ca cert used to sign server/client cert
        Return/Exception: Will raise Exception in case of errors'''
        cert_file = context_config["certFile"]
        private_file = context_config["privateFile"]
        trust_files = [context_config["trustFile"]]

        if not cert_file or not private_file or not trust_files:
            self.dev_mode = True

        self.direction = context_config["direction"]
        # Create default endpoint protocol for opcua from given endpoint
        endpoint = context_config["endpoint"]

        err_msg = open62541W.ContextCreate(endpoint,
                                           self.direction,
                                           context_config["certFile"],
                                           context_config["privateFile"],
                                           [context_config["trustFile"]])
        py_error_msg = err_msg.decode()
        if py_error_msg != "0":
            self.logger.error("ContextCreate() API failed!")
            raise Exception(py_error_msg)

    def start_topic(self, topic_config):
        '''
        Topic creation for the messagebus
        Arguments:
            topic_config<dict>: Publish topic parameters
                <fields>
                "name": Topic name (in hierarchical form with '/' as delimiter)
                    <example> "root/level1/level2/level3"
                "type": Data type associated with the topic
        Return/Exception: Will raise Exception in case of errors
        '''

    def send(self, topic_config, data):
        '''
        Publish data on the topic
        Arguments:
            topic_config: topic_config for opcua, with topic name & it's type
            data: actual message
        Return/Exception: Will raise Exception in case of errors
        '''

        if self.direction == "PUB":
            # TODO: Support for different data types
            if isinstance(data, str):
                try:
                    err_msg = open62541W.Publish(topic_config, data)
                    py_error_msg = err_msg.decode()
                    if py_error_msg != "0":
                        self.logger.error("Publish() API failed!")
                        raise Exception(py_error_msg)
                except Exception:
                    self.logger.exception("{} Failure!!!".format(
                        self.send.__name__))
                    raise
            else:
                raise Exception("Wrong Data Type!!!")
        else:
            raise Exception("Wrong Bus Direction!!!")

    def receive(self, topic_configs, topic_config_count, trig, queue):
        '''Subscribe data from the topic
        Arguments:
            topic_configs: topic_configs for opcua, with topic name & it's type
            topic_config_count: length of topic_configs dict
            trig: START/STOP to start/stop the subscription
            queue: A queue to which the message should be pushed on arrival
        Return/Exception: Will raise Exception in case of errors'''

        if (self.direction == "SUB") and (trig == "START"):
            global G_QUEUE
            G_QUEUE = queue
            err_msg = open62541W.Subscribe(topic_configs, topic_config_count, trig,
                                           cb_func)
            py_error_msg = err_msg.decode()
            if py_error_msg != "0":
                self.logger.error("Subscribe() API failed!")
                raise Exception(py_error_msg)
        elif (self.direction == "SUB") and (trig == "STOP"):
            # TODO: To be implemented - stop subscription
            pass
        else:
            raise Exception("Wrong Bus Direction or Trigger!!!")

    def stop_topic(self, topic):
        '''Delete topic
        Arguments:
            topic_config<dict>: Topic parameters
                <fields>
                "name": Topic name
                "type": Data type associated with the topic
        Return/Exception: Will raise Exception in case of errors'''

        # TODO:
        # if self.direction == "PUB":
        #    objs = self.server.get_objects_node()
        #    obj_itr = objs
        #    topic_ls = topic.split("/")
        #    for topic in topic_ls[0:]:
        #        try:
        #            child = obj_itr.get_child("{}:{}".format(self.nsIndex,
        #                                                      topic))
        #        except Exception as e:
        #            print(type(e).__name__)
        #            return
        #        obj_itr = child
        #    # Now get & delete the variable object
        #    var = obj_itr.get_child("{}:{}".format(self.nsIndex,
        #                                       "{}_var".format(topic_ls[-1])))
        #    # delete the var & object
        #    var.delete()

        #    obj_itr.delete()
        return

    def destroy_context(self):
        '''Destroy the messagebus context'''
        try:
            open62541W.ContextDestroy()
            self.logger.debug("OPCUA context is Terminated")
        except Exception:
            self.logger.exception("{} Failure!!!".format(
                self.destroy_context.__name__))
            raise
