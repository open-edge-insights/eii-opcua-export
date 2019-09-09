# Dockerfile
ARG EIS_VERSION
FROM ia_gobase:$EIS_VERSION as gobase

LABEL description="OpcuaExport image"

RUN apt-get install -y libmbedtls-dev

WORKDIR /EIS/go/src/IEdgeInsights

COPY OpcuaBusAbstraction ./libs/OpcuaBusAbstraction

RUN cd safestringlib && \
    cp -rf libsafestring.a /EIS/go/src/IEdgeInsights/libs/OpcuaBusAbstraction/go && \
    cp -rf libsafestring.a /EIS/go/src/IEdgeInsights/libs/OpcuaBusAbstraction/c/open62541/src

ENV CPATH $GO_WORK_DIR/libs/OpcuaBusAbstraction/c/open62541/src
ENV CFLAGS -std=c99 -g -I../include -I../../

RUN echo "Building the open62541 wrapper library libopen62541W.a.." && \
    cd ${CPATH} && gcc ${CFLAGS} -c ../../DataBus.c open62541_wrappers.c && gcc ${CFLAGS} -c open62541.c && \
    ar crU libopen62541W.a DataBus.o open62541_wrappers.o open62541.o && ar crU libsafestring.a DataBus.o open62541_wrappers.o open62541.o && \
    rm -rf DataBus.o open62541_wrappers.o open62541.o

FROM ia_common:$EIS_VERSION as common

FROM gobase

COPY --from=common /libs ${GO_WORK_DIR}/libs
COPY --from=common /util ${GO_WORK_DIR}/util

RUN cd ${GO_WORK_DIR}/libs/EISMessageBus && \
    rm -rf build deps && mkdir -p build && cd build && \
    cmake -DWITH_GO=ON .. && \
    make && \
    make install

ENV MSGBUS_DIR $GO_WORK_DIR/libs/EISMessageBus
ENV LD_LIBRARY_PATH $LD_LIBRARY_PATH:$MSGBUS_DIR/build/
ENV PKG_CONFIG_PATH $PKG_CONFIG_PATH:$MSGBUS_DIR/build/
ENV CGO_CFLAGS -I$MSGBUS_DIR/include/
ENV CGO_LDFLAGS -L$MSGBUS_DIR/build -leismsgbus
ENV LD_LIBRARY_PATH ${LD_LIBRARY_PATH}:/usr/local/lib

RUN ln -s ${GO_WORK_DIR}/libs/EISMessageBus/go/EISMessageBus/ $GOPATH/src/EISMessageBus

COPY . ./OpcuaExport/

RUN cd OpcuaExport && go build OpcuaExport.go
ENTRYPOINT ["./OpcuaExport/OpcuaExport"]
