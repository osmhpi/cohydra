FROM hyperledger/sawtooth-settings-tp:1.0

RUN apt update && apt install -y iproute net-tools

COPY ./settings-tp.sh /settings-tp.sh

CMD ["/settings-tp.sh"]