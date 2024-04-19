# Use Ubuntu 20.04 as a base image
FROM ubuntu:20.04

# Set up a working directory
WORKDIR /app

# Copy all files in the dash-ll-server folder to the /app directory
COPY ./* /app/

RUN chmod -R 777 /app

# Add execute permissions to the scripts
RUN chmod +x /app/run_server.sh && \
    chmod +x /app/run_gen.sh

# Update the apt package manager and install python 3.10.14 and its required components
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.10 python3.10-dev libxcb1 libvpx6 libx264-dev


RUN apt-get install -y python3-pip

EXPOSE 9001
EXPOSE 3000

# Setting environment variables
ENV PYTHONUNBUFFERED=1

CMD ["/app/run_server.sh"]
