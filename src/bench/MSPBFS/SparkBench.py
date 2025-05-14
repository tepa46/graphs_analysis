from src.algo.MSBFS.PysparkMSBFS import SparkMSBFS
from src.bench.SSPBFS.SSPBFSBench import SSBFSBench

if __name__ == "__main__":
    with SparkMSBFS() as algo:
        SSBFSBench().run_bench(algo)
