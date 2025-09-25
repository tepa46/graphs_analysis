from src.algo.Pagerank.PysparkGraphFrame import SparkGraphFrame
from src.bench.PageRank.PageRankBench import PageRankBench

if __name__ == "__main__":
    with SparkGraphFrame() as algo:
        PageRankBench().run_bench(algo)
