# Copyright (c) 2020 Intel Corporation.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Dockerfile

ARG EIS_VERSION
ARG DOCKER_REGISTRY
FROM ${DOCKER_REGISTRY}ia_eisbase:$EIS_VERSION as eisbase

LABEL description="OpcuaExport image"

RUN apt-get install -y libmbedtls-dev

WORKDIR /EIS/go/src/IEdgeInsights

COPY OpcuaBusAbstraction ./OpcuaExport/OpcuaBusAbstraction

RUN cd safestringlib && \
    cp -rf libsafestring.a /EIS/go/src/IEdgeInsights/OpcuaExport/OpcuaBusAbstraction/go && \
    cp -rf libsafestring.a /EIS/go/src/IEdgeInsights/OpcuaExport/OpcuaBusAbstraction/c/open62541/src

ENV CPATH $GO_WORK_DIR/OpcuaExport/OpcuaBusAbstraction/c/open62541/src
ENV CFLAGS -std=c99 -g -I../include -I../../

RUN echo "Building the open62541 wrapper library libopen62541W.a.." && \
    cd ${CPATH} && gcc ${CFLAGS} -c ../../DataBus.c open62541_wrappers.c && gcc ${CFLAGS} -c open62541.c && \
    ar crU libopen62541W.a DataBus.o open62541_wrappers.o open62541.o && ar crU libsafestring.a DataBus.o open62541_wrappers.o open62541.o && \
    rm -rf DataBus.o open62541_wrappers.o open62541.o

FROM ${DOCKER_REGISTRY}ia_common:$EIS_VERSION as common

FROM eisbase

COPY --from=common ${GO_WORK_DIR}/common/libs ${GO_WORK_DIR}/common/libs
COPY --from=common ${GO_WORK_DIR}/common/util ${GO_WORK_DIR}/common/util
COPY --from=common ${GO_WORK_DIR}/common/cmake ${GO_WORK_DIR}/common/cmake
COPY --from=common /usr/local/lib /usr/local/lib
COPY --from=common /usr/local/include /usr/local/include
COPY --from=common ${GO_WORK_DIR}/../EISMessageBus ${GO_WORK_DIR}/../EISMessageBus
COPY --from=common ${GO_WORK_DIR}/../ConfigManager ${GO_WORK_DIR}/../ConfigManager
COPY --from=common ${GO_WORK_DIR}/../EnvConfig ${GO_WORK_DIR}/../EnvConfig

COPY . ./OpcuaExport/

RUN cd OpcuaExport && go build OpcuaExport.go
ENTRYPOINT ["./OpcuaExport/OpcuaExport"]
