/*
Copyright (c) 2020 Intel Corporation.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/

#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>
#include <gtest/gtest.h>
#include <CommonTestUtils.h>

#define NUM_OF_TOPICS 10
#define MSG_SIZE 100
#define TOPIC_NAME 32

char pub[] = "PUB";
char sub[] = "SUB";
char pubsub[] = "PUBSUB";

char certFile[] = "/etc/ssl/opcua/opcua_client_certificate.der";
char privateFile[] = "/etc/ssl/opcua/opcua_client_key.der";
char trustFile[] = "/etc/ssl/ca/ca_certificate.der";

char *trustStores[] = {trustFile};

char topicName[] = "ab";
char ns[] = "tm";
char dtype[] = "string";

int topicMsgCount[10] = {
    0x00,
};

int strToInt(const char *text) {
    int n = 0;
    for (; isdigit(*text); ++text) {
        n *= 10;
        n += (*text - '0');
    }
    return n;
}

void cb(const char *topic, const char *data, void *pyFunc) {
    if (topic) {
        int val = strToInt(topic + 5);
        topicMsgCount[val]++;
    }

    if (data)
        printf("Data received: topic=%s and data=%s\n", topic, data);
}

TEST(ContextCreateTestCase, NegativeTestcaseSubToWrongTopic) {
    /*Test description: This is test case which verifies
    the subscription do not for a topic which is not created.
    */
    // This test case is currenly passing
    // However it should fail. It needs fixes

    struct ContextConfig contextConfigPub;
    struct ContextConfig contextConfigSub;

    char *trustFileArray[2] = {0x00};
    trustFileArray[0] = trustFile;
    char *errorMsg = NULL;
    int isError = 0;

    initContext(&contextConfigPub, certFile, privateFile,
                trustFileArray, 1, "opcua://localhost:65008", pub);
    errorMsg = ContextCreate(contextConfigPub);
    isError = strcmp(errorMsg, "0");
    if (isError) {
        printf("ContextCreate() API failed, error: %s\n", errorMsg);
    }
    ASSERT_EQ(isError, 0);

    initContext(&contextConfigSub, certFile, privateFile,
                trustFileArray, 1, "opcua://localhost:65008", sub);
    errorMsg = ContextCreate(contextConfigSub);
    isError = strcmp(errorMsg, "0");

    if (isError) {
        printf("ContextCreate() API failed, error: %s\n", errorMsg);
    }
    ASSERT_EQ(isError, 0);


    struct TopicConfig tempTopicConfig[NUM_OF_TOPICS];
    for (int i = 0; i < NUM_OF_TOPICS; i++) {
        char topicName[TOPIC_NAME] = {
            0x00,
        };
        sprintf(topicName, "topic%d", i);
        initTopic(&tempTopicConfig[i], topicName, ns, dtype);
    }

    for (int i = 0; i < NUM_OF_TOPICS; i++) {
        char result[MSG_SIZE] = {0x00};
        sprintf(result,
                "topic-creation for:%s, Data:%d", tempTopicConfig[i].name, i);
        errorMsg = Publish(tempTopicConfig[i], result);
        isError = strcmp(errorMsg, "0");
        if (isError) {
            printf("Publish() API failed, error: %s\n", errorMsg);
        }
        ASSERT_EQ(isError, 0);
    }

    for (int i = 0; i < NUM_OF_TOPICS; i++) {
        freeTopic(&tempTopicConfig[i]);
    }

    for (int i = 0; i < NUM_OF_TOPICS; i++) {
        char topicName[TOPIC_NAME] = {
            0x00,
        };
        sprintf(topicName, "TOPIC%d", i);
        initTopic(&tempTopicConfig[i], topicName, ns, dtype);
    }

    errorMsg = Subscribe(tempTopicConfig, NUM_OF_TOPICS, "START",
                         cb, reinterpret_cast<void *>(NULL));
    isError = strcmp(errorMsg, "0");
    if (isError) {
        printf("Subscribe() API failed, error: %s\n", errorMsg);
    }

    ASSERT_EQ(isError, 0);

    ContextDestroy();
    freeContext(&contextConfigPub);
    freeContext(&contextConfigSub);
    for (int i = 0; i < NUM_OF_TOPICS; i++) {
        freeTopic(&tempTopicConfig[i]);
    }
}

int main(int argc, char **argv) {
    testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
