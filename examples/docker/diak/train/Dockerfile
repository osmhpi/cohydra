FROM alpine:latest

EXPOSE 23400 23401 23402

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]

RUN apk add --no-cache socat
RUN apk add --no-cache python
RUN apk add --no-cache python3


COPY ./train.py /train.py
CMD [ "python3", "/train.py" ]
