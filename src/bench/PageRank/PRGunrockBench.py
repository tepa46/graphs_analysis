from src.algo.Pagerank.GunrockPR import GunrockPR
from src.bench.PageRank.PageRankBench import PageRankBench

if __name__ == "__main__":
    algo = GunrockPR()
    PageRankBench().run_bench(algo)