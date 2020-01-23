FROM alpine:latest

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]

RUN apk add --no-cache socat

COPY ./ping.sh /ping.sh
CMD [ "/ping.sh" ]
