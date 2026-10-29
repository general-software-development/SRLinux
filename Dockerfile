FROM ghcr.io/astral-sh/uv:latest AS uv
FROM python:3.12-slim AS filesystem

WORKDIR /

RUN mkdir -p /srl/pkg
RUN mkdir -p /srl/bin
RUN mkdir -p /opt/srlinux
RUN mkdir -p /media/srl-install/astral-sh.uv
RUN mkdir -p /media/srl-install/srl.syspkg
RUN ln -s /srl/pkg /opt/srlinux/packages
RUN ln -s /srl/pkg /srl/packages
RUN ln -s /media/srl-install/astral-sh.uv/uv /usr/sbin/uv
RUN ln -s /media/srl-install/astral-sh.uv/uvx /usr/sbin/uvx
RUN ln -s /srl/bin /usr/srl
RUN ln -s /media/srl-install/srl.syspkg/bin/syspkg /srl/bin/syspkg
RUN ln -s /media/srl-install/srl.syspkg/bin/pkg /srl/bin/pkg

ENV PATH="/usr/srl:${PATH}"


FROM filesystem AS get-files

COPY --from=uv /uv /uvx /media/srl-install/astral-sh.uv

WORKDIR /opt/srlinux

COPY syspkg/pyproject.toml syspkg/README.md ./
COPY syspkg/src ./src
COPY syspkg/packages/ ./packages/


FROM filesystem AS environment

RUN apt-get update && \
    apt-get install -y --no-install-recommends zsh

# use --allow-remove-essential to tell apt we know what were doing :D
RUN apt-get remove -y bash --allow-remove-essential

SHELL ["/bin/zsh", "-c"]

RUN ln -s /usr/bin/zsh /usr/bin/bash

RUN apt install build-essential -y

FROM environment AS final

WORKDIR /opt/srlinux/

COPY --from=get-files /opt/srlinux /opt/srlinux
COPY --from=get-files /srl/pkg/ /srl/pkg/
COPY --from=get-files /media/srl-install /media/srl-install

RUN uv sync && uv pip install --no-cache-dir --prefix=/media/srl-install/srl.syspkg .

RUN rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["zsh"]

# docker build -t srlinux .
# docker run --rm -it srlinux
