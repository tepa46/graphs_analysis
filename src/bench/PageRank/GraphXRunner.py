from src.algo.Pagerank.GraphX import SparkGraphXPG
from src.bench.PageRank.PageRankBench import PageRankBench

if __name__ == "__main__":
    with SparkGraphXPG() as algo:
        PageRankBench().run_bench(algo)
