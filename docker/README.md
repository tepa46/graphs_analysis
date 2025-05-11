# TODO

## Generate sources

```bash
source .venv/bin/activate
python3 -m src.sources_generator 
```

## Build image and run container 

```bash 
docker build -t test-app -f ./docker/MSBFS/GraphBLAS/Dockerfile .
docker run -it test-app       
```

## Remove all containers and images

```bash
docker rm -f $(docker ps -aq)  
docker rmi -f $(docker images -q)  
```
