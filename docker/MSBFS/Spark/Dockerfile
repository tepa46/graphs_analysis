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
ENV HADOOP_HDFS_HOME=$HADOOP_HOME
ENV HADOOP_MAPRED_HOME=$HADOOP_HOME
ENV HADOOP_COMMON_HOME=$HADOOP_HOME
ENV HADOOP_COMMON_LIB_NATIVE_DIR=$HADOOP_HOME/lib/native
ENV HADOOP_OPTS="$HADOOP_OPTS -Djava.library.path=$HADOOP_HOME/lib/native"
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
ENV LD_LIBRARY_PATH=$HADOOP_HOME/lib/native

WORKDIR /app/datasets
COPY datasets/ .

WORKDIR /app/src
COPY src/ .

WORKDIR /app
COPY docker/MSBFS/Spark/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "-m", "src.bench.MSPBFS.SparkBench"]
