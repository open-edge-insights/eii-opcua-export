# Dockerfile
ARG EIS_VERSION
FROM ia_gobase:$EIS_VERSION as base

LABEL description="OpcuaExport image"

RUN apt-get install -y libmbedtls-dev

WORKDIR /EIS/go/src/IEdgeInsights




COPY OpcuaBusAbstraction ./libs/OpcuaBusAbstraction

RUN cd safestringlib && \
    cp -rf libsafestring.a /EIS/go/src/IEdgeInsights/libs/OpcuaBusAbstraction/go && \
    cp -rf libsafestring.a /EIS/go/src/IEdgeInsights/libs/OpcuaBusAbstraction/c/open62541/src

RUN cd /EIS/go/src/IEdgeInsights/libs/OpcuaBusAbstraction/go/test && \
    make build_lib_for_docker


RUN cd /EIS/go/src/IEdgeInsights/libs/EISMessageBus && \
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

COPY . ./OpcuaExport/


RUN cd OpcuaExport && go build OpcuaExport.go
ENTRYPOINT ["./OpcuaExport/OpcuaExport"]
HEALTHCHECK NONE
