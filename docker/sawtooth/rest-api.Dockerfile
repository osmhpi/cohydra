FROM hyperledger/sawtooth-rest-api:1.0

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]

RUN apt update && apt -y install curl net-tools iproute

COPY ./rest-api.sh /rest-api.sh

CMD ["/rest-api.sh"]
