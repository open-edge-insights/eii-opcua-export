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

RUN apt-get update && \
    apt-get install -y libmbedtls-dev

WORKDIR /EIS/go/src/IEdgeInsights

COPY OpcuaBusAbstraction ./OpcuaExport/OpcuaBusAbstraction

FROM ${DOCKER_REGISTRY}ia_common:$EIS_VERSION as common

FROM eisbase

COPY --from=common ${GO_WORK_DIR}/common/libs ${GO_WORK_DIR}/common/libs
COPY --from=common ${GO_WORK_DIR}/common/util ${GO_WORK_DIR}/common/util
COPY --from=common ${GO_WORK_DIR}/common/cmake ${GO_WORK_DIR}/common/cmake
COPY --from=common /usr/local/lib /usr/local/lib
COPY --from=common /usr/local/include /usr/local/include
COPY --from=common ${GO_WORK_DIR}/../EISMessageBus ${GO_WORK_DIR}/../EISMessageBus
COPY --from=common ${GO_WORK_DIR}/../ConfigMgr ${GO_WORK_DIR}/../ConfigMgr

ENV CPATH $GO_WORK_DIR/OpcuaExport/OpcuaBusAbstraction/c/open62541/src
ENV CFLAGS -std=c99 -g -fpic -I../include -I../../

RUN echo "Building the open62541 wrapper library libopen62541W.so.." && \
    cd ${CPATH} && gcc ${CFLAGS} -c ../../DataBus.c open62541_wrappers.c && gcc ${CFLAGS} -c open62541.c && \
    gcc -shared -o libopen62541W.so DataBus.o open62541_wrappers.o open62541.o -L/usr/local/lib -lsafestring &&  \
    rm -rf DataBus.o open62541_wrappers.o open62541.o

RUN cd ${CPATH} && cp libopen62541W.so /usr/local/lib

COPY . ./OpcuaExport/

RUN cd OpcuaExport && go build OpcuaExport.go

HEALTHCHECK NONE

ENTRYPOINT ["./OpcuaExport/OpcuaExport"]
