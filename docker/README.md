# Run benchmarks on datasets

## Generate sources

First, generate source nodes for the BFS algorithms:


```bash
source .venv/bin/activate
python3 -m src.sources_generator 
```

## Build image and run container 

Now you can run every algorithm-library combination on its own using:

```bash 
docker build -t graph-analysis-app -f ./docker/{algorithm_name}/{library_name}/Dockerfile .
docker run graph-analysis-app       
```

## Output

### PageRank Output Format
```
graph_name1: mean_ms std_ms
graph_name2: mean_ms std_ms  
... 
```

### Single Source Parent BFS Output Format 
```
graph_name1 source_node1: mean_ms std_ms
graph_name2 source_node2: mean_ms std_ms  
... 
```

### Multi Source Parent BFS Output Format 
```
graph_name1 source_nodes_count_1: mean_ms std_ms
graph_name1 source_nodes_count_2: mean_ms std_ms
...
graph_name2 source_nodes_count_1: mean_ms std_ms
graph_name2 source_nodes_count_2: mean_ms std_ms
... 
```