from bench.PageRank.PageRankBench import PageRankBench
from pageRank.GraphBLAS.GBPRAlgo import GBPRAlgo

if __name__ == "__main__":
    algo = GBPRAlgo()
    PageRankBench().run_bench(algo)
