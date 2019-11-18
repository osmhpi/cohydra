FROM hyperledger/sawtooth-intkey-tp-python:1.0

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]

RUN apt update && apt install -y iproute net-tools

COPY ./intkey-tp.sh /intkey-tp.sh

CMD ["/intkey-tp.sh"]
