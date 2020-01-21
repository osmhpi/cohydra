FROM rs22/ns3:netanim-bindings

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    git \
    python3-pip \
 && rm -rf /var/lib/apt/lists/*

RUN pip3 install pipenv

ENV DEBIAN_FRONTEND=

WORKDIR /app

COPY Pipfile Pipfile.lock ./
RUN pipenv install --deploy --system

COPY testbed/ testbed/
COPY examples/ examples/
COPY docker/ docker/

ENV PYTHONPATH="/app:${PYTHONPATH}"
