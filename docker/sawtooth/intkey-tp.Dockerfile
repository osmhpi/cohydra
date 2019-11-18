FROM hyperledger/sawtooth-intkey-tp-python:1.0

RUN apt update && apt install -y iproute net-tools

COPY ./intkey-tp.sh /intkey-tp.sh

CMD ["/intkey-tp.sh"]