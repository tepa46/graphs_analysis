from src.algo.Pagerank.GBPR import GBPR
from src.bench.PageRank.PageRankBench import PageRankBench

if __name__ == "__main__":
    algo = GBPR()
    PageRankBench().run_bench(algo)
