ARG SN3T_TAG=

FROM mgjm/sn3t:base${SN3T_TAG:+-$SN3T_TAG}

RUN apt-get update && \
	apt-get install -y --no-install-recommends \
	sudo \
	&& \
	apt-get autoremove -y && \
	apt-get clean -y && \
	rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
	pylint \
	rope \
	&& true

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME && \
	useradd --create-home --shell /bin/bash --uid $USER_UID --gid $USER_GID $USERNAME && \
	echo "$USERNAME ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/$USERNAME && \
	chmod 440 /etc/sudoers.d/$USERNAME && \
	mkdir -p /workspace/testbed && \
	chown -R $USERNAME:$USERNAME /workspace

WORKDIR /workspace/testbed
ENV PATH=${PATH}:/workspace/testbed/tools
RUN ln -s /workspace/testbed/testbed $PYTHONPATH/testbed

USER $USERNAME
