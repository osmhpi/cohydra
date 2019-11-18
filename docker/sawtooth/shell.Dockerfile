FROM hyperledger/sawtooth-all:1.0

RUN apt update && apt install -y iproute net-tools iputils-ping nmap

COPY ./sawtooth-shell.sh /sawtooth-shell.sh

CMD ["/sawtooth-shell.sh"]