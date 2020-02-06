ARG NS3_TAG=3.30-python3

FROM mgjm/ns-3:$NS3_TAG

RUN apt-get update && \
	apt-get install -y --no-install-recommends \
	git \
	python3-pip \
	python3-setuptools \
	&& \
	apt-get autoremove -y && \
	apt-get clean -y && \
	rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
	coloredlogs \
	docker \
	nsenter \
	paramiko \
	pyroute2 \
	pyyaml \
	git+https://github.com/active-expressions/active-expressions-static-python

ENV COLOREDLOGS_DATE_FORMAT="%H:%M:%S" \
	COLOREDLOGS_LOG_FORMAT="%(asctime)s %(name)-32s %(levelname)-8s %(message)s" \
	COLOREDLOGS_LOG_LEVEL="DEBUG" \
	COLOREDLOGS_LEVEL_STYLES="debug=cyan;warning=yellow;error=red;critical=red,bold" \
	COLOREDLOGS_AUTO_INSTALL="true"
