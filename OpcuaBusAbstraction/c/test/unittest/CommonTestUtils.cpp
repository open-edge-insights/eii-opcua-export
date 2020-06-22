/*
Copyright (c) 2020 Intel Corporation.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/


#include <stdlib.h>
#include <CommonTestUtils.h>

void initContext(struct ContextConfig *contextConfig, char *certFile,
                 char *privateFile, char **trustFileArray, int numOfTrustFile,
                 char *endPoint, char *opType) {
    int len = 0;
    if (certFile) {
        len = strlen(certFile);
        contextConfig->certFile = reinterpret_cast<char *>(calloc(len + 1,
                                                                 sizeof(char)));
        strcpy_s(contextConfig->certFile, len + 1, certFile);
    } else {
        contextConfig->certFile = NULL;
    }

    if (privateFile) {
        len = strlen(privateFile);
        contextConfig->privateFile = reinterpret_cast<char *>(calloc(len + 1,
                                                             sizeof(char)));
        strcpy_s(contextConfig->privateFile, len + 1, privateFile);
    } else {
        contextConfig->privateFile = NULL;
    }

    if (numOfTrustFile > 0) {
        contextConfig->trustFile = reinterpret_cast<char **>(calloc(
                                               numOfTrustFile, sizeof(char *)));
        contextConfig->trustedListSize = numOfTrustFile;

        for (int i = 0; i < numOfTrustFile; i++) {
            len = strlen(trustFileArray[i]);
            contextConfig->trustFile[i] = reinterpret_cast<char *>(calloc(
                                                        len + 1, sizeof(char)));
            strcpy_s(contextConfig->trustFile[i], len + 1, trustFileArray[i]);
        }
    } else {
        contextConfig->trustFile = NULL;
        contextConfig->trustedListSize = 0;
    }

    if (endPoint) {
        len = strlen(endPoint);
        contextConfig->endpoint = reinterpret_cast<char *>(calloc(len + 1,
                                                                 sizeof(char)));
        strcpy_s(contextConfig->endpoint, len + 1, endPoint);
    } else {
        contextConfig->endpoint = NULL;
    }

    if (opType) {
        len = strlen(opType);
        contextConfig->direction = reinterpret_cast<char *>(calloc(len + 1,
                                                            sizeof(char)));
        strcpy_s(contextConfig->direction, len + 1, opType);
    } else {
        contextConfig->direction = NULL;
    }
}

void freeContext(struct ContextConfig *contextConfig) {
    if (contextConfig) {
        if (contextConfig->certFile)
            free(contextConfig->certFile);

        if (contextConfig->privateFile)
            free(contextConfig->privateFile);

        for (int i = 0; i < contextConfig->trustedListSize; i++)
            free(contextConfig->trustFile[i]);

        free(contextConfig->trustFile);

        if (contextConfig->endpoint)
            free(contextConfig->endpoint);

        if (contextConfig->direction)
            free(contextConfig->direction);
    }
}

void initTopic(struct TopicConfig *tempTopicConfig, char *topic,
               char *nmSpace, char *dataType) {
    int len = 0;
    len = strlen(dataType) + 1;
    tempTopicConfig->dType = reinterpret_cast<char *>(calloc(len,
                                                            sizeof(char)));
    strcpy_s(tempTopicConfig->dType, len, dataType);

    len = strlen(topic) + 1;
    tempTopicConfig->name = reinterpret_cast<char *>(calloc(len,
                                                           sizeof(char)));
    strcpy_s(tempTopicConfig->name, len, topic);

    len = strlen(nmSpace) + 1;
    tempTopicConfig->ns = reinterpret_cast<char *>(calloc(len,
                                                         sizeof(char)));
    strcpy_s(tempTopicConfig->ns, len, nmSpace);
}

void freeTopic(struct TopicConfig *tempTopicConfig) {
    if (tempTopicConfig->dType)
        free(tempTopicConfig->dType);

    if (tempTopicConfig->name)
        free(tempTopicConfig->name);

    if (tempTopicConfig->ns)
        free(tempTopicConfig->ns);
}
