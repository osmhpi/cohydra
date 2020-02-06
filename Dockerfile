ARG SN3T_TAG=

FROM mgjm/sn3t:base${SN3T_TAG:+-$SN3T_TAG}

COPY tools /usr/local/bin
COPY cohydra $PYTHONPATH/cohydra
