# Graph Algorithms Performance Analysis

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Overview

This academic project serves as a platform for benchmarking graph algorithms across multiple libraries

### Algorithms and Implementations

1. **PageRank**:
    - Implementation using Gunrock (Elkin)
    - Implementation using Spark  (Pavlushkin)
    - Implementation using GraphBLAS (Shishin)


2. **Single Source Parent BFS**:
    - Implementation using Gunrock (Elkin)
    - Implementation using Spark (Pavlushkin)
    - Implementation using GraphBLAS (Shishin)


3. **Multi Source Parent BFS**:
    - Implementation using Gunrock (Elkin)
    - Implementation using Spark (Pavlushkin)
    - Implementation using GraphBLAS (Shishin)

## How To Run

### Clone the repository

```bash
git clone https://github.com/tepa46/graphs_analysis.git
```

### Prepare datasets 

In the `/datasets` directory, you can find one of the prepared graphs: *Email-Enron*.

The format is as follows:
```
node_from_0\tnode_to_0  
node_from_1\tnode_to_1  
...  
node_from_n\tnode_to_n  
```

You can add your own graphs for benchmarking or use datasets from the [Stanford Large Network Dataset Collection](https://snap.stanford.edu/data/index.html).

### Run benchmarks on datasets

[See benchmarks launch instructions](https://github.com/tepa46/graphs_analysis/blob/main/docker/README.md)

