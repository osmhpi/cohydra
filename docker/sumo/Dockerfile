FROM openjdk:11.0.5-slim-buster

COPY ./filetransfer /filetransfer
WORKDIR /filetransfer
RUN javac *.java
RUN java GenTestFile