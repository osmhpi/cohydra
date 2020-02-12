ARG COHYDRA_TAG=

FROM osmhpi/cohydra:base${COHYDRA_TAG:+-$COHYDRA_TAG}

COPY tools /usr/local/bin
COPY cohydra $PYTHONPATH/cohydra
