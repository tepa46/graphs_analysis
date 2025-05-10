from src.algo.SSBFS.GBSSBFS import GBSSBFS
from src.bench.SSPBFS.SSPBFSBench import SSBFSBench

if __name__ == "__main__":
    algo = GBSSBFS()
    SSBFSBench().run_bench(algo)
