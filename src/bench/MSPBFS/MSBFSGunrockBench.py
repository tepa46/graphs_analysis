from src.algo.MSBFS.Gunrock.GunrockMSBFS import GunrockMSBFS
from src.bench.MSPBFS.MSBFSBench import MSBFSBench

if __name__ == "__main__":
    algo = GunrockMSBFS()
    MSBFSBench().run_bench(algo)
