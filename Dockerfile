# Dockerfile
ARG IEI_VERSION
FROM ia_gobase:$IEI_VERSION as base

LABEL description="OpcuaExport image"

RUN apt-get install -y libmbedtls-dev

WORKDIR /IEI/go/src/IEdgeInsights

COPY libs/DataBusAbstraction ./libs/DataBusAbstraction

#TODO: comeup with placing safestringlib build steps at one place
RUN git clone https://github.com/intel/safestringlib.git && \
        cd safestringlib && \
        git checkout 77b772849eda2321fb0dca56a321e3939930d7b9 && \
        cd include && \
        sed -i "/RSIZE_MAX_STR/c\#define RSIZE_MAX_STR      ( 60 << 10 )      /* 60KB */" "safe_str_lib.h" && \
        cd .. && \
        make

RUN cd safestringlib && \
    cp -rf libsafestring.a /IEI/go/src/IEdgeInsights/libs/DataBusAbstraction/go && \
    cp -rf libsafestring.a /IEI/go/src/IEdgeInsights/libs/DataBusAbstraction/c/open62541/src

RUN cd /IEI/go/src/IEdgeInsights/libs/DataBusAbstraction/go/test && \
    make build_lib_for_docker

COPY libs/EISMessageBus ./libs/EISMessageBus
RUN cd /IEI/go/src/IEdgeInsights/libs/EISMessageBus && \
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

RUN ln -s /IEI/go/src/IEdgeInsights/libs/EISMessageBus/go/EISMessageBus/ $GOPATH/src/EISMessageBus

COPY libs/ConfigManager ./libs/ConfigManager
COPY libs/common/go ./libs/common/go
COPY OpcuaExport ./OpcuaExport
COPY Util ./Util

RUN cd OpcuaExport && go build OpcuaExport.go
ENTRYPOINT ["./OpcuaExport/OpcuaExport"]
HEALTHCHECK NONE
