from src.bench.SSPBFS.SSPBFSBench import SSBFSBench
from src.algo.SSBFS.Gunrock.GunrockSSBFS import GunrockSSBFS

if __name__ == "__main__":
    algo = GunrockSSBFS()
    SSBFSBench().run_bench(algo)
