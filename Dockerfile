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

ARG EII_VERSION
ARG UBUNTU_IMAGE_VERSION
ARG ARTIFACTS="/artifacts"
FROM ia_common:$EII_VERSION as common
FROM ia_eiibase:${EII_VERSION} as builder
LABEL description="OpcuaExport image"
RUN apt-get update && \
    apt-get install -y libmbedtls-dev

WORKDIR ${GOPATH}/src/IEdgeInsights
ARG CMAKE_INSTALL_PREFIX
ENV CMAKE_INSTALL_PREFIX=${CMAKE_INSTALL_PREFIX}

# Install libzmq
RUN rm -rf deps && \
    mkdir -p deps && \
    cd deps && \
    wget -q --show-progress https://github.com/zeromq/libzmq/releases/download/v4.3.4/zeromq-4.3.4.tar.gz -O zeromq.tar.gz && \
    tar xf zeromq.tar.gz && \
    cd zeromq-4.3.4 && \
    ./configure --prefix=${CMAKE_INSTALL_PREFIX} && \
    make install

# Install cjson
RUN rm -rf deps && \
    mkdir -p deps && \
    cd deps && \
    wget -q --show-progress https://github.com/DaveGamble/cJSON/archive/v1.7.12.tar.gz -O cjson.tar.gz && \
    tar xf cjson.tar.gz && \
    cd cJSON-1.7.12 && \
    mkdir build && cd build && \
    cmake -DCMAKE_INSTALL_INCLUDEDIR=${CMAKE_INSTALL_PREFIX}/include -DCMAKE_INSTALL_PREFIX=${CMAKE_INSTALL_PREFIX} .. && \
    make install

COPY --from=common ${CMAKE_INSTALL_PREFIX}/include ${CMAKE_INSTALL_PREFIX}/include
COPY --from=common ${CMAKE_INSTALL_PREFIX}/lib ${CMAKE_INSTALL_PREFIX}/lib
COPY --from=common /eii/common/util/util.go ./OpcuaExport//util/util.go
COPY --from=common  ${CMAKE_INSTALL_PREFIX}/lib/libsafestring.so /usr/local/lib
COPY --from=common ${GOPATH}/src ${GOPATH}/src
COPY --from=common /eii/common/libs/EIIMessageBus/go/EIIMessageBus $GOPATH/src/EIIMessageBus
COPY --from=common /eii/common/libs/ConfigMgr/go/ConfigMgr $GOPATH/src/ConfigMgr

COPY . ./OpcuaExport/

ARG ARTIFACTS
RUN mkdir $ARTIFACTS \
          $ARTIFACTS/OpcuaExport \
          $ARTIFACTS/lib


ENV CPATH ./OpcuaExport/OpcuaBusAbstraction/c/open62541/src
ENV CFLAGS -std=c99 -g -fpic -I../include -I../../

RUN echo "Building the open62541 wrapper library libopen62541W.so.." && \
    cd ${CPATH} && gcc ${CFLAGS} -c ../../DataBus.c open62541_wrappers.c && gcc ${CFLAGS} -c open62541.c && \
    gcc -shared -o libopen62541W.so DataBus.o open62541_wrappers.o open62541.o -L/usr/local/lib -lsafestring &&  \
    rm -rf DataBus.o open62541_wrappers.o open62541.o

RUN cd ${CPATH} && cp libopen62541W.so $ARTIFACTS/lib

ENV PATH="$PATH:/usr/local/go/bin" \
    PKG_CONFIG_PATH="$PKG_CONFIG_PATH:${CMAKE_INSTALL_PREFIX}/lib/pkgconfig" \
    LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${CMAKE_INSTALL_PREFIX}/lib"

# These flags are needed for enabling security while compiling and linking with cpuidcheck in golang
ENV CGO_CFLAGS="$CGO_FLAGS -I ${CMAKE_INSTALL_PREFIX}/include -O2 -D_FORTIFY_SOURCE=2 -Werror=format-security -fstack-protector-strong -fPIC" \
    CGO_LDFLAGS="$CGO_LDFLAGS -L${CMAKE_INSTALL_PREFIX}/lib -z noexecstack -z relro -z now"

RUN cd OpcuaExport/ && GO111MODULE=on go build -o $ARTIFACTS/OpcuaExport/OpcuaExport OpcuaExport.go

RUN mv OpcuaExport/schema.json $ARTIFACTS


FROM ubuntu:$UBUNTU_IMAGE_VERSION as runtime
ARG ARTIFACTS
ARG EII_UID
ARG EII_USER_NAME
RUN groupadd $EII_USER_NAME -g $EII_UID && \
    useradd -r -u $EII_UID -g $EII_USER_NAME $EII_USER_NAME

RUN apt-get update && \
    apt-get install -y libmbedtls-dev

WORKDIR /app

ARG CMAKE_INSTALL_PREFIX
ENV CMAKE_INSTALL_PREFIX=${CMAKE_INSTALL_PREFIX}
COPY --from=builder ${CMAKE_INSTALL_PREFIX}/lib .local/lib
COPY --from=builder $ARTIFACTS .
COPY --from=builder $ARTIFACTS/lib .local/lib

RUN chown -R ${EII_UID}:${EII_UID} /tmp/ && \
    chmod -R 760 /tmp/

USER $EII_USER_NAME

ENV LD_LIBRARY_PATH ${LD_LIBRARY_PATH}:/app/.local/lib
HEALTHCHECK NONE

ENTRYPOINT ["./OpcuaExport/OpcuaExport"]
