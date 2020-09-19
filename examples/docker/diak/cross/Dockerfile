FROM python:3

EXPOSE 23400 23401 23402

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]

RUN apk add --no-cache socat

COPY ./cross.py /cross.py
CMD [ "python", "/cross.py" ]
