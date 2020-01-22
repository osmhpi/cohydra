FROM hyperledger/sawtooth-validator:1.0

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]

RUN apt update && apt install -y iproute net-tools

COPY ./start_validator.sh /start_validator.sh

CMD [ "/start_validator.sh" ]
