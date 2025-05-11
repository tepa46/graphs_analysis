from src.algo.Pagerank.SparkPR import SparkPG
from src.bench.PageRank.PageRankBench import PageRankBench

if __name__ == "__main__":
    with SparkPG() as algo:
        PageRankBench().run_bench(algo)
