# 使用官方的 golang 镜像作为基础镜像
FROM golang:1.19 AS build

# 设置工作目录
WORKDIR /app

# 复制项目文件到工作目录
COPY ./* /app/

RUN go get github.com/lucas-clemente/quic-go

RUN go get github.com/lucas-clemente/quic-go/http3

# 构建 Go 项目
RUN go build -o main main.go

EXPOSE 9001

# 设置容器启动时执行的命令
CMD ["/app/run_server.sh"]
