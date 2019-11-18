FROM alpine:latest

RUN apk add --no-cache socat

COPY ./ping.sh /ping.sh

CMD ["/ping.sh"]