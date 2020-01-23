FROM hyperledger/sawtooth-all:1.0

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]

RUN apt update && apt install -y iproute net-tools iputils-ping nmap

COPY ./sawtooth-shell.sh /sawtooth-shell.sh

CMD ["/sawtooth-shell.sh"]
