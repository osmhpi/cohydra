FROM hyperledger/sawtooth-settings-tp:1.0

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]

RUN apt update && apt install -y iproute net-tools

COPY ./settings-tp.sh /settings-tp.sh

CMD ["/settings-tp.sh"]
