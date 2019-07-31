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

COPY libs/common/go ./libs/common/go
COPY OpcuaExport ./OpcuaExport

RUN cd OpcuaExport && go build OpcuaExport.go
ENTRYPOINT ["./OpcuaExport/OpcuaExport"]
HEALTHCHECK NONE
