# Use the official golang image as the base image
FROM golang:1.19 AS build

WORKDIR /app

COPY ./* /app/

RUN go build -o main main.go

EXPOSE 9001

CMD ["./main -port 9001 -directory media"]
