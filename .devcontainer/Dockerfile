FROM debian:10

ENV DEBIAN_FRONTEND=noninteractive

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create a non-root user
RUN groupadd --gid $USER_GID $USERNAME && \
    useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME

RUN apt-get update

# Add sudo support for the non-root user
RUN apt-get install -y sudo && \
    echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME

RUN apt-get install -y --no-install-recommends pipenv curl bzip2 make git g++ python3-dev cmake llvm-dev libclang-dev qt5-default patch

# # Verify git, process tools, lsb-release (common in install instructions for CLIs) installed
# RUN apt-get -y install git iproute2 procps lsb-release \

# # Clean up
# RUN apt-get autoremove -y && \
#     apt-get clean -y && \
#     rm -rf /var/lib/apt/lists/*

ENV DEBIAN_FRONTEND=

RUN mkdir /home/$USERNAME/ns3 && chown $USERNAME /home/$USERNAME/ns3
