############################################################
# Run stage
############################################################

FROM alpine

RUN apk update && apk add busybox-extras

COPY ping.sh /ping.sh
RUN chmod +x /ping.sh

CMD ["/ping.sh"]
