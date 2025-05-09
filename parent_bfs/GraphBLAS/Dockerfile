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

WORKDIR /datasets
COPY datasets .

WORKDIR /app/src

COPY parent_bfs/GraphBLAS/requirements.txt .
COPY parent_bfs/GraphBLAS/SingleSourceParentBFSAlgo.py .
COPY parent_bfs/GraphBLAS/bench_runner.py .
COPY algo.py .
COPY bench.py .
COPY utils.py .

RUN pip install --no-cache-dir -r requirements.txt

#CMD ["python3", "-u", "bench_runner.py"]
