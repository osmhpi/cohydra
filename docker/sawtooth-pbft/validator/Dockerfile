# Copyright 2018 Cargill Incorporated
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# docker build -f validator/Dockerfile -t sawtooth-validator-local .

# -------------===  build ===-------------

FROM ubuntu:bionic

RUN apt-get update \
 && apt-get install gnupg -y curl net-tools iputils-ping

RUN echo "deb http://repo.sawtooth.me/ubuntu/chime/stable bionic universe" >> /etc/apt/sources.list \
 && (apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 8AA7AF1F1091A5FD) \
 && apt-get update

RUN apt-get install -y sawtooth sawtooth-pbft-engine

COPY sawtooth-pbft/config/validator.toml /etc/sawtooth/
COPY sawtooth-pbft/config/rest_api.toml /etc/sawtooth/

COPY sawtooth-pbft/validator/bootstrap.sh /bootstrap.sh
COPY sawtooth-pbft/validator/get_public_keys.sh /get_public_keys.sh

ENTRYPOINT [ "/bootstrap.sh" ]