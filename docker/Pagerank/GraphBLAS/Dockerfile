FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /opt
RUN git clone -b v10.0.3 https://github.com/DrTimothyAldenDavis/GraphBLAS.git && \
    cd GraphBLAS && \
    make && \
    make install && \
    ldconfig

WORKDIR /app/datasets
COPY datasets/ .

WORKDIR /app/src
COPY src/ .

WORKDIR /app
COPY docker/Pagerank/GraphBLAS/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "-m", "src.bench.PageRank.GBBenchRunner"]
