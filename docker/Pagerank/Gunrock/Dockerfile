FROM nvidia/cuda:12.2.0-devel-ubuntu22.04

RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    git \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

#Correct cmake version
RUN wget https://github.com/Kitware/CMake/releases/download/v3.27.9/cmake-3.27.9-linux-x86_64.sh && \
    chmod +x cmake-3.27.9-linux-x86_64.sh && \
    ./cmake-3.27.9-linux-x86_64.sh --skip-license --prefix=/usr/local && \
    rm cmake-3.27.9-linux-x86_64.sh

WORKDIR /app/datasets
COPY datasets/ .

WORKDIR /app/src
COPY src/ .

RUN git clone https://github.com/gunrock/gunrock.git && \
    cd gunrock && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make pr -j$(nproc)

CMD ["python3", "-u", "src.bench.PageRank.PRGunrockBench"]
