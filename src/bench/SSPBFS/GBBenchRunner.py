from src.bench.SSPBFS.SSPBFSBench import SSBFSBench
from parent_bfs.GraphBLAS.SingleSourceParentBFSAlgo import SingleSourceParentBFSAlgo

if __name__ == "__main__":
    algo = SingleSourceParentBFSAlgo()
    SSBFSBench().run_bench(algo)
