FROM python:3.12-slim

ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8
ENV TZ=Asia/Kolkata

# Define a folder for worker metrics
ENV PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus-multiproc-dir
RUN apt-get update  \
     &&  apt-get -y install vim python3-pip
     
# Create the folder
RUN mkdir -p $PROMETHEUS_MULTIPROC_DIR

# Set the working directory
WORKDIR /app
COPY requirements.txt .

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x run.sh

ENTRYPOINT [ "/bin/bash", "run.sh" ]