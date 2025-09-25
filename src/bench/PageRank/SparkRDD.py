from src.algo.Pagerank.PysparkRDD import SparkRDD
from src.bench.PageRank.PageRankBench import PageRankBench

if __name__ == "__main__":
    with SparkRDD() as algo:
        PageRankBench().run_bench(algo)
