ARG SN3T_TAG=

FROM mgjm/sn3t:base${SN3T_TAG:+-$SN3T_TAG}

RUN pip3 install --no-cache-dir \
	pylint \
	rope \
	&& true

WORKDIR /root/testbed
ENV PATH=${PATH}:/root/testbed/tools \
	PYLXD_WARNINGS=
RUN ln -s /root/testbed/testbed $PYTHONPATH/testbed
