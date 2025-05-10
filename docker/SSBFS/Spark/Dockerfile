FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    python3 \
    python3-pip \
    python3-venv \
    wget \
    openjdk-18-jdk \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt

WORKDIR /opt
RUN wget -q https://dlcdn.apache.org/hadoop/common/hadoop-3.4.1/hadoop-3.4.1.tar.gz -O /tmp/hadoop.tar.gz \
    && tar -xzf /tmp/hadoop.tar.gz -C /opt/ \
    && rm /tmp/hadoop.tar.gz \
    && mv /opt/hadoop-3.4.1 /opt/hadoop

# ENV JAVA_HOME=/usr/lib/jvm/java-18-openjdk-arm64
ENV JAVA_HOME=/usr/lib/jvm/java-18-openjdk-amd64
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

WORKDIR /datasets
COPY datasets .

WORKDIR /app/src

COPY parent_bfs/Spark/requirements.txt .
COPY parent_bfs/Spark/SparkPG.py .
COPY parent_bfs/Spark/bench_runner.py .
COPY algo.py .
COPY bench.py .
COPY utils.py .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "-u", "bench_runner.py"]
