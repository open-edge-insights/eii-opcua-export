# Dockerfile
ARG EIS_VERSION
FROM ia_eisbase:$EIS_VERSION as eisbase

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

FROM ia_common:$EIS_VERSION as common

FROM eisbase

COPY --from=common ${GO_WORK_DIR}/common/libs ${GO_WORK_DIR}/common/libs
COPY --from=common ${GO_WORK_DIR}/common/util ${GO_WORK_DIR}/common/util
COPY --from=common ${GO_WORK_DIR}/common/cmake ${GO_WORK_DIR}/common/cmake
COPY --from=common /usr/local/lib /usr/local/lib
COPY --from=common /usr/local/include /usr/local/include
COPY --from=common ${GO_WORK_DIR}/../EISMessageBus ${GO_WORK_DIR}/../EISMessageBus
COPY --from=common ${GO_WORK_DIR}/../ConfigManager ${GO_WORK_DIR}/../ConfigManager

COPY . ./OpcuaExport/

RUN cd OpcuaExport && go build OpcuaExport.go
ENTRYPOINT ["./OpcuaExport/OpcuaExport"]
