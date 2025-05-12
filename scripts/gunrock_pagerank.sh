#!/bin/bash
#A reminder of the need to use --gpus all flag
docker build -t gunrock-test -f pageRank\Gunrock\Dockerfile .
docker run --rm --gpus all gunrock-test