from src.algo.MSBFS.GBMSBFS import GBMSBFS
from src.bench.MSPBFS.MSBFSBench import MSBFSBench

if __name__ == "__main__":
    algo = GBMSBFS()
    MSBFSBench().run_bench(algo)
