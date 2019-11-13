############################################################
# Build stage
############################################################

FROM golang:1.9 as builder

# Building Beacon simple app
WORKDIR /go/src/github.com/chepeftw
RUN git clone https://github.com/chepeftw/Beacon.git
WORKDIR /go/src/github.com/chepeftw/Beacon
RUN go get && CGO_ENABLED=0 go install -a -tags netgo -ldflags '-extldflags "-static"'

RUN ldd /go/bin/Beacon | grep -q "not a dynamic executable"


############################################################
# Run stage
############################################################

FROM alpine

#RUN apk update && apk add bash

COPY ping.sh /ping.sh
RUN chmod +x /ping.sh

COPY wrapper.sh /wrapper.sh
RUN chmod +x /wrapper.sh
COPY --from=builder /go/bin/Beacon /beacon

CMD ["/ping.sh"]
