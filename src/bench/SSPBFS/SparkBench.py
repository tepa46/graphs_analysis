from src.algo.SSBFS.PysparkSSBFS import SparkSSBFS
from src.bench.SSPBFS.SSPBFSBench import SSBFSBench

if __name__ == "__main__":
    with SparkSSBFS() as algo:
        SSBFSBench().run_bench(algo)
