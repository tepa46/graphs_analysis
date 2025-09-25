from src.algo.MSBFS.PysparkMSBFS import SparkMSBFS
from src.bench.MSPBFS.MSBFSBench import MSBFSBench

if __name__ == "__main__":
    with SparkMSBFS() as algo:
        MSBFSBench().run_bench(algo)
